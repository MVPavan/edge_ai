import sys
import io
import gi
gi.require_version("Gst", "1.0")
from gi.repository import GLib, Gst
import pyds

from deep_stream.ds_utils.is_aarch_64 import is_aarch64
from deep_stream.ds_utils.bus_call import bus_call
from utils.ds_vars import DSVars, DsResultVars

from deep_stream.plugins.basic_plugins import create_pipeline, make_gst_element
from deep_stream.plugins.multi_input_plugin import create_multisrc_inputbin
from deep_stream.probes.probe_funcs import tensor_to_object_probe

from .pipeline_choices import MultiStreamPipeline

import logging
ds_log = logging.getLogger()


pipeline_config = MultiStreamPipeline()

def ds_main(ds_vars:DSVars, result_vars:DsResultVars):
    perf_data = result_vars.perf_data
    pipeline = create_pipeline()
    streammux = make_gst_element(*pipeline_config.stream_muxer)
    pipeline.add(streammux)

    #TODO: Explore nvmultiurisrcbin
    pipeline, streammux = create_multisrc_inputbin(
        uri_list=ds_vars.uri_list,
        pipeline=pipeline,
        streammux=streammux
    )
    pgie = make_gst_element(*pipeline_config.triton_server )

    fakesink=make_gst_element(*pipeline_config.sink)
    fakesink.set_property('sync', 1)

    streammux.set_property("width", ds_vars.width)
    streammux.set_property("height", ds_vars.height)
    streammux.set_property("batch-size", result_vars.batch_size)
    streammux.set_property("batched-push-timeout", 4000000)

    pgie.set_property("config-file-path", ds_vars.pgie_config_file)

    if not is_aarch64():
        # Use CUDA unified memory in the pipeline so frames
        # can be easily accessed on CPU in Python.
        mem_type = int(pyds.NVBUF_MEM_CUDA_UNIFIED)
        streammux.set_property("nvbuf-memory-type", mem_type)

    ds_log.info("Adding elements to Pipeline \n")
    pipeline.add(pgie)
    pipeline.add(fakesink)
    
    ds_log.info("Linking elements in the Pipeline \n")
    streammux.link(pgie)
    pgie.link(fakesink)

    # Add a probe on the primary-infer source pad to get inference output tensors
    pgiesrcpad = pgie.get_static_pad("src")
    if not pgiesrcpad:
        sys.stderr.write(" Unable to get src pad of primary infer \n")

    pgiesrcpad.add_probe(Gst.PadProbeType.BUFFER, tensor_to_object_probe, result_vars)
    GLib.timeout_add(perf_data.delta_time, perf_data.perf_print_callback)

    # start play back and listen to events
    ds_log.info("Starting pipeline \n")
    perf_data.start_fps(len(ds_vars.uri_list))

    # create an event loop and feed gstreamer bus mesages to it
    loop = GLib.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", bus_call, loop)
    pipeline.set_state(Gst.State.PLAYING)
    try:
        loop.run()
    except:
        pass
    # cleanup
    pipeline.set_state(Gst.State.NULL)

    return result_vars

