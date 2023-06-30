from dataclasses import dataclass

@dataclass(frozen=True)
class DsPlugins:
    # Input plugins
    multi_uri_src = lambda _name: ("nvmultiurisrcbin", f"{_name}")

    # Streammux plugins
    stream_muxer = lambda _name: ("nvstreammux", f"{_name}")

    # Inference plugins
    triton_server = lambda _name: ("nvinferserver", f"{_name}")

    # Tee plugins
    tee = lambda _name: ("tee", f"{_name}") 

    # Queue plugins
    queue = lambda _name: ("queue", f"{_name}")
    
    # Filter plugins
    caps_filter = lambda _name: ("capsfilter", f"{_name}")

    # Video plugins
    mpeg4_encoder = lambda _name: ("avenc_mpeg4", f"{_name}")
    MPEG4_ENCODER_BITRATE:int = 2000000
    mpeg4_parser = lambda _name: ("mpeg4videoparse", f"{_name}")
    nvvideo_convert = lambda _name: ("nvvideoconvert", f"{_name}")
    qtmux = lambda _name: ("qtmux", f"{_name}")
        
    # OSD plugins
    nvosd = lambda _name: ("nvdsosd", f"{_name}")

    # Output plugins
    nvtiler = lambda _name: ("nvmultistreamtiler", f"{_name}")
    encoder_h264 = lambda _name: ("nvv4l2h264enc", f"{_name}")
    encoder_h265 = lambda _name: ("nvv4l2h265enc", f"{_name}")
    rtppay_h264 = lambda _name: ("rtph264pay", f"{_name}")
    rtppay_h265 = lambda _name: ("rtph265pay", f"{_name}")
    
    # Sink plugins
    filesink = lambda _name: ("filesink", f"{_name}")
    udpsink = lambda _name: ("udpsink", f"{_name}")
    fakesink = lambda _name: ("fakesink", f"{_name}")

    # Message broker plugins
    nvmsgconv = lambda _name: ("nvmsgconv", f"{_name}")
    nvmsgbroker = lambda _name: ("nvmsgbroker", f"{_name}")
    

