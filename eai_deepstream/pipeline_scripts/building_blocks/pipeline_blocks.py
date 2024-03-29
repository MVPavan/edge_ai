from pydantic import BaseModel
from .deepstream_plugins import DsPlugins


class FakeSinkTail(BaseModel):
    pipeline_elements: list = [
        DsPlugins.queue("queue_fakesink"),
        DsPlugins.fakesink("fake_sink")
    ]

class FileSinkTail(BaseModel):
    pipeline_elements: list = [
        DsPlugins.queue("queue_filesink"),
        DsPlugins.mpeg4_encoder("mpeg4_encoder_filesink"),
        DsPlugins.mpeg4_parser("mpeg4_parser_filesink"),
        DsPlugins.qtmux("qtmux_filesink"),
        DsPlugins.filesink("file_sink")
    ]

class RtspSinkTail(BaseModel):
    pipeline_elements: list = [
        DsPlugins.queue("queue_rtsp"),
        DsPlugins.encoder_h264("encoder_rtsp"),
        DsPlugins.rtppay_h264("rtppay_rtsp"),
        DsPlugins.udpsink("udp_sink")
    ]

class OsdPipeline(BaseModel):
    pipeline_elements: list = [
        DsPlugins.queue("queue_osd_pre"),
        DsPlugins.nvvideo_convert("nvvideo_convert_osd_pre"),
        DsPlugins.caps_filter("caps_filter_osd"),
        DsPlugins.nvtiler("nvtiler_osd"),
        DsPlugins.nvosd("nvosd"),
        DsPlugins.nvvideo_convert("nvvideo_convert_osd_post"),
        DsPlugins.queue("queue_osd_post"),
        DsPlugins.tee("tee_osd")
    ]

class KafkaTail(BaseModel):
    pipeline_elements: list = [
        DsPlugins.queue("queue_kafka"),
        DsPlugins.nvmsgconv("msgconv_kafka"),
        DsPlugins.nvmsgbroker("msgbroker_kafka")
    ]

class PipelineBlocks(BaseModel):
    osd_pipeline: OsdPipeline = OsdPipeline()
    rtsp_sink_tail: RtspSinkTail = RtspSinkTail()
    file_sink_tail: FileSinkTail = FileSinkTail()
    fake_sink_tail: FakeSinkTail = FakeSinkTail()
    kafka_tail: KafkaTail = KafkaTail()
    