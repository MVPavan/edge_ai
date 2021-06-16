import time
import faiss  # make faiss available
import numpy as np
from numpy.linalg import norm
from FRCommon.fr_config import logger, CoreConfig


"""
Conclusions of the Experiment:
L2, faiss.METRIC_L2 for euclidean distance and IP , faiss.METRIC_INNER_PRODUCT for cosine similarity
couldn't find a way to get cosine similarity for indexIVFFlat

faiss.IndexFlatL2 / faiss.knn_L2sqr:
These are better options for dimesions <= 1000 with response time in 100's of micro secs
and from 1000 tot 10000 its still a better option with response time in single digit milli secs
knn_L2sqr doesnt require index training, it directly performs on memory heaps, and train time of IndexFlatL2 for nb<1000 is in micro secs
so for consistency fo implementation between IndexFlatL2 and IndexIVFFlat, IndexFlatL2 is chosen over knn_L2sqr

faiss.IndexIVFFlat:
for all the sizes this a very fast in search
nb <= 1000 similar to IndexFlatL2
from nb >= 1000 it gets many fold better than IndexFlatL2
However the Index train time is a trade of for this usecase which ranges from 10's of ms to 100's of ms

Please refer to similarity_search.log in experiments for results
"""

class FaissIndexes:
    def __init__(self, dim = 512, distance_type = faiss.METRIC_INNER_PRODUCT):
        '''
        Distance Type: faiss.METRIC_INNER_PRODUCT for cosine similarity
                       faiss.METRIC_L2 for euclidean distance
        '''
        self.groupIndex = {}
        self.dim = dim
        self.distance_type = distance_type
        logger.info("New Search instance at: {}".format(time.time()))

    def trainGroupIndex(self, groupName, faceEmbeds):
        self.groupIndex[groupName] = self.indexFlatL2IP(embeds=faceEmbeds)
        return True

    def loadGroupIndex(self, groupFeatures):
        for groupName in groupFeatures[CoreConfig.groups]:
            self.trainGroupIndex(
                groupName=groupName,
                faceEmbeds=groupFeatures[groupName + CoreConfig.grp_embeds],
            )
        return True

    def indexFlatL2IP(self, embeds):
        '''
        # IP for cosine similarity
        # L2 for euclidean distance
        '''
        if self.distance_type == faiss.METRIC_L2:
            indexflatl2IP = faiss.IndexFlatL2(self.dim) 
        else:
            indexflatl2IP = faiss.IndexFlatIP(self.dim)  # build the index
        #  
        t10 = time.time()
        indexflatl2IP.add(embeds)
        t11 = time.time()  # add vectors to the index
        print(
            "IndexFlatL2 train timing: {},\nTrained: {}\nTotal: {}".format(
                (t11 - t10), indexflatl2IP.is_trained, indexflatl2IP.ntotal
            )
        )
        logger.info("IndexFlatL2 train timing: {}".format(t11 - t10))
        return indexflatl2IP

    def indexIVFFlat(self, embeds, nlist=1, nprobe=1):
        quantizer = faiss.IndexFlatL2(self.dim)  # the other index
        indexivfflat = faiss.IndexIVFFlat(
            quantizer, self.dim, nlist, faiss.METRIC_L2
        )
        t20 = time.time()
        assert not indexivfflat.is_trained
        indexivfflat.train(embeds)
        assert indexivfflat.is_trained
        indexivfflat.add(embeds)
        t21 = time.time()
        indexivfflat.nprobe = nprobe
        print(
            "IndexIVFFlat train timing: {},\nTrained: {}\nTotal: {}".format(
                (t21 - t20), indexivfflat.is_trained, indexivfflat.ntotal
            )
        )
        logger.info("IndexIVFFlat train timing: {}".format(t21 - t20))
        return indexivfflat

    def knnL2sqrHeap(self, neighbours=1, nq=1 ):
        t1s = time.time()  # add vectors to the index
        self.D = np.empty((nq, neighbours), dtype="float32")
        self.I = np.empty((nq, neighbours), dtype="int64")
        if self.distance_type == faiss.METRIC_L2:
            self.heaps = faiss.float_maxheap_array_t()
        else:
            self.heaps = faiss.float_minheap_array_t()
        self.heaps.k = neighbours
        self.heaps.nh = nq
        self.heaps.val = faiss.swig_ptr(self.D)
        self.heaps.ids = faiss.swig_ptr(self.I)
        t1e = time.time()  # add vectors to the index
        logger.info("Heap initiation for InMem search complete!")
        print("Heap Init Time: {}".format(t1e-t1s))
        
    def embedSearchIndex(self, groupName, queryVec, neighbours=1):
        try:
            return self.groupIndex[groupName].search(queryVec, neighbours)
        except:
            return (np.zeros((queryVec.shape[0],1)),np.zeros((queryVec.shape[0],1)))

    def embedSearchNoIndex(self, queryVecs, embed):
        D,I = np.array([]), np.array([])
        # D,I = [],[]
        for queryVec in queryVecs:
            queryVec = queryVec.reshape(1,-1)
            if self.distance_type == faiss.METRIC_L2:
                faiss.knn_L2sqr(
                    faiss.swig_ptr(queryVec),
                    faiss.swig_ptr(embed),
                    self.dim,
                    queryVec.shape[0],
                    embed.shape[0],
                    self.heaps,
                )
            else:
                faiss.knn_inner_product(
                    faiss.swig_ptr(queryVec),
                    faiss.swig_ptr(embed),
                    self.dim,
                    queryVec.shape[0],
                    embed.shape[0],
                    self.heaps,
                )
            if D.any():
                D = np.vstack((D,self.D))
                I = np.vstack((I,self.I))
            else:
                D = np.copy(self.D)
                I = np.copy(self.I)
        return (D,I)
    
    def embedSearchCosine(self, queryVecs, embed):
        D = np.inner(queryVecs,embed)
        return (D,"")