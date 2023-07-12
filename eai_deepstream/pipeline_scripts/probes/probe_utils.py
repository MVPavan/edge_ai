from eai_core_api.imports import (
    pyds, logger
)

from utils.ds_vars import DsResultVars

UNTRACKED_OBJECT_ID = 0xffffffffffffffff

def add_display_string(batch_meta, frame_meta, result_vars:DsResultVars):
    perf_data = result_vars.perf_data
    frame_number = frame_meta.frame_num
    num_rects = frame_meta.num_obj_meta
    stream_fps = perf_data.get_stream_fps(perf_data.get_stream_key(frame_meta.pad_index))
    # Acquiring a display meta object. The memory ownership remains in
    # the C code so downstream plugins can still access it. Otherwise
    # the garbage collector will claim it when this probe function exits.
    display_meta = pyds.nvds_acquire_display_meta_from_pool(batch_meta)
    display_meta.num_labels = 1
    py_nvosd_text_params = display_meta.text_params[0]
    # Setting display text to be shown on screen
    # Note that the pyds module allocates a buffer for the string, and the
    # memory will not be claimed by the garbage collector.
    # Reading the display_text field here will return the C address of the
    # allocated string. Use pyds.get_string() to get the string content.
    disp_string = "Frame Number={} Number of Objects={} Stream FPS={}"
    py_nvosd_text_params.display_text = disp_string.format(
        frame_number,
        num_rects,
        stream_fps
    )
    # Now set the offsets where the string should appear
    py_nvosd_text_params.x_offset = 10
    py_nvosd_text_params.y_offset = 12
    # Font , font-color and font-size
    py_nvosd_text_params.font_params.font_name = "Serif"
    py_nvosd_text_params.font_params.font_size = 10
    # set(red, green, blue, alpha); set to White
    py_nvosd_text_params.font_params.font_color.set(1.0, 1.0, 1.0, 1.0)
    # Text background color
    py_nvosd_text_params.set_bg_clr = 1
    # set(red, green, blue, alpha); set to Black
    py_nvosd_text_params.text_bg_clr.set(0.0, 0.0, 0.0, 1.0)
    # Using pyds.get_string() to get display_text as string
    # print(pyds.get_string(py_nvosd_text_params.display_text))
    pyds.nvds_add_display_meta_to_frame(frame_meta, display_meta)

def add_obj_meta_to_frame(frame_object, batch_meta, frame_meta, label_names):
    """ Inserts an object into the metadata """
    # this is a good place to insert objects into the metadata.
    # Here's an example of inserting a single object.
    obj_meta = pyds.nvds_acquire_obj_meta_from_pool(batch_meta)
    # Set bbox properties. These are in input resolution.
    rect_params = obj_meta.rect_params
    rect_params.left = int(frame_object.left)
    rect_params.top = int(frame_object.top)
    rect_params.width = int(frame_object.width)
    rect_params.height = int(frame_object.height)

    # Semi-transparent yellow backgroud
    rect_params.has_bg_color = 0
    rect_params.bg_color.set(1, 1, 0, 0.4)

    # Red border of width 3
    rect_params.border_width = 3
    rect_params.border_color.set(1, 0, 0, 1)

    # Set object info including class, detection confidence, etc.
    obj_meta.confidence = frame_object.detectionConfidence
    obj_meta.class_id = frame_object.classId

    # There is no tracking ID upon detection. The tracker will
    # assign an ID.
    obj_meta.object_id = UNTRACKED_OBJECT_ID

    lbl_id = frame_object.classId
    if lbl_id >= len(label_names):
        lbl_id = 0

    # Set the object classification label.
    obj_meta.obj_label = label_names[lbl_id]

    # Set display text for the object.
    txt_params = obj_meta.text_params
    if txt_params.display_text:
        pyds.free_buffer(txt_params.display_text)

    txt_params.x_offset = int(rect_params.left)
    txt_params.y_offset = max(0, int(rect_params.top) - 10)
    txt_params.display_text = (
        label_names[lbl_id] + " " + "{:04.3f}".format(frame_object.detectionConfidence)
    )
    # Font , font-color and font-size
    txt_params.font_params.font_name = "Serif"
    txt_params.font_params.font_size = 10
    # set(red, green, blue, alpha); set to White
    txt_params.font_params.font_color.set(1.0, 1.0, 1.0, 1.0)

    # Text background color
    txt_params.set_bg_clr = 1
    # set(red, green, blue, alpha); set to Black
    txt_params.text_bg_clr.set(0.0, 0.0, 0.0, 1.0)

    # Inser the object into current frame meta
    # This object has no parent
    pyds.nvds_add_obj_meta_to_frame(frame_meta, obj_meta, None)
    return label_names[lbl_id]


