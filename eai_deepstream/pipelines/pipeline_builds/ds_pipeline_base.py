from imports import (
    Path, sys, logger, Callable, Optional,
    BaseModel, OmegaConf, DictConfig, Field,
    Gst, pyds, GstRtspServer
)


from ds_utils.is_aarch_64 import is_aarch64
from ds_configs import (
    pipline_props_folder, plugin_props_folder, infer_configs_folder, COCO_LABELS_FILE
)
from pipelines.probes.probe_funcs import (
    tensor_to_object_probe, read_obj_meta_probe, overlay_probe
)
from utils.ds_vars import DsResultVars, PERF_DATA
from utils.other_utils import get_label_names_from_file

class DsPipelineCreate(BaseModel):
    pipeline_name:str
    pipeline_description:str
    pipeline_props_file:Optional[str] = None
    pipeline_props:Optional[DictConfig] = None
    parser_function:Optional[Callable] = None


class DsPipelineBase:

    CUDA_MEM_ELEMENTS = ["nvstreammux","nvvideoconvert","nvmultistreamtiler"]
    CAPS_GENERATOR = {
        "CAPS_NVMM_RGBA": lambda : Gst.Caps.from_string("video/x-raw(memory:NVMM), format=RGBA"),
        "CAPS_NVMM_I420" : lambda : Gst.Caps.from_string("video/x-raw(memory:NVMM), format=I420"),
        "CAPS_I420" : lambda : Gst.Caps.from_string("video/x-raw, format=I420"),
    }

    def __init__(self, ds_pipeline_create:DsPipelineCreate):
        self.pipeline_name = ds_pipeline_create.pipeline_name
        self.pipeline_description = ds_pipeline_create.pipeline_description
        self.pipeline:Gst.Pipeline = self.__create_pipeline()
        
        
        if ds_pipeline_create.pipeline_props is None:
            self.pipeline_props:DictConfig = self.__load_pipeline_props(
                ds_pipeline_create.pipeline_props_file
            )
        else:
            self.pipeline_props:DictConfig = ds_pipeline_create.pipeline_props
        
        self.result_vars:DsResultVars = DsResultVars()
        self.result_vars.perf_data = PERF_DATA(delta_time=3000, exact_aggregate_fps=False)
        self.__load_labels_file()

    def __load_pipeline_props(self, pipeline_props_file) -> DictConfig:        
        assert pipeline_props_file is not None, "Pipeline props file not provided!"
        pipeline_props_file = Path(pipeline_props_file)

        if not pipeline_props_file.is_file():
            pipeline_props_file = pipline_props_folder/pipeline_props_file.name
        assert Path(pipeline_props_file).is_file(), \
              f"Pipeline props file {pipeline_props_file} is not valid file!"

        return OmegaConf.load(pipeline_props_file) # type: ignore

    def __create_pipeline(self):
        Gst.init(None)
        logger.info(f"Creating Pipeline {self.pipeline_name} \n ")
        pipeline = Gst.Pipeline()
        if not pipeline:
            sys.stderr.write(f"Unable to create Pipeline {self.pipeline_name}\n")
        return pipeline
    
    def __load_labels_file(self):
        labels_file = None
        if self.pipeline_props.plugins.custom_parser or \
            self.pipeline_props.plugins.fps:
            labels_file = self.pipeline_props.custom_parser_labels.labels_file
        if labels_file is None:
            labels_file = COCO_LABELS_FILE

        self.result_vars.label_names = get_label_names_from_file(labels_file) # type: ignore


    def build_pipeline_from_list(self, plugin_list:list, properties:DictConfig) -> list:
        link_sequence = []
        for plugin in plugin_list:
            elem_props = {}
            if plugin[1] in properties:
                elem_props = properties[plugin[1]]                

            element = self.make_gst_element(
                plugin, properties=elem_props,
            )
            self.pipeline.add(element)
            link_sequence.append(element)
        self.link_elements_within_seq(link_sequence=link_sequence)
        return link_sequence
    
    def add_fps_probe(self, element, plugin_name:str=""):

        if isinstance(element, list):
            element = self.get_named_plugin_from_list(element, plugin_name)
            assert element is not None, f"No plugin with name: {plugin_name}"

        element.get_static_pad("src").add_probe(
            Gst.PadProbeType.BUFFER, read_obj_meta_probe, self.result_vars
        )

    def add_parser_probe(self, element, plugin_name:str=""):

        if isinstance(element, list):
            element = self.get_named_plugin_from_list(element, plugin_name)
            assert element is not None, f"No plugin with name: {plugin_name}"


        assert self.result_vars.parser_func is not None, "Parser function not set"
        element.get_static_pad("src").add_probe(
            Gst.PadProbeType.BUFFER, tensor_to_object_probe, self.result_vars
        )

    @staticmethod
    def make_gst_element(plugin_names,properties:dict={}):
        """ Creates an element with Gst Element Factory make.
            Return the element  if successfully created, otherwise print
            to stderr and return None.
        """
        factory_name = plugin_names[0]
        user_name = plugin_names[1]
        element = Gst.ElementFactory.make(factory_name, user_name)
        if not element:
            sys.stderr.write("Unable to create " + user_name + " \n")

        logger.info(f"Created Element :{element.get_name()}")
        if properties:
            if isinstance(properties, DictConfig):
                properties = OmegaConf.to_container(properties, resolve=True) # type: ignore
            
            for key, value in properties.items():
                if "caps" in key: 
                    value = DsPipelineBase.CAPS_GENERATOR[value]()
                element.set_property(key, value)

        if factory_name in DsPipelineBase.CUDA_MEM_ELEMENTS:
            element = DsPipelineBase.set_memory_types(element=element)
        return element

    @staticmethod
    def check_file_path(file_path, load_folder:Path=Path("")):
        if Path(file_path).is_file():
            return file_path
        
        file_path = load_folder/file_path
        if not Path(file_path).is_file():
            raise FileNotFoundError(f"File {file_path} not found")
        return file_path.as_posix()

    @staticmethod
    def set_memory_types(element):
        if not is_aarch64():
            # Use CUDA unified memory in the pipeline so frames
            # can be easily accessed on CPU in Python.
            mem_type = int(pyds.NVBUF_MEM_CUDA_UNIFIED)
            element.set_property("nvbuf-memory-type", mem_type)
        return element
    
    @staticmethod
    def get_plugin_name(plugin:Gst.Plugin):
        return plugin.get_name()

    @staticmethod
    def get_named_plugin_from_list(plugin_list:list, plugin_name:str):
        assert plugin_name is not "", "Plugin name substring cannot be empty"
        for plugin in plugin_list:
            if plugin_name == DsPipelineBase.get_plugin_name(plugin):
                return plugin
        return None

    @staticmethod
    def link_elements_within_seq(link_sequence):
        for i in range(len(link_sequence)-1):
            link_sequence[i].link(link_sequence[i+1])

    @staticmethod
    def join_link_sequences(link_seq_head, link_seq_tail):
        if DsPipelineBase.check_tail_tee_head_queue(link_seq_head, link_seq_tail):
            DsPipelineBase.link_tee_queue(link_seq_head[-1],link_seq_tail[0])
        else:
            link_seq_head[-1].link(link_seq_tail[0])
    
    @staticmethod
    def check_tail_tee_head_queue(link_seq_head, link_seq_tail):
        """
        Checks if the tail element of the head sequence is a tee element
        and the head element of the tail sequence is a queue element.
        """
        if ("tee" in link_seq_head[-1].get_name()) and \
            ("queue" in link_seq_tail[0].get_name()):
            return True
        return False

    @staticmethod
    def link_tee_queue(tee_plugin,queue_plugin):
        assert "tee" in tee_plugin.get_name(), "tee_plugin must be a tee element"
        assert "queue" in queue_plugin.get_name(), "queue_plugin must be a queue element"
        tee_src_pad = tee_plugin.get_request_pad('src_%u')
        queue_sink_pad = queue_plugin.get_static_pad('sink')
        tee_src_pad.link(queue_sink_pad)

    @staticmethod
    def create_rtsp_server(properties:DictConfig):
            # Start streaming
        server = GstRtspServer.RTSPServer.new()
        server.props.service = "%d" % properties.RTSP_PORT
        server.attach(None)

        factory = GstRtspServer.RTSPMediaFactory.new()
        factory.set_launch(
            '( udpsrc name=pay0 port=%d buffer-size=524288 caps="application/x-rtp, media=video, clock-rate=90000, encoding-name=(string)%s, payload=96 " )'
            % (properties.UDPSINK_PORT, properties.RTSP_CODEC)
        )
        factory.set_shared(True)
        server.get_mount_points().add_factory(properties.RTSP_STREAM_NAME, factory)

        logger.info(f"\n ***DeepStream: Launched RTSP Streaming at:\
            rtsp://localhost:{properties.RTSP_PORT}{properties.RTSP_STREAM_NAME} ***\n\n")
            