import sys
from pathlib import Path
import math

import gi
gi.require_version("Gst", "1.0")
from gi.repository import GLib, Gst, GstRtspServer

from utils.ds_vars import DSVars, DsResultVars

from deep_stream.plugins.basic_plugins import (
    PipelineVars, make_gst_element
)
from deep_stream.probes.probe_funcs import overlay_probe
from deep_stream.ds_utils.is_aarch_64 import is_aarch64

from .pipeline_choices import MSPFake, MSPOsd, MSPTiler, MSPTilerRTSP, output_folder

import logging
ds_log = logging.getLogger()



def add_file_sink(ds_vars:DSVars, pipeline_vars:PipelineVars, result_vars:DsResultVars):
    pipeline_config = ds_vars.pipeline_config
    mpeg4_encoder = make_gst_element(
        *pipeline_config.mpeg4_encoder,pipeline_vars=pipeline_vars,
        properties={"bitrate":pipeline_config.MPEG4_ENCODER_BITRATE}
    )
    
    mpeg4_parser = make_gst_element(*pipeline_config.mpeg4_parser,pipeline_vars=pipeline_vars)
    
    qtmux = make_gst_element(*pipeline_config.qtmux,pipeline_vars=pipeline_vars)
    
    if result_vars.save_file is None:
        result_vars.out_file = output_folder/f"{Path(ds_vars.uri_list[0]).stem}.mp4"

    filesink = make_gst_element(
        *pipeline_config.filesink,pipeline_vars=pipeline_vars,
        properties={"location": result_vars.save_file, "sync": 1}
    )
    return pipeline_vars


def add_rtsp_sink(ds_vars:DSVars, pipeline_vars:PipelineVars, result_vars:DsResultVars):
    
    pipeline_config = ds_vars.pipeline_config
    
    # Make the encoder
    if pipeline_config.RTSP_CODEC == "H264":
        rtsp_encoder = make_gst_element(
            *pipeline_config.encoder_h264,pipeline_vars=pipeline_vars,
            properties={"bitrate": pipeline_config.RTSP_ENCODER_BITRATE}
        )
    elif pipeline_config.RTSP_CODEC == "H265":
        rtsp_encoder = make_gst_element(
            *pipeline_config.encoder_h265,pipeline_vars=pipeline_vars,
            properties={"bitrate": pipeline_config.RTSP_ENCODER_BITRATE}
        )
    else:
        sys.stderr.write(" Encoder Codec not valid")
    if is_aarch64():
        rtsp_encoder.set_property("preset-level", 1)
        rtsp_encoder.set_property("insert-sps-pps", 1)
        #rtsp_encoder.set_property("bufapi-version", 1)
    
    # Make the payload-encode video into RTP packets
    if pipeline_config.RTSP_CODEC == "H264":
        rtppay = make_gst_element(*pipeline_config.rtppay_h264,pipeline_vars=pipeline_vars)
    elif pipeline_config.RTSP_CODEC == "H265":
        rtppay = make_gst_element(*pipeline_config.rtppay_h265,pipeline_vars=pipeline_vars)
    else:
        sys.stderr.write(" Rtppay Codec not valid")

    # Make the UDP sink
    udpsink_props = {
        "host": pipeline_config.UDPSINK_HOST,
        "port": pipeline_config.UDPSINK_PORT, 
        "async": 0,
        "sync": 1,
    }
    udpsink = make_gst_element(
        *pipeline_config.udpsink,pipeline_vars=pipeline_vars,
        properties=udpsink_props
    )

    # Start streaming
    server = GstRtspServer.RTSPServer.new()
    server.props.service = "%d" % pipeline_config.RTSP_PORT
    server.attach(None)

    factory = GstRtspServer.RTSPMediaFactory.new()
    factory.set_launch(
        '( udpsrc name=pay0 port=%d buffer-size=524288 caps="application/x-rtp, media=video, clock-rate=90000, encoding-name=(string)%s, payload=96 " )'
        % (pipeline_config.UDPSINK_PORT, pipeline_config.RTSP_CODEC)
    )
    factory.set_shared(True)
    server.get_mount_points().add_factory(pipeline_config.RTSP_STREAM_NAME, factory)

    ds_log.info(f"\n ***DeepStream: Launched RTSP Streaming at:\
          rtsp://localhost:{pipeline_config.RTSP_PORT}{pipeline_config.RTSP_STREAM_NAME} ***\n\n")
    return pipeline_vars


def add_viz_pipeline(ds_vars:DSVars, pipeline_vars:PipelineVars, result_vars:DsResultVars):
    pipeline_config = ds_vars.pipeline_config
    
    if pipeline_config.__class__.__name__ == "MSPFake":
        fakesink=make_gst_element(
            *pipeline_config.fakesink, pipeline_vars=pipeline_vars,
            properties={"sync": 1}
        )

    elif pipeline_config.__class__.__name__ in ["MSPOsd", "MSPTiler", "MSPTilerRTSP"]:
        nvvidconv_pre = make_gst_element(*pipeline_config.nvvidconv_pre,pipeline_vars=pipeline_vars)
        
        caps = Gst.Caps.from_string("video/x-raw(memory:NVMM), format=RGBA")
        # caps = Gst.Caps.from_string("video/x-raw(memory:NVMM), format=I420")
        # caps = Gst.Caps.from_string("video/x-raw, format=I420")
        capsfilter_pre = make_gst_element(
            *pipeline_config.capsfilter_pre, pipeline_vars=pipeline_vars,
            properties={"caps": caps}
        )
        
        if pipeline_config.__class__.__name__ in ["MSPTiler","MSPTilerRTSP"]:
            number_sources = len(ds_vars.uri_list)
            tiler_rows = int(math.sqrt(number_sources))
            tiler_columns = int(math.ceil((1.0 * number_sources) / tiler_rows))
            tiler_props= {
                "rows": tiler_rows,
                "columns": tiler_columns,
                "width": pipeline_config.TILED_OUTPUT_WIDTH,
                "height": pipeline_config.TILED_OUTPUT_HEIGHT
            }
            nvtiler = make_gst_element(
                *pipeline_config.nvtiler, pipeline_vars=pipeline_vars,
                properties=tiler_props
            )
            tiler_sink_pad = nvtiler.get_static_pad("sink")
            if not tiler_sink_pad:
                sys.stderr.write(" Unable to get src pad \n")
            else:
                tiler_sink_pad.add_probe(Gst.PadProbeType.BUFFER, overlay_probe, result_vars)


        nvosd = make_gst_element(*pipeline_config.nvosd,pipeline_vars=pipeline_vars)
        osdsinkpad = nvosd.get_static_pad("sink")
        # if not osdsinkpad:
        #     sys.stderr.write(" Unable to get sink pad of nvosd \n")
        # osdsinkpad.add_probe(Gst.PadProbeType.BUFFER, osd_probe, result_vars)
        
        nvqueue = make_gst_element(*pipeline_config.queue,pipeline_vars=pipeline_vars)
        
        nvvidconv_post = make_gst_element(*pipeline_config.nvvidconv_post,pipeline_vars=pipeline_vars)

        if pipeline_config.__class__.__name__ == "MSPTilerRTSP":
            pipeline_vars = add_rtsp_sink(ds_vars=ds_vars, pipeline_vars=pipeline_vars, result_vars=result_vars)
        else:
            pipeline_vars = add_file_sink(ds_vars=ds_vars, pipeline_vars=pipeline_vars, result_vars=result_vars)
        
    else:
        sys.exit("Choice of Pipeline Config is not Valid!")
    return pipeline_vars
