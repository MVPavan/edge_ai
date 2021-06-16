# https://stackoverflow.com/questions/37794849/efficient-and-precise-calculation-of-the-euclidean-distance
# https://semantive.com/blog/high-performance-computation-in-python-numpy-2/
# Efficiency Test Script:
import numpy as np
from numpy.linalg import norm
from scipy.spatial import distance
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.preprocessing import normalize
import math
import copy
import faiss  # make faiss available
import time, sys
import timeit
from loguru import logger
# from memory_profiler import profile as mprofile

# from memory_profiler import LogFile as mLogFile
logger.add("similarity_search_time.log")
mf = open("similarity_search_memory.log", "w+")
# sys.stdout = mLogFile("similarity_search_memory.log")
"""
Conclusions of the Experiment:
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

Please refer to similarity_search.log for results
"""

# v1 = np.load("/home/pavanmv/Pavan/study/stack_embeds.npy",allow_pickle=True)
d, k, nq, nb, nlist, nprobe = [512, 3, 10, 10000, 100, 1]
v = np.load("/home/pavanmv/Pavan/study/embeds_98639.npy", allow_pickle=True)
eid_list = np.load("/home/pavanmv/Pavan/study/eid_98639.npy", allow_pickle=True)
v_index_random = np.random.choice(v.shape[0], nb, replace=False)
v1 = normalize((v[v_index_random]))
e1 = eid_list[v_index_random]
v_query_random = np.random.choice(v1.shape[0], nq, replace=False)
v2t = normalize(v1[v_query_random])
number, repeat = 10, 5


def wrapper(func, *args, **kwargs):
    def wrapped():
        return func(*args, **kwargs)

    return wrapped


class SimilarityFuncs:
    def __init__(self,):
        self.I1, self.D1 = [], []
        self.I2, self.D2 = [], []

    # 1
    def eudis1(self, v1, v2):
        return np.linalg.norm(v1 - v2, axis=1)

    # 2
    def eudis2(self, v1, v2):
        return list(map(lambda vk: distance.euclidean(vk, v2), iter(v1)))

    # 3
    def eudis3(self, v1, v2):
        return euclidean_distances(v1, v2.reshape(1, -1))

    # 4
    def eudis4(self, v1, v2):
        return np.sum((v1 - v2) ** 2, axis=1)

    # 5
    def eudis5(self, v1, v2):
        dist = [(a - v2) ** 2 for a in v1]
        dist = [math.sqrt(b) for b in [sum(a) for a in dist]]
        return dist

    # 6
    def eudis6(self, v1, v2):
        z = v1 - v2
        return np.einsum("ij,ij->ij", z, z)

    # 7
    def eudis7(self, v1, v2, k):
        ################ Train Phase ########################################
        # indexflatl2 = faiss.IndexFlatL2(d)   # build the index
        # indexflatl2.add(v1)
        #######################################################################
        # Dt,It= indexflatl2.search(v2, k)
        Dt, It = v1.search(v2, k)
        return (self.I1.append(It), self.D1.append(Dt))
        # It[Dt[:,0]<1,0]

    # 8
    def eudis8(self, v1, v2, k):
        ################ Train Phase ########################################
        # quantizer = faiss.IndexFlatL2(d)  # the other index
        # indexivfflat = faiss.IndexIVFFlat(quantizer, d, nlist, faiss.METRIC_L2)
        # assert not indexivfflat.is_trained
        # indexivfflat.train(v1)
        # assert indexivfflat.is_trained
        # indexivfflat.add(v1)
        # indexivfflat.nprobe = nprobe
        #######################################################################
        # Dt,It= indexivfflat.search(v2, k)
        Dt, It = v1.search(v2, k)
        return (self.I2.append(It), self.D2.append(Dt))

    # 9
    def eudis9(self, v1, v2, heaps):
        # I3 = np.empty((nq, k), dtype='int64')
        # D3 = np.empty((nq, k), dtype='float32')
        # heaps = faiss.float_maxheap_array_t()
        # heaps.k = k
        # heaps.nh = nq
        # heaps.val = faiss.swig_ptr(D3)
        # heaps.ids = faiss.swig_ptr(I3)
        return faiss.knn_inner_product(
            faiss.swig_ptr(v2), faiss.swig_ptr(v1), d, v2.shape[0], v1.shape[0], heaps
        )
        # return faiss.knn_L2sqr(
        #     faiss.swig_ptr(v2), faiss.swig_ptr(v1), d, v2.shape[0], v1.shape[0], heaps
        # )

    def eudis10(self, v1, v2):
        print("wow")
        np.inner(v1, v2) / (norm(v1) * norm(v2))


