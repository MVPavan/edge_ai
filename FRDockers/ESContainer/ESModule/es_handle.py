from FRCommon.fr_config import CoreConfig
from ESModule.ESFeatures.embed_search import FaissIndexes
from ESModule.ESFeatures.fr_feature_log import FRFeatureLog
import numpy as np



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
        