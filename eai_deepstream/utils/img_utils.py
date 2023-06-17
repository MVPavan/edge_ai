import sys
import time
from pathlib import Path
from tqdm import tqdm
import numpy as np
import pandas as pd
import cv2
import logging
tc_log  = logging.getLogger()



yolo_bbox_format = ["class","x_center","y_center","width","height","score"]


def img_bgr_rgb(img, bgr=False, rgb=False):
    """
    Converts BGR images to RGB and viceverse.
    """
    if bgr or rgb:
        assert bgr!=rgb, "Both flags cant be True!"
    if bgr:
        return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    if rgb:
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

def img_swap_channels(img, swap=(2,0,1)):
    """
    swap = (2,0,1) : HWC --> CHW
    swap = (1,2,0) : CHW --> HWC
    """
    return img.transpose(swap)

def preproc_resize(img, input_size, swap=(2,0,1)):
    """
    input_size = HxW
    img.shape = HxWxC
    """
    if len(img.shape) == 3:
        padded_img = np.zeros((input_size[0], input_size[1], 3), dtype=np.uint8)
    else:
        padded_img = np.ones(input_size, dtype=np.uint8) * 114
    r = min(input_size[0] / img.shape[0], input_size[1] / img.shape[1])
    resized_img = cv2.resize(
        img,
        (int(img.shape[1] * r), int(img.shape[0] * r)),
        interpolation=cv2.INTER_LINEAR,
    ).astype(np.uint8)
    padded_img[: int(img.shape[0] * r), : int(img.shape[1] * r)] = resized_img
    
    if swap is not None:
        padded_img = img_swap_channels(padded_img, swap)
    return padded_img, r

def bbox_to_yolo_df(df, image_width, image_height):
    yolodf = pd.DataFrame(columns=yolo_bbox_format)
    df.columns = range(df.columns.size)
    yolodf["x_center"] = (df[0] + df[2]) / 2 / image_width
    yolodf["y_center"] = (df[1] + df[3]) / 2 / image_height
    yolodf["width"] = (df[2] - df[0]) / image_width
    yolodf["height"] = (df[3] - df[1]) / image_height
    return yolodf

