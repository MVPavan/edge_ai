import sys
from utils.tc_vars import ModelChoice

def get_pgie_model_config(model_choices:ModelChoice):
    if model_choices.yolox:
        config_file = "./deep_stream/ds_configs/config_triton_ensemble_yolox.txt"
    elif model_choices.yolov7:
        config_file = "./deep_stream/ds_configs/config_triton_yolov7_nms.txt"
    elif model_choices.peoplenet:
        config_file = "./deep_stream/ds_configs/config_triton_peoplenet.txt"
    else:
        sys.exit("Config file not available for model choice!")
    return config_file
