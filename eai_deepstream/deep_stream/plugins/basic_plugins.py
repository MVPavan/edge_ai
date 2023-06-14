
import sys, os
from dataclasses import dataclass, field
from pathlib import Path
import gi
gi.require_version("Gst", "1.0")
from gi.repository import GLib, Gst
import pyds

from deep_stream.ds_utils.bus_call import bus_call
from deep_stream.ds_utils.is_aarch_64 import is_aarch64

import logging
ds_log = logging.getLogger()

CUDA_MEM_ELEMENTS = ["nvstreammux","nvvideoconvert","nvmultistreamtiler"]


@dataclass
class PipelineVars:
    pipeline:Gst.Pipeline = None
    link_sequence:list = field(default_factory=list)

    def __post_init__(self):
        self.pipeline = create_pipeline()

def create_pipeline():
    Gst.init(None)
    ds_log.info("Creating Pipeline \n ")
    pipeline = Gst.Pipeline()
    if not pipeline:
        sys.stderr.write(" Unable to create Pipeline \n")
    return pipeline

def make_gst_element(
        factory_name,
        user_name, 
        pipeline_vars:PipelineVars,
        properties:dict={},
    ):
    """ Creates an element with Gst Element Factory make.
        Return the element  if successfully created, otherwise print
        to stderr and return None.
    """
    element = Gst.ElementFactory.make(factory_name, user_name)
    if not element:
        sys.stderr.write("Unable to create " + user_name + " \n")

    ds_log.info(f"Created Element :{element.get_name()}")
    for key, value in properties.items():
        element.set_property(key, value)
    if factory_name in CUDA_MEM_ELEMENTS:
        element = set_memory_types(element=element)
    pipeline_vars.pipeline.add(element)
    pipeline_vars.link_sequence.append(element)
    return element


def set_memory_types(element):
    if not is_aarch64():
        # Use CUDA unified memory in the pipeline so frames
        # can be easily accessed on CPU in Python.
        mem_type = int(pyds.NVBUF_MEM_CUDA_UNIFIED)
        element.set_property("nvbuf-memory-type", mem_type)
    return element


def graph_pipeline(pipeline_vars:PipelineVars):
    # GST_DEBUG_DUMP_DOT_DIR=/data/datasets/temp python3 run_ds.py
    # os.environ["GST_DEBUG_DUMP_DOT_DIR"] = "/tmp"
    # os.putenv('GST_DEBUG_DUMP_DIR_DIR', '/tmp')
    Gst.debug_bin_to_dot_file_with_ts(
        pipeline_vars.pipeline,
        Gst.DebugGraphDetails.ALL,
        "pipeline_rtsp"
    )


def run_pipeline(pipeline_vars:PipelineVars):
    graph_pipeline(pipeline_vars=pipeline_vars)
    # start play back and listen to events
    ds_log.info("Starting pipeline \n")
    # create an event loop and feed gstreamer bus mesages to it
    loop = GLib.MainLoop()
    bus = pipeline_vars.pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", bus_call, loop)
    pipeline_vars.pipeline.set_state(Gst.State.PLAYING)
    try:
        loop.run()
    except:
        pass
    # cleanup
    pipeline_vars.pipeline.set_state(Gst.State.NULL)
    return pipeline_vars