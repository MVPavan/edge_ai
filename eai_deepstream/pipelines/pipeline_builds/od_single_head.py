from imports import (
    OmegaConf, DictConfig, BaseModel
)

from .ds_pipeline_base import (
    DsPipelineBase, DsPipelineCreate,
    infer_configs_folder
)

from pipelines.building_blocks.deepstream_plugins import DsPlugins
from pipelines.building_blocks.pipeline_blocks import PipelineBlocks


class ODSingleHeadCreate(DsPipelineCreate):
    pipeline_name = "od_single_head"
    pipeline_description = "Object Detection Single Head Pipeline"
    pipeline_props_file = "od_single_head.yaml"


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

    def __init__(self, ods_pipeline_create:DsPipelineCreate = ODSingleHeadCreate()):
        super().__init__(ods_pipeline_create)


    def build_pipeline(self,):
        pipeline_blocks = PipelineBlocks()
        multi_uri_src = DsPlugins.multi_uri_src("multi_uri_src")
        pgie = DsPlugins.triton_server("pgie")
        tee_pgie = DsPlugins.tee("tee_pgie")
        self.pipeline_props.pgie["config-file-path"] = self.check_file_path(
            file_path=self.pipeline_props.pgie["config-file-path"],
            load_folder=infer_configs_folder
        )
        infer_head_elements = [multi_uri_src, pgie, tee_pgie]
        infer_head_link_seq = self.build_pipeline_from_list(
                plugin_list=infer_head_elements,
                properties=self.pipeline_props
        )

        if self.pipeline_props.plugins.custom_parser:
            self.add_parser_probe(infer_head_link_seq, plugin_name="pgie")

        elif self.pipeline_props.plugins.fps:
            self.add_fps_probe(infer_head_link_seq, plugin_name="pgie")


        if self.pipeline_props.plugins.fakesink:
            link_sequence_fake = self.build_pipeline_from_list(
                plugin_list=pipeline_blocks.fake_sink_tail.pipeline_elements,
                properties=self.pipeline_props
            )
            self.join_link_sequences(infer_head_link_seq, link_sequence_fake)
            return self.pipeline
        
        if self.pipeline_props.plugins.filesink or self.pipeline_props.plugins.rtsp:
            link_sequence_osd = self.build_pipeline_from_list(
                plugin_list=pipeline_blocks.osd_pipeline.pipeline_elements,
                properties=self.pipeline_props
            )
            self.join_link_sequences(infer_head_link_seq, link_sequence_osd)
        
            if self.pipeline_props.plugins.filesink:
                link_sequence_file = self.build_pipeline_from_list(
                    plugin_list=pipeline_blocks.file_sink_tail.pipeline_elements,
                    properties=self.pipeline_props
                )
                self.join_link_sequences(link_sequence_osd, link_sequence_file)
            
            if self.pipeline_props.plugins.rtsp:
                link_sequence_rtsp = self.build_pipeline_from_list(
                    plugin_list=pipeline_blocks.rtsp_sink_tail.pipeline_elements,
                    properties=self.pipeline_props
                )
                self.join_link_sequences(link_sequence_osd, link_sequence_rtsp)
                self.create_rtsp_server(properties=self.pipeline_props.rtsp)
        
        return self.pipeline




