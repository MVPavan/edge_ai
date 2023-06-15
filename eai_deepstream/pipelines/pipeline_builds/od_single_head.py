from imports import (
    OmegaConf
)

from .ds_pipeline_base import DsPipelineBase

from pipelines.building_blocks.deepstream_plugins import DsPlugins
from pipelines.building_blocks.pipeline_blocks import PipelineBlocks

class ODSingleHead(DsPipelineBase):
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
        pgie = DsPlugins.triton_server("pgie")
        tee_pgie = DsPlugins.tee("tee_pgie")
        infer_head_elements = [multi_uri_src, pgie, tee_pgie]
        infer_head_link_seq = self.build_pipeline_from_list(
                plugin_list=infer_head_elements,
                properties=self.pipeline_props
        )
                
        if self.pipeline_props.plugins.fakesink:
            link_sequence_fake = self.build_pipeline_from_list(
                plugin_list=PipelineBlocks.fake_sink_tail.pipeline_elements,
                properties=self.pipeline_props
            )
            self.join_link_sequences(infer_head_link_seq, link_sequence_fake)
            return self.pipeline
        
        if self.pipeline_props.plugins.filesink or self.pipeline_props.plugins.rtsp:
            link_sequence_osd = self.build_pipeline_from_list(
                plugin_list=PipelineBlocks.osd_pipeline.pipeline_elements,
                properties=self.pipeline_props
            )
            self.join_link_sequences(infer_head_link_seq, link_sequence_osd)
        
        if self.pipeline_props.plugins.filesink:
            link_sequence_file = self.build_pipeline_from_list(
                plugin_list=PipelineBlocks.file_sink_tail.pipeline_elements,
                properties=self.pipeline_props
            )
            self.join_link_sequences(link_sequence_osd, link_sequence_file)
        
        if self.pipeline_props.plugins.rtsp:
            link_sequence_rtsp = self.build_pipeline_from_list(
                plugin_list=PipelineBlocks.rtsp_sink_tail.pipeline_elements,
                properties=self.pipeline_props
            )
            self.join_link_sequences(link_sequence_osd, link_sequence_rtsp)
            self.create_rtsp_server(properties=self.pipeline_props)
        return self.pipeline




