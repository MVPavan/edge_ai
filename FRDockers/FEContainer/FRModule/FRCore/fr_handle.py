from FRModule.FRCore.fr_config import CoreConfig
from FRModule.FaceEmbedding.arcfaceIF.face_embedding import FaceEmbedding
import numpy as np

class FEHandle:  # Face Embeddigns
    def __init__(self, detect_only=False):
        self.fr = FaceEmbedding()

    def alignFace(self, img, bbox_list, landmarks_list):
        return self.fr.faceAlign(
            face_img=img, bbox_list=bbox_list, landmarks_list=landmarks_list
        )

    def embedFace(self, aligned_face):
        return self.fr.getEmbedding(aligned_face=aligned_face)
