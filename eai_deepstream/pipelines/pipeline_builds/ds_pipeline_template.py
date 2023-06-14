from imports import (
    Path, sys, logger,
    BaseModel, OmegaConf, DictConfig,
    Gst, pyds, GstRtspServer
)


from ds_utils.is_aarch_64 import is_aarch64

CUDA_MEM_ELEMENTS = ["nvstreammux","nvvideoconvert","nvmultistreamtiler"]


class DsPipeline:
    def __init__(self,):
        self.pipeline_name:str
        self.pipeline_description:str
        self.pipeline_props_file:str
        self.pipeline_props = self.__load_pipeline_props()
        self.pipeline:Gst.Pipeline = self.__create_pipeline()
        self.link_sequence:list = []

    def __load_pipeline_props(self):
        self.pipeline_props_file = Path(self.pipeline_props_file)
        if not self.pipeline_props_file.exists():
            self.pipeline_props_file = \
            Path(__file__).parent.parent/f"pipeline_props/{self.pipeline_props_file.name}"
        assert Path(self.pipeline_props_file).is_file(), \
              f"Pipeline props file {self.pipeline_props_file} is not valid file!"
        return OmegaConf.load(self.pipeline_props_file)
    
    def __create_pipeline(self):
        Gst.init(None)
        logger.info(f"Creating Pipeline {self.pipeline_name} \n ")
        pipeline = Gst.Pipeline()
        if not pipeline:
            sys.stderr.write(f"Unable to create Pipeline {self.pipeline_name}\n")
        return pipeline
    
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
        if isinstance(properties, DictConfig):
            properties = OmegaConf.to_container(properties, resolve=True)
        for key, value in properties.items():
            element.set_property(key, value)
        if factory_name in CUDA_MEM_ELEMENTS:
            element = DsPipeline.set_memory_types(element=element)
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
    def link_elements(self,link_sequence):
        for i in range(len(link_sequence)-1):
            link_sequence[i].link(link_sequence[i+1])

    def build_plugin_list(self, plugin_list:list, properties:OmegaConf):
        link_sequence = []
        for plugin in plugin_list:
            element = self.make_gst_element(
                plugin,
                properties=properties[plugin[1]],
            )
            self.pipeline.add(element)
            link_sequence.append(element)
        self.link_elements(link_sequence=link_sequence)
        return link_sequence
        

    def create_rtsp_server(self, properties:OmegaConf):
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
