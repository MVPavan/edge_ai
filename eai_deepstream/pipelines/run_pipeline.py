from imports import (Gst, GLib,)


from eai_deepstream.ds_utils.bus_call import bus_call

import logging
ds_log = logging.getLogger()

from pipelines.pipeline_builds.ds_pipeline_base import DsPipelineBase

def graph_pipeline(ds_pipeline:DsPipelineBase):
    # GST_DEBUG_DUMP_DOT_DIR=/data/datasets/temp python3 run_ds.py
    # os.environ["GST_DEBUG_DUMP_DOT_DIR"] = "/tmp"
    # os.putenv('GST_DEBUG_DUMP_DIR_DIR', '/tmp')
    Gst.debug_bin_to_dot_file_with_ts(
        ds_pipeline.pipeline,
        Gst.DebugGraphDetails.ALL,
        "pipeline_rtsp"
    )


def run_pipeline(ds_pipeline:DsPipelineBase):
    graph_pipeline(ds_pipeline=ds_pipeline)
    # start play back and listen to events
    ds_log.info("Starting pipeline \n")
    # create an event loop and feed gstreamer bus mesages to it
    loop = GLib.MainLoop()
    bus = ds_pipeline.pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", bus_call, loop)
    ds_pipeline.pipeline.set_state(Gst.State.PLAYING)
    try:
        loop.run()
    except:
        pass
    # cleanup
    ds_pipeline.pipeline.set_state(Gst.State.NULL)
    return ds_pipeline