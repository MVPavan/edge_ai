
import sys
import numpy as np
import pyds

from utils.ds_vars import DsResultVars
from deep_stream.probe_utils.nms import cluster_and_fill_detection_output_nms
from utils.tc_vars import ModelChoice


import logging
ds_log = logging.getLogger()


class BoxSizeParam:
    """ Class contaning base element for too small object box deletion. """
    def __init__(self, screen_height, screen_width,
                 min_box_height, min_box_width):
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.min_box_height = min_box_height
        self.min_box_width = min_box_width

    def is_percentage_sufficiant(self, percentage_height, percentage_width):
        """ Return True if detection box dimension is large enough,
            False otherwise.
        """
        res = self.screen_width * percentage_width > self.min_box_width
        res &= self.screen_height * percentage_height > self.min_box_height
        return res


class NmsParam:
    """ Contains parametter for non maximal suppression algorithm. """
    def __init__(self, top_k=20, iou_threshold=0.4):
        self.top_k = top_k
        self.iou_threshold = iou_threshold


class DetectionParam:
    """ Contains the number of classes and their detection threshold. """

    def __init__(self, class_nb=80, threshold=0.3):
        self.class_nb = class_nb
        self.classes_threshold = [threshold] * class_nb

    def get_class_threshold(self, index):
        """ Get detection value of a class """
        return self.classes_threshold[index]

def __layer_finder(output_layer_info, name, expected_dtype=0):
    """ Return the layer contained in output_layer_info which corresponds
        to the given name.

        pyds.NvDsInferDataType
        Enumerator, Specifies the data type of a layer.
        Members:
        FLOAT : FP32 format. <=> dataType == 0
        HALF : FP16 format. <=> dataType == 1
        INT8 : INT8 format. <=> dataType == 2
        INT32 : INT32 format <=> dataType == 3
    """
    for layer in output_layer_info:
        # print(layer.layerName, layer.dataType)
        if layer.dataType == expected_dtype and layer.layerName == name:
            return layer
    return None



def clip(elm, mini, maxi):
    """ Clips a value between mini and maxi."""
    return max(min(elm, maxi), mini)


def compute_nms(object_list, nms_param:NmsParam):
    if object_list:
        object_list = cluster_and_fill_detection_output_nms(
            object_list, nms_param.top_k, nms_param.iou_threshold
        )
    return object_list


def __make_nodi_object(score, class_idx, detection_param=None, bbox_xyxy=None, bbox_xywh=None):
    """ Creates a NvDsInferObjectDetectionInfo (NODI) object.
        Return None if the class Id is invalid, if the detection confidence
        is under the threshold or if the width/height of the bounding box is
        null/negative.
        Return the created NvDsInferObjectDetectionInfo object otherwise.
    """
    res = pyds.NvDsInferObjectDetectionInfo()
    res.detectionConfidence = score
    res.classId = class_idx

    if detection_param is not None:
        if res.classId >= detection_param.class_nb or res.detectionConfidence < detection_param.get_class_threshold(res.classId):
            return None

    if bbox_xyxy:
        res.left = int(bbox_xyxy[0])
        res.top = int(bbox_xyxy[1])
        res.width = int(bbox_xyxy[2] -  bbox_xyxy[0])
        res.height = int(bbox_xyxy[3] -  bbox_xyxy[1])

    elif bbox_xywh:
        res.left = int(bbox_xyxy[0])
        res.top = int(bbox_xyxy[1])
        res.width = int(bbox_xyxy[3])
        res.height = int(bbox_xyxy[2])
    
    else:
        sys.stderr.write("ERROR: No bbox info to make NODI object\n")
    # print(res.top, res.left, res.height, res.width)
    return res

def get_output_layer_info(tensor_meta):
    layers_info = []
    for i in range(tensor_meta.num_output_layers):
        layer = pyds.get_nvds_LayerInfo(tensor_meta, i)
        layers_info.append(layer)
    return layers_info


