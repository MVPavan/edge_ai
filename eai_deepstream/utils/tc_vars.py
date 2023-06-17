
from dataclasses import dataclass
import logging
tc_log  = logging.getLogger()
@dataclass
class TritonVars:
    URL = "127.0.0.1:8001"
    MODEL_NAME = None
    MODEL_VERSION = '1'
    MODEL_INPUT_NAME = None
    MODEL_INPUT_DTYPE = None
    MODEL_OUTPUT_NAME = None
    MODEL_WIDHT = None
    MODEL_HEIGHT = None
    force_reload:bool = False
    unload_all:bool = False


@dataclass
class ImageVars:
    input_folder = None
    output_folder = None
    image_paths_dict={}
    resize_hwr_dict={}  # actual height width and resize ratio
    indices = []
    inference_images = []
    original_images = []


@dataclass
class TcResultVars:
    post_process_func = None 
    async_requests = None
    sent_count:int = 0 

@dataclass
class ModelChoice:
    yolox:bool = False
    yolov7:bool = False
    peoplenet:bool = False
    def __post_init__(self):
        model_choices = [self.yolox, self.yolov7,self.peoplenet]
        if sum(model_choices)!=1:
            raise ValueError("Only one model must be selected")

if __name__=="__main__":
    tc_log.info("here")