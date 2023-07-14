from imports import Gst

from utils.ds_vars import DsResultVars

from .probe_blocks import (
    iter_frame_meta, iter_tensor_meta, iter_object_meta, layers_to_objects
)

from .probe_utils import (
    add_obj_meta_to_frame, add_display_string
)


def tensor_to_object_probe(pad, info, result_vars:DsResultVars):
    """
    info -> batch_meta -> frame_meta -> user_meta -> tensor_meta -> layer_info
    """
    perf_data = result_vars.perf_data
    for batch_meta, frame_meta in iter_frame_meta(info):
        perf_data.update_fps(perf_data.get_stream_key(frame_meta.pad_index))
        result_vars.frame_count += 1
        for tensor_meta in iter_tensor_meta(frame_meta):
            frame_object_list = layers_to_objects(tensor_meta=tensor_meta, parser_func=result_vars.parser_func)
            result_vars.det_count += len(frame_object_list)

            for frame_object in frame_object_list:
                add_obj_meta_to_frame(frame_object, batch_meta, frame_meta, result_vars.label_names)
                label_name = result_vars.label_names[frame_object.classId]
                if label_name in result_vars.object_count.keys():
                    result_vars.object_count[label_name] += 1
                else:
                    result_vars.object_count[label_name] = 1
    return Gst.PadProbeReturn.OK


def read_obj_meta_probe(pad, info, result_vars:DsResultVars):
    """
    info -> batch_meta -> frame_meta -> object_meta
    """
    perf_data = result_vars.perf_data
    for batch_meta, frame_meta in iter_frame_meta(info):
        perf_data.update_fps(perf_data.get_stream_key(frame_meta.pad_index))
        result_vars.frame_count += 1
        for obj_meta in iter_object_meta(frame_meta):
            result_vars.det_count += 1
            label_name = result_vars.label_names[obj_meta.class_id]
            if label_name in result_vars.object_count.keys():
                result_vars.object_count[label_name] += 1
            else:
                result_vars.object_count[label_name] = 1
    return Gst.PadProbeReturn.OK


def overlay_probe(pad, info, result_vars:DsResultVars):
    for batch_meta, frame_meta in iter_frame_meta(info):
        add_display_string(batch_meta=batch_meta, frame_meta=frame_meta, result_vars=result_vars)
    return Gst.PadProbeReturn.OK
