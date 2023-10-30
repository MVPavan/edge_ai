
from dataclasses import dataclass
from typing import Optional
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
    inference_images_dict = {}


@dataclass
class TcResultVars:
    post_process_func = None 
    async_requests = None
    sent_count:int = 0 
    result_object = None
