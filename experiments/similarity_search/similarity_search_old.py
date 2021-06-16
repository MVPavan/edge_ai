# https://stackoverflow.com/questions/37794849/efficient-and-precise-calculation-of-the-euclidean-distance
# https://semantive.com/blog/high-performance-computation-in-python-numpy-2/
# Efficiency Test Script:
import numpy as np
from scipy.spatial import distance
from sklearn.metrics.pairwise import euclidean_distances
import math
import copy
import faiss  # make faiss available
import time
import timeit
from loguru import logger

logger.add("similarity_search.log")

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


def v2Iterator(func):
    def inner1(*args, **kwargs):
        begin = time.time()
        [
            func(args[0], args[1][i].reshape(1, -1), **kwargs)
            for i in range(args[1].shape[0])
        ]
        end = time.time()
        print("Interanl loop time:", func.__name__, end - begin)

    return inner1


# 1
# @v2Iterator
def eudis1(v1, v2):
    return np.linalg.norm(v1 - v2, axis=1)


# 2
def eudis2(v1, v2):
    return list(map(lambda vk: distance.euclidean(vk, v2), iter(v1)))


# 3
def eudis3(v1, v2):
    return euclidean_distances(v1, v2.reshape(1, -1))


# 4
def eudis4(v1, v2):
    return np.sum((v1 - v2) ** 2, axis=1)


# 5
def eudis5(v1, v2):
    dist = [(a - v2) ** 2 for a in v1]
    dist = [math.sqrt(b) for b in [sum(a) for a in dist]]
    return dist


# 6
def eudis6(v1, v2):
    z = v1 - v2
    return np.einsum("ij,ij->ij", z, z)


I1, D1 = [], []


def eudis7(v1, v2, k):
    global I1, D1
    ################ Train Phase ########################################
    # indexflatl2 = faiss.IndexFlatL2(d)   # build the index
    # indexflatl2.add(v1)
    #######################################################################
    Dt, It = indexflatl2.search(v2, k)
    # Dt,It= v1.search(v2, k)
    return (I1.append(It), D1.append(Dt))


I2, D2 = [], []


def eudis8(v1, v2, k):
    global I2, D2
    ################ Train Phase ########################################
    # quantizer = faiss.IndexFlatL2(d)  # the other index
    # indexivfflat = faiss.IndexIVFFlat(quantizer, d, nlist, faiss.METRIC_L2)
    # assert not indexivfflat.is_trained
    # indexivfflat.train(v1)
    # assert indexivfflat.is_trained
    # indexivfflat.add(v1)
    # indexivfflat.nprobe = nprobe
    #######################################################################
    Dt, It = indexivfflat.search(v2, k)
    # Dt,It= v1.search(v2, k)
    return (I2.append(It), D2.append(Dt))


def eudis9(v1, v2):
    # I3 = np.empty((nq, k), dtype='int64')
    # D3 = np.empty((nq, k), dtype='float32')
    # heaps = faiss.float_maxheap_array_t()
    # heaps.k = k
    # heaps.nh = nq
    # heaps.val = faiss.swig_ptr(D3)
    heaps.ids = faiss.swig_ptr(I3)
    return faiss.knn_L2sqr(faiss.swig_ptr(v2), faiss.swig_ptr(v1), d, nq, nb, heaps)


# v1 = np.load("/home/pavanmv/Pavan/study/stack_embeds.npy",allow_pickle=True)
v1 = np.load("/home/pavanmv/Pavan/study/embeds_98639.npy", allow_pickle=True)
# v1 = v[np.random.choice(v.shape[0], 10000, replace=False)]
eid_list = np.load("/home/pavanmv/Pavan/study/eid_98639.npy", allow_pickle=True)


d = 512  # dimension
k = 1
nq = 1
nb = v1.shape[0]
nlist = 1000
nprobe = 1

v_index_random = np.random.choice(v1.shape[0], nq, replace=False)
v2t = v1[v_index_random]