class FaissIndexes:
    def __init__(self):
        logger.info("New run instance at: {}".format(time.time()))
        logger.info(
            "d:{},k:{},nb:{},nq:{},nlist: {},nprobe: {}".format(
                d, k, nb, nq, nlist, nprobe
            )
        )

    def indexFlatL2(self,):
        self.indexflatl2 = faiss.IndexFlatIP(d)  # build the index
        # self.indexflatl2 = faiss.IndexFlatL2(d)  # build the index
        # self.indexflatl2.mapID
        t10 = time.time()
        self.indexflatl2.add(v1)
        t11 = time.time()  # add vectors to the index
        print(
            "IndexFlatL2 train timing: {},\nTrained: {}\nTotal: {}".format(
                (t11 - t10), self.indexflatl2.is_trained, self.indexflatl2.ntotal
            )
        )
        logger.info("IndexFlatL2 train timing: {}".format(t11 - t10))

    def indexIVFFlat(self,):
        quantizer = faiss.IndexFlatIP(d)  # the other index
        # quantizer = faiss.IndexFlatL2(d)  # the other index
        self.indexivfflat = faiss.IndexIVFFlat(quantizer, d, nlist)#, faiss.METRIC_L2)
        # here we specify METRIC_L2, by default it performs inner-product search
        t20 = time.time()
        assert not self.indexivfflat.is_trained
        self.indexivfflat.train(v1)
        # indexivfflat.train()
        assert self.indexivfflat.is_trained
        self.indexivfflat.add(v1)
        t21 = time.time()
        self.indexivfflat.nprobe = nprobe
        print(
            "IndexIVFFlat train timing: {},\nTrained: {}\nTotal: {}".format(
                (t21 - t20), self.indexivfflat.is_trained, self.indexivfflat.ntotal
            )
        )
        logger.info("IndexIVFFlat train timing: {}".format(t21 - t20))

    def knn_L2sqr(self,):
        self.I3 = np.empty((nq, k), dtype="int64")
        self.D3 = np.empty((nq, k), dtype="float32")
        # self.heaps = faiss.float_maxheap_array_t()
        self.heaps = faiss.float_minheap_array_t()
        self.heaps.k = k
        self.heaps.nh = nq
        self.heaps.val = faiss.swig_ptr(self.D3)
        self.heaps.ids = faiss.swig_ptr(self.I3)


class SimProfiler:
    def __init__(self,):
        self._faiss = FaissIndexes()
        self.simFuncs = SimilarityFuncs()

    def indexFlatL2Perf(self):
        self._faiss.indexFlatL2()
        wrappered7 = wrapper(self.simFuncs.eudis7, self._faiss.indexflatl2, v2t, k)
        # wrappered7 = wrapper(eudis7, v1, v2t, k)
        t7 = timeit.repeat(wrappered7, repeat=repeat, number=number)
        print("t7: ", sum(t7) / (len(t7) * number))
        logger.info(
            "indexflatl2 index serach time:{}".format(sum(t7) / (len(t7) * number))
        )

    def indexIVFFlatPerf(self):
        self._faiss.indexIVFFlat()
        wrappered8 = wrapper(self.simFuncs.eudis8, self._faiss.indexivfflat, v2t, k)
        # wrappered8 = wrapper(eudis8, v1, v2t, k)
        t8 = timeit.repeat(wrappered8, repeat=repeat, number=number)
        print("t8: ", sum(t8) / (len(t8) * number))
        logger.info(
            "indexivfflat index serach time:{}".format(sum(t8) / (len(t8) * number))
        )

    def knn_L2sqrPerf(self):
        self._faiss.knn_L2sqr()
        wrappered9 = wrapper(self.simFuncs.eudis9, v1, v2t, self._faiss.heaps)
        t9 = timeit.repeat(wrappered9, repeat=repeat, number=number)
        print("t9: ", sum(t9) / (len(t9) * number))
        logger.info(
            "knn_L2sqr index serach time:{}".format(sum(t9) / (len(t9) * number))
        )

    def npcosineSimPerf(self):
        wrappered6 = wrapper(self.simFuncs.eudis10, v1, v2t)
        # wrappered8 = wrapper(eudis8, v1, v2t, k)
        t8 = timeit.repeat(wrappered6, repeat=repeat, number=number)
        print("t8: ", sum(t8) / (len(t8) * number))
        logger.info(
            "indexivfflat index serach time:{}".format(sum(t8) / (len(t8) * number))
        )


    # @mprofile(stream=mf)
    def calcPerformance(self):
        self.indexFlatL2Perf()
        self.indexIVFFlatPerf()
        self.knn_L2sqrPerf()
        print(self.simFuncs.I2[0], self.simFuncs.I1[0], self._faiss.I3[0])
        assert self.simFuncs.I2[0] == self.simFuncs.I1[0]
        tt = time.time()
        k = e1[self.simFuncs.I1[0][0][0]]
        print(k[0], time.time() - tt)
        print("........... Performace calc Completed ....................")


if __name__ == "__main__":
    SimProfiler().calcPerformance()
