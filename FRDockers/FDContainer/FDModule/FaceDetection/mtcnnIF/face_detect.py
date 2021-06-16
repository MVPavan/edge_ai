from pathlib import Path
import cv2
import numpy as np
import mxnet as mx
from FDModule.FaceDetection.mtcnnIF.mtcnn_detector import MtcnnDetector
from FRCommon.fr_config import FDConfig, CoreConfig
from .face_preprocess import preprocess


def do_flip(data):
    for idx in range(data.shape[0]):
        data[idx, :, :] = np.fliplr(data[idx, :, :])


class FaceDetect:
    def __init__(self,):
        mtcnn_path = Path(FDConfig.FD_MTCNN_CAFFE_WEIGHTS)
        if CoreConfig.GPU_DEVICE >= 0:
            ctx = mx.gpu(CoreConfig.GPU_DEVICE)
        else:
            ctx = mx.cpu()

        if FDConfig.MTCNN_DET_MODE == 0:
            self.detector = MtcnnDetector(
                model_folder=mtcnn_path,
                ctx=ctx,
                num_worker=1,
                accurate_landmark=True,
                minsize=FDConfig.FD_MIN_SIZE,
                threshold=FDConfig.MTCNN_NETWORK_THRESHOLDS,
            )
        else:
            self.detector = MtcnnDetector(
                model_folder=mtcnn_path,
                ctx=ctx,
                num_worker=1,
                accurate_landmark=True,
                threshold=[0.0, 0.0, 0.2],
            )

    def detect(self, face_img):
        res = self.detector.detect_face(face_img, det_type=FDConfig.MTCNN_DET_MODE)
        if res is not None:
            bbox_list, landmarks_list = res
        else:
            bbox_list, landmarks_list = [[], []]
        return (bbox_list, landmarks_list)

    def faceAlign(self, face_img, bbox_list=[], landmarks_list=[]):
        """
        input: Image, bounding boxes, landmarks
        output: cropped/Aligned and preprocessed
        """
        faces_list = []
        bbox_list_conf = []
        face_counter = 0
        for bbox_ in bbox_list:
            if bbox_[4] > FDConfig.FD_CONFIDENCE_THRESHOLD:
                bbox = bbox_[0:4]
                landmarks = landmarks_list[face_counter - 1, :].reshape((2, 5)).T
                nimg = preprocess(
                    img=face_img,
                    bbox=bbox,
                    landmark=landmarks,
                    image_size=FDConfig.FR_IMAGE_SIZE,
                )
                nimg = cv2.cvtColor(nimg, cv2.COLOR_BGR2RGB)
                aligned_face = np.transpose(nimg, (2, 0, 1))
                aligned_face = aligned_face.astype("uint32", order='C',copy=False)
                faces_list.append(aligned_face)
                bbox_list_conf.append(bbox_)
            face_counter += 1
        return (faces_list, bbox_list_conf)