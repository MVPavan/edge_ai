from imports import (
    OmegaConf, DictConfig, BaseModel
)

from .ds_pipeline_base import (
    DsPipelineBase, DsPipelineProps,
    infer_configs_folder
)

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
    If props not provided loads default props based on pipeline choice
    """

    def __init__(self, ds_pipeline_props:DsPipelineProps):
        # Initialize the Object Detection Single Head pipeline
        super().__init__(ds_pipeline_props)

    # Define the pipeline building function
    def build_pipeline(self,):
        # Create an instance of the PipelineBlocks class
        pipeline_blocks = PipelineBlocks()
        # Create a multi-uri source element
        multi_uri_src = DsPlugins.multi_uri_src("multi_uri_src")
        # Create a primary GIE element using Triton server
        pgie = DsPlugins.triton_server("pgie")
        # Create a tee element for the primary GIE
        tee_pgie = DsPlugins.tee("tee_pgie")
        # Check the file path for the primary GIE configuration file
        self.pipeline_props.pgie["config-file-path"] = self.check_file_path(
            file_path=self.pipeline_props.pgie["config-file-path"],
            load_folder=infer_configs_folder
        )
        # Create the sequence of elements for the inference head
        infer_head_elements = [multi_uri_src, pgie, tee_pgie]
        # Build the inference head pipeline from the list of elements
        infer_head_link_seq = self.build_pipeline_from_list(
                plugin_list=infer_head_elements,
                properties=self.pipeline_props
        )

        # Add a parser probe if specified in the pipeline properties
        if self.pipeline_props.plugins.custom_parser:
            self.add_parser_probe(infer_head_link_seq, plugin_name="pgie")
        # Add an FPS probe if specified in the pipeline properties
        elif self.pipeline_props.plugins.fps:
            self.add_fps_probe(infer_head_link_seq, plugin_name="pgie")

        # Build the fake sink pipeline from the PipelineBlocks class
        if self.pipeline_props.plugins.fakesink:
            link_sequence_fake = self.build_pipeline_from_list(
                plugin_list=pipeline_blocks.fake_sink_tail.pipeline_elements,
                properties=self.pipeline_props
            )
            # Join the inference head pipeline with the fake sink pipeline
            self.join_link_sequences(infer_head_link_seq, link_sequence_fake)
            # Return the complete pipeline
            return self.pipeline

        # Build the OSD pipeline from the PipelineBlocks class
        if self.pipeline_props.plugins.filesink or self.pipeline_props.plugins.rtsp:
            link_sequence_osd = self.build_pipeline_from_list(
                plugin_list=pipeline_blocks.osd_pipeline.pipeline_elements,
                properties=self.pipeline_props
            )
            # Join the inference head pipeline with the OSD pipeline
            self.join_link_sequences(infer_head_link_seq, link_sequence_osd)
            # Build the file sink pipeline from the PipelineBlocks class
            if self.pipeline_props.plugins.filesink:
                link_sequence_file = self.build_pipeline_from_list(
                    plugin_list=pipeline_blocks.file_sink_tail.pipeline_elements,
                    properties=self.pipeline_props
                )
                # Join the OSD pipeline with the file sink pipeline
                self.join_link_sequences(link_sequence_osd, link_sequence_file)

            # Build the RTSP sink pipeline from the PipelineBlocks class
            if self.pipeline_props.plugins.rtsp:
                link_sequence_rtsp = self.build_pipeline_from_list(
                    plugin_list=pipeline_blocks.rtsp_sink_tail.pipeline_elements,
                    properties=self.pipeline_props
                )
                # Join the OSD pipeline with the RTSP sink pipeline
                self.join_link_sequences(link_sequence_osd, link_sequence_rtsp)
                # Create an RTSP server if specified in the pipeline properties
                self.create_rtsp_server(properties=self.pipeline_props.rtsp)
        
        if self.pipeline_props.plugins.kafka:
            # Build the Kafka output pipeline from the PipelineBlocks class
            link_sequence_kafka = self.build_pipeline_from_list(
                plugin_list=pipeline_blocks.kafka_tail.pipeline_elements,
                properties=self.pipeline_props
            )
            # Join the inference head pipeline with the Kafka output pipeline
            self.join_link_sequences(infer_head_link_seq, link_sequence_kafka)

        # Return the complete pipeline
        return self.pipeline