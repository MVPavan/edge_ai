import sys
from pathlib import Path

import gi
gi.require_version("Gst", "1.0")
from gi.repository import GLib, Gst

from utils.ds_vars import DSVars, DsResultVars

from deep_stream.plugins.basic_plugins import (
    PipelineVars, make_gst_element, run_pipeline
)
from deep_stream.plugins.multi_input_plugin import create_multisrc_inputbin
from deep_stream.probes.probe_funcs import tensor_to_object_probe

from .pipeline_choices import MSPFake, MSPOsd, output_folder
from .sink_pipeline import add_viz_pipeline

import logging
ds_log = logging.getLogger()


def run_msp(ds_vars:DSVars, result_vars:DsResultVars):
    pipeline_config = ds_vars.pipeline_config
    perf_data = result_vars.perf_data
    
    pipeline_vars = PipelineVars()

    ds_log.info("Adding elements to Pipeline \n")
    streamux_props={
        "width": ds_vars.width,
        "height": ds_vars.height,
        "batch-size": ds_vars.batch_size,
        "batched-push-timeout": 4000000
    }
    streammux = make_gst_element(
        *pipeline_config.stream_muxer, pipeline_vars=pipeline_vars,
        properties=streamux_props
    )

    #TODO: Explore nvmultiurisrcbin
    streammux = create_multisrc_inputbin(
        uri_list=ds_vars.uri_list, pipeline_vars=pipeline_vars,
        streammux=streammux
    )

    pgie = make_gst_element(
        *pipeline_config.triton_server, pipeline_vars=pipeline_vars,
        properties={"config-file-path": ds_vars.pgie_config_file}
    )
    # Add a probe on the primary-infer source pad to get inference output tensors
    pgiesrcpad = pgie.get_static_pad("src")
    if not pgiesrcpad:
        sys.stderr.write(" Unable to get src pad of primary infer \n")
    pgiesrcpad.add_probe(Gst.PadProbeType.BUFFER, tensor_to_object_probe, result_vars)

    pipeline_vars = add_viz_pipeline(ds_vars=ds_vars, pipeline_vars=pipeline_vars, result_vars=result_vars)
    
    link_list = [element.name for element in pipeline_vars.link_sequence]
    ds_log.info(
        f"Linking elements in the Pipeline : \n{link_list}\n",
    )
    for i in range(len(pipeline_vars.link_sequence)-1):
        pipeline_vars.link_sequence[i].link(pipeline_vars.link_sequence[i+1])

    # Start perf analysis and run pipeline
    GLib.timeout_add(perf_data.delta_time, perf_data.perf_print_callback)
    perf_data.start_fps(len(ds_vars.uri_list))

    pipeline_vars = run_pipeline(pipeline_vars=pipeline_vars)

    return result_vars

