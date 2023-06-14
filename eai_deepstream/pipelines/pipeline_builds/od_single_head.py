from imports import (
    OmegaConf
)

from .ds_pipeline_template import DsPipeline

from pipelines.building_blocks.deepstream_plugins import DsPlugins
from pipelines.building_blocks.pipeline_blocks import PipelineBlocks

class ODSingleHead(DsPipeline):
    """
    Object Detection Single Head Pipeline
    Consists of:
        - Object Detection Single Head
        - Tracker (Optional)
        - Secondary GIE (Optional)
        
        - Tiled Display (Optional)
        - On Screen Display (Optional)
        - Fake Sink / File Sink / RTSP Sink (Optional)
        - Kafka Output (Optional)
    """

    def __init__(self, pipeline_props:OmegaConf = None):
        self.pipeline_name:str = "od_single_head"
        self.pipeline_description:str = "Object Detection Single Head Pipeline"
        self.pipeline_props_file:str = "od_single_head.yaml"
        super().__init__()
        if pipeline_props is not None:
            self.pipeline_props = pipeline_props


    def build_pipeline(self,):
        multi_uri_src = DsPlugins.multi_uri_src("multi_uri_src")
        multi_uri_src_plugin = self.make_gst_element(
            multi_uri_src, properties=self.pipeline_props.multi_uri_src
        )
        pgie = DsPlugins.triton_server("pgie")
        pgie_plugin = self.make_gst_element(
            pgie, properties=self.pipeline_props.pgie
        )
        
        link_sequence = self.build_plugin_list()


