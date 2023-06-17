from imports import (
    Path, sys, logger,
    BaseModel, OmegaConf, DictConfig,
    Gst, pyds, GstRtspServer
)


from ds_utils.is_aarch_64 import is_aarch64


class DsPipelineCreate(BaseModel):
    pipeline_name:str
    pipeline_description:str
    pipeline_props_file:str = None
    pipeline_props:DictConfig = None

class DsPipelineBase:
    CAPS_NVMM_RGBA = lambda : Gst.Caps.from_string("video/x-raw(memory:NVMM), format=RGBA")
    # CAPS_NVMM_I420 = Gst.Caps.from_string("video/x-raw(memory:NVMM), format=I420")
    # CAPS_I420 = Gst.Caps.from_string("video/x-raw, format=I420")
    CUDA_MEM_ELEMENTS = ["nvstreammux","nvvideoconvert","nvmultistreamtiler"]

    def __init__(self, ds_pipeline_create:DsPipelineCreate):
        self.pipeline_name = ds_pipeline_create.pipeline_name
        self.pipeline_description = ds_pipeline_create.pipeline_description
        self.pipeline_props_file = ds_pipeline_create.pipeline_props_file
        self.pipeline_props:DictConfig = ds_pipeline_create.pipeline_props
        self.pipeline:Gst.Pipeline = self.__create_pipeline()
        self.link_sequence:list = []
        self.__load_pipeline_props()


    def __load_pipeline_props(self):
        if self.pipeline_props is not None: return
        
        assert self.pipeline_props_file is not None
        self.pipeline_props_file = Path(self.pipeline_props_file)

        if not self.pipeline_props_file.exists():
            self.pipeline_props_file = \
            Path(__file__).parent.parent/f"pipeline_props/{self.pipeline_props_file.name}"
        assert Path(self.pipeline_props_file).is_file(), \
              f"Pipeline props file {self.pipeline_props_file} is not valid file!"

        self.pipeline_props = OmegaConf.load(self.pipeline_props_file)


    def __create_pipeline(self):
        Gst.init(None)
        logger.info(f"Creating Pipeline {self.pipeline_name} \n ")
        pipeline = Gst.Pipeline()
        if not pipeline:
            sys.stderr.write(f"Unable to create Pipeline {self.pipeline_name}\n")
        return pipeline
    

    def build_pipeline_from_list(self, plugin_list:list, properties:DictConfig) -> list:
        link_sequence = []
        for plugin in plugin_list:
            if plugin[1] in properties:
                elem_props = properties[plugin[1]]
            else:
                elem_props = {}

            element = self.make_gst_element(
                plugin, properties=elem_props,
            )
            self.pipeline.add(element)
            link_sequence.append(element)
        self.link_elements_within_seq(link_sequence=link_sequence)
        return link_sequence

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
                properties = OmegaConf.to_container(properties, resolve=True)
            for key, value in properties.items():
                element.set_property(key, value)
        if factory_name in DsPipelineBase.CUDA_MEM_ELEMENTS:
            element = DsPipelineBase.set_memory_types(element=element)
        return element

    @staticmethod
    def set_memory_types(element):
        if not is_aarch64():
            # Use CUDA unified memory in the pipeline so frames
            # can be easily accessed on CPU in Python.
            mem_type = int(pyds.NVBUF_MEM_CUDA_UNIFIED)
            element.set_property("nvbuf-memory-type", mem_type)
        return element
    
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

