from FRModule.FRCore.fr_config import CoreConfig
from FRModule.FaceDetection.mtcnnIF.face_detect import FaceDetect
from FRModule.FaceEmbedding.arcfaceIF.face_embedding import FaceEmbedding
from FRModule.FRFeatures.embed_search import FaissIndexes
from FRModule.FRFeatures.fr_feature_log import FRFeatureLog
import numpy as np

class FRHandle:  # Face Recognition
    def __init__(self, detect_only=False):
        self.fd = FaceDetect()
        if not detect_only:
            self.fr = FaceEmbedding()

    def detectFace(self, img):
        return self.fd.detect(face_img=img)

    def alignFace(self, img, bbox_list, landmarks_list):
        return self.fr.faceAlign(
            face_img=img, bbox_list=bbox_list, landmarks_list=landmarks_list
        )

    def embedFace(self, aligned_face):
        return self.fr.getEmbedding(aligned_face=aligned_face)


class FDHandle:  # Face Detect
    def __init__(self,):
        self.fd = FaceDetect()

    def detectFace(self, img):
        return self.fd.detect(face_img=img)

    def alignFace(self, img, bbox_list, landmarks_list):
        return self.fd.faceAlign(
            face_img=img, bbox_list=bbox_list, landmarks_list=landmarks_list
        )


class FEHandle:  # Face Embeddigns
    def __init__(self, detect_only=False):
        self.fr = FaceEmbedding()

    def alignFace(self, img, bbox_list, landmarks_list):
        return self.fr.faceAlign(
            face_img=img, bbox_list=bbox_list, landmarks_list=landmarks_list
        )

    def embedFace(self, aligned_face):
        return self.fr.getEmbedding(aligned_face=aligned_face)


class ESHandle:  # Embeddings Search
    def __init__(self):
        self.feature_log = FRFeatureLog()
        self.es = FaissIndexes(dim=512)
        self.initIndexes()

    def initIndexes(self, neighbours=1, nq=1):
        '''
        choose between indexed and non indexed searching
        -loadGroupIndex for Indexed search - Further of choice of 
        which type of indexed search can be made in embed_search file
        -knnL2sqrHeap for non indexed search
        '''
        self.es.loadGroupIndex(self.feature_log.groupFeatures)
        # self.es.knnL2sqrHeap(neighbours=1, nq=1)

    def updateNewEmbed(self, face_embedding, groupUUID, eid):
        '''
        Group the new Embedding, eid into thier appropriate groups
        if Indexsearch is choosed retrain the groupIndex for new changed group
        uncomment traingroupIndex
        '''
        self.feature_log.embedGrouping(
            grp_name=groupUUID,
            face_embedding=face_embedding,
            face_id=eid,
        )
        self.es.trainGroupIndex(
            groupName=groupUUID,
            faceEmbeds=self.feature_log.groupFeatures[groupUUID +
                                                      CoreConfig.grp_embeds]
        )
        self.feature_log.featureSaver(grp_name=groupUUID)

    def embedSearch(self, groupUUID, queryVec, neighbours=1):
        '''
        choose between indexed and non indexed searching
        neighbours here only affects indexed search
        for non indexed search change neighbours using initIndexes
        '''
        # D,I = self.es.embedSearchNoIndex(
        #     queryVec=queryVec,
        #     embeds=self.feature_log.groupFeatures[groupUUID +
        #                                           CoreConfig.grp_embeds])
        D, I = self.es.embedSearchIndex(
            groupName=groupUUID, queryVec=queryVec, neighbours=neighbours)
        return (D, I)

    def embedMatch(self, queryVec, groupUUID, eid):
        # D, I = self.es.embedSearchNoIndex(
        #     queryVecs=queryVec, embed=self.feature_log.getEIDEmbed(grp_name=groupUUID, eid=eid))
        D, I = self.es.embedSearchCosine(
            queryVecs=queryVec, embed=self.feature_log.getEIDEmbed(grp_name=groupUUID, eid=eid))
        return (D, I)

    def getEIDS(self, groupUUID, idx):
        try:
            return self.feature_log.groupFeatures[groupUUID+CoreConfig.grp_ids][idx]
        except:
            return np.zeros((idx.shape[0],1)).astype("<U7")
        