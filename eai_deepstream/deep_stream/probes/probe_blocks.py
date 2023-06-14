
import pyds

import logging
ds_log = logging.getLogger()


def iter_frame_meta(info):
    gst_buffer = info.get_buffer()
    if not gst_buffer:
        ds_log.info("Unable to get GstBuffer ")
        return
    # Retrieve batch metadata from the gst_buffer
    # Note that pyds.gst_buffer_get_nvds_batch_meta() expects the
    # C address of gst_buffer as input, which is obtained with hash(gst_buffer)
    batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))
    l_frame = batch_meta.frame_meta_list
    while l_frame is not None:
        try:
            # Note that l_frame.data needs a cast to pyds.NvDsFrameMeta
            # The casting also keeps ownership of the underlying memory
            # in the C code, so the Python garbage collector will leave
            # it alone.
            frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
        except StopIteration:
            break
        yield (batch_meta, frame_meta)

        try:
            # indicate inference is performed on the frame
            frame_meta.bInferDone = True
            l_frame = l_frame.next
        except StopIteration:
            break


def iter_tensor_meta(frame_meta:pyds.NvDsFrameMeta):
    """
    Tensor meta consists of layer info, which holds output tensor data
    """
    l_user = frame_meta.frame_user_meta_list
    while l_user is not None:
        try:
            user_meta = pyds.NvDsUserMeta.cast(l_user.data)
        except StopIteration:
            break
        if user_meta.base_meta.meta_type != pyds.NvDsMetaType.NVDSINFER_TENSOR_OUTPUT_META:
            continue

        tensor_meta = pyds.NvDsInferTensorMeta.cast(user_meta.user_meta_data)

        # Boxes in the tensor meta should be in network resolution which is
        # found in tensor_meta.network_info. Use this info to scale boxes to
        # the input frame resolution.
        
        yield tensor_meta

        try:
            l_user = l_user.next
        except StopIteration:
            break
        

def layers_to_objects(tensor_meta, parser_func):
    frame_object_list = parser_func(tensor_meta)
    if frame_object_list is None:
        ds_log.info("Unable to parse tensor_meta")
        return
    return frame_object_list