def __ds_parser_yolox(tensor_meta, detection_param=None,nms_param=None):
    output_layer_info = get_output_layer_info(tensor_meta)
    # print("Network info: ",tensor_meta.network_info.width, tensor_meta.network_info.height)
    yolo_bbox = __layer_finder(output_layer_info, "YOLOX_BBOX", 0)
    if not yolo_bbox :
        sys.stderr.write("ERROR: some layers missing in output tensors\n")
        return None
    num_detections,output_size = (yolo_bbox.inferDims.d)[:yolo_bbox.inferDims.numDims]
    # if num_detections>1:
    #     tc_log.info("Here: ",yolo_bbox.inferDims.d,num_detections,output_size )
    #     tc_log.info("Here: ",[pyds.get_detections(yolo_bbox.buffer, i) for i in range(7*i)])
    yolox_out = [pyds.get_detections(yolo_bbox.buffer, i) for i in range(7*num_detections)]

    object_list = []
    for i in range(num_detections):
        score = pyds.get_detections(yolo_bbox.buffer, 7*i+4)*pyds.get_detections(yolo_bbox.buffer, 7*i+5)
        class_idx = int(pyds.get_detections(yolo_bbox.buffer, 7*i+6))
        bbox_xyxy = [pyds.get_detections(yolo_bbox.buffer, 7*i+j) for j in range(4)]
        nodi_object = __make_nodi_object(
            score=score,
            class_idx=class_idx,
            bbox_xyxy=bbox_xyxy,
            detection_param=DetectionParam(threshold=0.3)
        )
        if nodi_object:
            object_list.append(nodi_object)
    
    if nms_param is not None:
        object_list = compute_nms(object_list=object_list, nms_param=nms_param)
    return object_list


def __ds_parser_yolov7(tensor_meta, detection_param=None,nms_param=None):
    output_layer_info = get_output_layer_info(tensor_meta)
    num_dets = __layer_finder(output_layer_info, "num_dets" , 3)
    bbox = __layer_finder(output_layer_info, "det_boxes", 0)
    scores = __layer_finder(output_layer_info, "det_scores", 0)
    det_classes = __layer_finder(output_layer_info, "det_classes", 3)
    if not num_dets :
        sys.stderr.write("ERROR: some layers missing in output tensors\n")
        return None

    num_detections = pyds.get_detections_int(num_dets.buffer, 0)

    object_list = []
    for i in range(num_detections):
        score = pyds.get_detections(scores.buffer, i)
        class_idx = pyds.get_detections_int(det_classes.buffer, i)
        bbox_xyxy = [pyds.get_detections(bbox.buffer, 4*i+j) for j in range(4)]
        nodi_object = __make_nodi_object(
            score=score,
            class_idx=class_idx,
            bbox_xyxy=bbox_xyxy,
            detection_param=DetectionParam(threshold=0.3)
        )
        if nodi_object:
            object_list.append(nodi_object)
    
    if nms_param is not None:
        object_list = compute_nms(object_list=object_list, nms_param=nms_param)
    return object_list


def __ds_parser_peoplenet(tensor_meta):
    output_layer_info = get_output_layer_info(tensor_meta)
    bbox = __layer_finder(output_layer_info, "output_bbox/BiasAdd")
    scores = __layer_finder(output_layer_info, "output_cov/Sigmoid")
    if not bbox :
        sys.stderr.write("ERROR: some layers missing in output tensors\n")
        return None
    return [True]


def get_ds_model_parser(model_choice:ModelChoice):
    if model_choice.yolox:
        parser_func = __ds_parser_yolox
    elif model_choice.yolov7:
        parser_func = __ds_parser_yolov7
    elif model_choice.peoplenet:
        parser_func = __ds_parser_peoplenet
    else:
        sys.exit("Parser Func not available for model choice!")
    return parser_func