############################################################################################################################
indexflatl2 = faiss.IndexFlatL2(d)  # build the index
t10 = time.time()
indexflatl2.add(v1)
t11 = time.time()  # add vectors to the index
print(
    "IndexFlatL2 create timing: {},\nTrained: {}\nTotal: {}".format(
        (t11 - t10), indexflatl2.is_trained, indexflatl2.ntotal
    )
)
############################################################################################################################
quantizer = faiss.IndexFlatL2(d)  # the other index
indexivfflat = faiss.IndexIVFFlat(quantizer, d, nlist, faiss.METRIC_L2)
# here we specify METRIC_L2, by default it performs inner-product search
t20 = time.time()
assert not indexivfflat.is_trained
indexivfflat.train(v1)
# indexivfflat.train()
assert indexivfflat.is_trained
# indexivfflat.add_with_ids(v1,eid_list)
indexivfflat.add(v1)
t21 = time.time()
indexivfflat.nprobe = nprobe
print(
    "IndexIVFFlat create timing: {},\nTrained: {}\nTotal: {}".format(
        (t21 - t20), indexivfflat.is_trained, indexivfflat.ntotal
    )
)
# ############################################################################################################################
# indexflatip = faiss.IndexFlatIP(d)   # build the index
# t30=time.time()
# indexflatip.add(v)
# t31=time.time()                # add vectors to the index
# print("IndexFlatIP create timing: {},\nTrained: {}\nTotal: {}".format((t31-t30),indexflatip.is_trained,indexflatip.ntotal))
############################################################################################################################
# n_bits = 2 * d
# lsh = faiss.IndexLSH (d, n_bits)
# lsh.train (x_train)
# lsh.add (x_base)
# print("lsh create timing: {},\nTrained: {}\nTotal: {}".format((t11-t01),lsh.is_trained,lsh.ntotal))
############################################################################################################################
I3 = np.empty((nq, k), dtype="int64")
D3 = np.empty((nq, k), dtype="float32")
heaps = faiss.float_maxheap_array_t()
heaps.k = k
heaps.nh = nq
heaps.val = faiss.swig_ptr(D3)
heaps.ids = faiss.swig_ptr(I3)
############################################################################################################################


def wrapper(func, *args, **kwargs):
    def wrapped():
        return func(*args, **kwargs)

    return wrapped


number = 10

############################################################################################################################

wrappered7 = wrapper(eudis7, indexflatl2, v2t, k)
# wrappered7 = wrapper(eudis7, v1, v2t, k)
t7 = timeit.repeat(wrappered7, repeat=5, number=number)
print("t7: ", sum(t7) / (len(t7) * number))

wrappered8 = wrapper(eudis8, indexivfflat, v2t, k)
# wrappered8 = wrapper(eudis8, v1, v2t, k)
t8 = timeit.repeat(wrappered8, repeat=5, number=number)
print("t8: ", sum(t8) / (len(t8) * number))

wrappered9 = wrapper(eudis9, v1, v2t)
t9 = timeit.repeat(wrappered9, repeat=5, number=number)
print("t9: ", sum(t9) / (len(t9) * number))

# t1,t2,t3,t4,t5,t6 = np.array([[],[],[],[],[],[]])
# for i in range(v2t.shape[0]):
#     v2 = v2t[i].reshape(1,-1)
#     # wrappered1 = wrapper(eudis1, v1, v2)
#     # wrappered2 = wrapper(eudis2, v1, v2)
#     # wrappered3 = wrapper(eudis3, v1, v2)
#     wrappered4 = wrapper(eudis4, v1, v2)
#     # wrappered5 = wrapper(eudis5, v1, v2)
#     # wrappered6 = wrapper(eudis6, v1, v2)

#     if any(t1):
#         t1=np.add(t1,timeit.repeat(wrappered4, repeat=3, number=number))
#     else:
#         t1 = timeit.repeat(wrappered4, repeat=3, number=number)
#     # # t2 = timeit.repeat(wrappered2, repeat=3, number=number)
#     # # print('t2: ', sum(t2)/len(t2))
#     # # t3 = timeit.repeat(wrappered3, repeat=3, number=number)
#     # # print('t3: ', sum(t3)/len(t3))
#     if any(t4):
#         t4=np.add(t4,timeit.repeat(wrappered4, repeat=3, number=number))
#     else:
#         t4 = timeit.repeat(wrappered4, repeat=3, number=number)
#     # # t5 = timeit.repeat(wrappered5, repeat=3, number=number)
#     # # print('t5: ', sum(t5)/len(t5))
#     if any(t6):
#         t6=np.add(t6,timeit.repeat(wrappered4, repeat=3, number=number))
#     else:
#         t6 = timeit.repeat(wrappered4, repeat=3, number=number)
#     # print(t1,"\n",t4,"\n",t6)


# print('t1: ', sum(t1)/(len(t1)*number))
# print('t4: ', sum(t4)/(len(t4)*number))
# print('t6: ', sum(t6)/(len(t6)*number))

print(I2[0], I1[0])
assert I2[0] == I1[0]
print("wow")

logger.info("New run instance at: {}".format(time.time()))
logger.info(
    "d:{},k:{},nb:{},nq:{},nlist: {},nprobe: {}".format(d, k, nb, nq, nlist, nprobe)
)
# logger.info("IndexFlatL2 create timing: {},\nTrained: {}\nTotal: {}"\
#     .format((t11-t10),indexflatl2.is_trained,indexflatl2.ntotal))
# logger.info("IndexIVFFlat create timing: {},\nnlist: {},\nnprobe: {},\nTrained: {}\nTotal: {}"\
#     .format((t21-t20),nlist, nprobe, indexivfflat.is_trained,indexivfflat.ntotal))
logger.info("indexflatl2 Train_search:{}".format(sum(t7) / (len(t7) * number)))
logger.info("indexivfflat Train_search:{}".format(sum(t8) / (len(t8) * number)))
logger.info("knn_L2sqr Train_search:{}".format(sum(t9) / (len(t9) * number)))
