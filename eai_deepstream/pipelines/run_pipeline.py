from imports import (os, Gst, GLib, Path)


from ds_utils.bus_call import bus_call

import logging
logger = logging.getLogger()

from pipelines.pipeline_builds.ds_pipeline_base import DsPipelineBase

def graph_pipeline(ds_pipeline:DsPipelineBase):
    # GST_DEBUG_DUMP_DOT_DIR=/data/datasets/temp python3 run_ds.py
    # os.environ["GST_DEBUG_DUMP_DOT_DIR"] = "/tmp"
    # os.putenv('GST_DEBUG_DUMP_DIR_DIR', '/tmp')
    log_path = Path(logger.handlers[1].baseFilename) # type: ignore
    gst_log_folder = log_path.parent/"gst_logs"
    gst_graph_folder = gst_log_folder/"graph"
    gst_graph_folder.mkdir(exist_ok=True, parents=True)
    os.environ["GST_DEBUG_DUMP_DOT_DIR"] = gst_graph_folder.as_posix()
    Gst.debug_bin_to_dot_file_with_ts(
        ds_pipeline.pipeline,
        Gst.DebugGraphDetails.ALL,
        ds_pipeline.pipeline_name
    )

def initialize_fps_calculation(ds_pipeline:DsPipelineBase):
    perf_data = ds_pipeline.result_vars.perf_data
    if ds_pipeline.pipeline_props.plugins.custom_parser or \
        ds_pipeline.pipeline_props.plugins.fps:
        GLib.timeout_add(perf_data.delta_time, perf_data.perf_print_callback)

def run_pipeline(ds_pipeline:DsPipelineBase):
    graph_pipeline(ds_pipeline=ds_pipeline)
    initialize_fps_calculation(ds_pipeline=ds_pipeline)
    # start play back and listen to events
    logger.info("Starting pipeline \n")
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