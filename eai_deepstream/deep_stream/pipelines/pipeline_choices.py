from dataclasses import dataclass
from pathlib import Path

output_folder = (Path(__name__).parent)/"output"
output_folder.mkdir(exist_ok=True, parents=True)

@dataclass
class MultiStreamPipeline:
    # [ stream_muxer -> triton_server] (MSP)
    stream_muxer = ("nvstreammux", "stream-muxer")
    triton_server = ("nvinferserver", "primary-inference")


@dataclass
class FileSinkPipeline: 
    #  [mpeg4_encoder -> mpeg4_parser -> qtmux -> sink] (Filesink/FS)
    mpeg4_encoder = ("avenc_mpeg4", "mpeg4_encoder")
    mpeg4_parser = ("mpeg4videoparse", "mpeg4_parser")
    qtmux = ("qtmux", "qtmux")
    filesink = ("filesink", "filesink")
    MPEG4_ENCODER_BITRATE = 2000000

@dataclass
class OSDPipeline:
    # [ nvvidconv -> capsfilter -> nvosd -> nvvidconv2 -> queue] (OSD)
    nvvidconv_pre = ("nvvideoconvert", "nvvidconv_pre")
    capsfilter_pre = ("capsfilter", "capsfilter_pre")
    # Create OSD to draw on the converted RGBA buffer
    nvosd = ("nvdsosd", "onscreendisplay")
    # Finally encode and save the osd output
    queue = ("queue", "queue")
    nvvidconv_post = ("nvvideoconvert", "nvvidconv_post")


@dataclass
class TilerPipeline(OSDPipeline):
    # [ nvvidconv -> capsfilter -> nvtiler -> nvosd -> nvvidconv2 -> queue -> Filesink] (Tiler)
    nvtiler = ("nvmultistreamtiler", "nvtiler")
    TILED_OUTPUT_WIDTH = 1920
    TILED_OUTPUT_HEIGHT = 1080


@dataclass
class RTSPSink:
    # [ nvv4l2h264enc -> rtph264pay -> udpsink] (RTSP)
    encoder_h264 = ("nvv4l2h264enc", "rtsp_encoder")
    encoder_h265 = ("nvv4l2h265enc", "rtsp_encoder")
    rtppay_h264 = ("rtph264pay", "rtppay")
    rtppay_h265 = ("rtph265pay", "rtppay")
    udpsink = ("udpsink", "udpsink")
    RTSP_CODEC = "H264"
    UDPSINK_PORT = 5400
    UDPSINK_HOST = "224.224.255.255"
    RTSP_ENCODER_BITRATE = 4000000
    RTSP_PORT = 8554
    RTSP_STREAM_NAME = "/illustrai"


@dataclass
class MSPFake(MultiStreamPipeline):
    """
    Multi Stream Pipeline with face sink
    """
    # [ MSP -> Fakesink]
    fakesink = ("fakesink", "fakesink")

@dataclass
class MSPOsd(MultiStreamPipeline, OSDPipeline, FileSinkPipeline):
    """
    Multi Stream Pipeline with osd sink
    """
    # [ MSP -> OSD -> FS]

@dataclass
class MSPTiler(MultiStreamPipeline, TilerPipeline, FileSinkPipeline):
    """
    Multi Stream Pipeline with tiler and osd sink
    """
    # [ MSP -> Tiler -> FS]

@dataclass
class MSPTilerRTSP(MultiStreamPipeline, TilerPipeline, RTSPSink):
    """
    Multi Stream Pipeline with tiler and osd sink
    """
    # [ MSP -> Tiler -> RTSP]

