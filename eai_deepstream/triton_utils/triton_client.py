######################################################################
############### YOLOX TRITON CLIENT #################################


import sys
import time
from pathlib import Path
from tqdm import tqdm
from functools import partial, wraps
import logging
import queue
import numpy as np
from omegaconf import OmegaConf
import tritonclient.grpc as grpcclient
import pprint
pp = pprint.PrettyPrinter(depth=4)
from utils.other_utils import timeit
from .tc_vars import TritonVars, ImageVars, TcResultVars
from .tc_stats_utils import save_stats_json
tc_log = logging.getLogger()
tc_grpc = None 

class AsyncRequests:
    """Data structure to gather queued requests."""
    def __init__(self):
        self._completed_requests = queue.Queue()


def create_triton_client_grpc(triton_url):
    global tc_grpc
    if tc_grpc is not None:return
    try:
        tc_grpc = grpcclient.InferenceServerClient(url=triton_url,verbose=False)
        tc_log.info("\nEstablished GRPC connection: Success")
    except Exception as e:
        tc_log.info("channel creation failed: " + str(e))
        sys.exit(1)
    if not tc_grpc.is_server_live():
        sys.exit("Server is not live!")

def unload_all_models():
    model_repo = tc_grpc.get_model_repository_index()
    for model in model_repo.models:
        if model.state == "READY":
            tc_log.info(f"unloading {model.name}")
            tc_grpc.unload_model(model.name)
            


def load_triton_model(triton_vars:TritonVars):
    model_loading = False
    create_triton_client_grpc(triton_vars.URL)
    if triton_vars.unload_all:
        unload_all_models()
        
    if not check_model_ready(triton_vars=triton_vars):
        tc_log.info("attempting load ....")
        tc_grpc.load_model(model_name=triton_vars.MODEL_NAME)
        model_loading = True
    elif triton_vars.force_reload:
        tc_log.info("attempting force reload ....")
        tc_grpc.unload_model(model_name=triton_vars.MODEL_NAME)
        tc_grpc.load_model(model_name=triton_vars.MODEL_NAME)
        model_loading = True

    if model_loading:
        timeout = 30
        timeout_start = time.time()
        while True:
            if check_model_ready(triton_vars=triton_vars):
                tc_log.info("Load Successful!")
                break
            elif time.time() > timeout_start + timeout:
                sys.exit(f"Failed to load model with in {timeout} sec")
            time.sleep(5)


def check_model_ready(triton_vars:TritonVars):
    if not tc_grpc.is_model_ready(
        model_name=triton_vars.MODEL_NAME, 
        model_version=triton_vars.MODEL_VERSION):
        tc_log.info(f"Model: {triton_vars.MODEL_NAME},\
            Version: {triton_vars.MODEL_VERSION} not loaded")
        return False
    else:
        return True
        

def get_triton_model_config(triton_vars:TritonVars):
    load_triton_model(triton_vars=triton_vars)
    model_config = tc_grpc.get_model_config(
        model_name=triton_vars.MODEL_NAME, 
        model_version=triton_vars.MODEL_VERSION, 
        as_json=True
    )
    mcd = OmegaConf.create(model_config["config"])
    if len(mcd.input) > 1:
        sys.exit("Currently supports model with 1 input")
    triton_vars.MODEL_INPUT_NAME = mcd.input[0].name
    triton_vars.MODEL_INPUT_DTYPE = mcd.input[0].data_type.split("TYPE_")[-1]
    if int(mcd.input[0].dims[-1])==3:
        triton_vars.MODEL_WIDHT = int(mcd.input[0].dims[-2])
        triton_vars.MODEL_HEIGHT = int(mcd.input[0].dims[-3])
    else:
        triton_vars.MODEL_WIDHT = int(mcd.input[0].dims[-1])
        triton_vars.MODEL_HEIGHT = int(mcd.input[0].dims[-2])
    triton_vars.MODEL_OUTPUT_NAME = [node.name for node in mcd.output]

    model_metadata = tc_grpc.get_model_metadata(
        model_name=triton_vars.MODEL_NAME, 
        model_version=triton_vars.MODEL_VERSION, 
        as_json=True
    )
    tc_log.info("Model Metadata: ")
    tc_log.info(model_metadata)
    pp.pprint(model_metadata)

    return triton_vars

def gather_async(asyc_resquests, result, error):
    asyc_resquests._completed_requests.put((result, error))


@timeit
def wait_async(image_vars:ImageVars,  triton_vars:TritonVars, result_vars:TcResultVars):
    processed_count = 0
    pbar = tqdm(total=result_vars.sent_count, desc="Postprocessing: ")
    while processed_count < result_vars.sent_count:
        (result, error) = result_vars.async_requests._completed_requests.get()
        processed_count += 1
        if error is not None:
            tc_log.info("inference failed: " + str(error))
            sys.exit(1)
        if result_vars.post_process_func is not None:
            result_vars.post_process_func(result=result, image_vars=image_vars, triton_vars=triton_vars, result_vars=result_vars)
        pbar.update(1)
    pbar.close()


@timeit
def run_grpc_inference(image_vars:ImageVars,  triton_vars:TritonVars, result_vars:TcResultVars):
    create_triton_client_grpc(triton_vars.URL)

    model_stats = tc_grpc.get_inference_statistics(
        model_name=triton_vars.MODEL_NAME, 
        model_version=triton_vars.MODEL_VERSION, 
        as_json=True
    )
    save_stats_json(model_stats=model_stats, file_name="start.json")

    result_vars.async_requests=AsyncRequests()
    result_vars.sent_count=0

    for idx, inference_image in tqdm(zip(image_vars.indices,image_vars.inference_images),total=len(image_vars.inference_images), desc="GRPC Inference "):
        if "uint8" in triton_vars.MODEL_INPUT_DTYPE.lower():
            inference_image = np.ascontiguousarray(inference_image, dtype=np.uint8)
        elif "fp32" in triton_vars.MODEL_INPUT_DTYPE.lower():
            # Normalize image (0,1)
            inference_image = np.ascontiguousarray(inference_image/255.0, dtype=np.float32)
        else:
            sys.exit("Unknown Input data type!")

        if len(inference_image.shape) < 4:
            inference_image = np.expand_dims(inference_image,axis=0)
        batch_no, ch,h,w = inference_image.shape

        inputs = [
            grpcclient.InferInput(triton_vars.MODEL_INPUT_NAME, [batch_no, ch,h,w], triton_vars.MODEL_INPUT_DTYPE)
        ]
        inputs[0].set_data_from_numpy(inference_image)
        outputs = [grpcclient.InferRequestedOutput(output_name) for output_name in triton_vars.MODEL_OUTPUT_NAME]

        tc_grpc.async_infer(
            model_name=triton_vars.MODEL_NAME,
            model_version=triton_vars.MODEL_VERSION,
            request_id=idx,
            callback=partial(gather_async,result_vars.async_requests),
            inputs=inputs,
            outputs=outputs
        )
        result_vars.sent_count+=1

    wait_async(image_vars=image_vars, triton_vars=triton_vars, result_vars=result_vars)
    model_stats = tc_grpc.get_inference_statistics(
        model_name=triton_vars.MODEL_NAME, 
        model_version=triton_vars.MODEL_VERSION, 
        as_json=True
    )
    save_stats_json(model_stats=model_stats, file_name="end.json")
    return result_vars

