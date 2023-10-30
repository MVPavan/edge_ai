import io
import time
from pathlib import Path
from urllib.request import pathname2url
from urllib.parse import urljoin
from functools import partial, wraps
import importlib

import logging
tc_log  = logging.getLogger()

VIDEO_EXT = [".mp4",".h264",".avi"]

def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        tc_log.info(f'Function {func.__name__} Took {total_time:.6f} seconds')
        return result
    return timeit_wrapper


def get_label_names_from_file(filepath):
    """ Read a label file and convert it to string list """
    f = io.open(filepath, "r")
    labels = f.readlines()
    labels = [elm[:-1] for elm in labels]
    f.close()
    return labels


def path_to_uri(uri_str:str):
    file_path = Path(uri_str)
    if file_path.suffix in VIDEO_EXT:
        uri_str = urljoin('file:',pathname2url(file_path.as_posix()))
    return uri_str

def import_ext_module(module_name, module_file_path):
    spec=importlib.util.spec_from_file_location(module_name, module_file_path)
    temp_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(temp_module)
    return temp_module


"""
Importing external module

https://www.geeksforgeeks.org/how-to-import-a-python-module-given-the-full-path/

Method:1 

spec=importlib.util.spec_from_file_location("YOLOX","/home/pavanmv/work/YOLOX/tools/Yolox_eval_V51.py")
yolox_import = importlib.util.module_from_spec(spec)
spec.loader.exec_module(yolox_import)

Method:2
from importlib.machinery import SourceFileLoader
yolox_import = SourceFileLoader("yolox","/home/pavanmv/work/YOLOX/tools/Yolox_eval_V51.py").load_module()
"""
