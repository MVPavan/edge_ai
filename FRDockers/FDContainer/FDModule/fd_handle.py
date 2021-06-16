from FRCommon.fr_config import CoreConfig
from FDModule.FaceDetection.mtcnnIF.face_detect import FaceDetect

class FDHandle:  # Face Detect
    def __init__(self,):
        self.fd = FaceDetect()

    def detectFace(self, img):
        return self.fd.detect(face_img=img)

    def alignFace(self, img, bbox_list, landmarks_list):
        return self.fd.faceAlign(
            face_img=img, bbox_list=bbox_list, landmarks_list=landmarks_list
        )
