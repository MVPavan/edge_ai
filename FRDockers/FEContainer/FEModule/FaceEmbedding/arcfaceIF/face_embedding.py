from pathlib import Path
import cv2
import mxnet as mx
import numpy as np
from sklearn import preprocessing as sklearn_preprocessing

from FRCommon.fr_config import FEConfig, CoreConfig
from .face_preprocess import preprocess


def do_flip(data):
    for idx in range(data.shape[0]):
        data[idx, :, :] = np.fliplr(data[idx, :, :])


def getIFModel(ctx, image_size, prefix, epoch, layer):
    print("AFIF model loading ....", prefix, epoch)
    sym, arg_params, aux_params = mx.model.load_checkpoint(prefix, epoch)
    all_layers = sym.get_internals()
    sym = all_layers[layer + "_output"]
    model = mx.mod.Module(symbol=sym, context=ctx, label_names=None)
    # model.bind(data_shapes=[('data', (args.batch_size, 3, image_size[0], image_size[1]))], label_shapes=[('softmax_label', (args.batch_size,))])
    model.bind(data_shapes=[("data", (1, 3, image_size[0], image_size[1]))])
    model.set_params(arg_params, aux_params)
    return model


class FaceEmbedding:
    def __init__(self):
        """
        AFIF model to generate embeddings from aligned face images
        """
        model_prefix = (Path(FEConfig.FR_AFIF_MXNET_WEIGHTS) / "model").as_posix()
        if CoreConfig.GPU_DEVICE >= 0:
            ctx = mx.gpu(CoreConfig.GPU_DEVICE)
        else:
            ctx = mx.cpu()
        self.model = getIFModel(
            ctx=ctx,
            image_size=FEConfig.FR_IMAGE_SIZE,
            prefix=model_prefix,
            epoch=0,
            layer="fc1",
        )

    def faceAlign(self, face_img, bbox_list=[], landmarks_list=[]):
        """
        input: Image, bounding boxes, landmarks
        output: cropped/Aligned and preprocessed
        """
        faces_list = []
        bbox_list_conf = []
        face_counter = 0
        for bbox_ in bbox_list:
            if bbox_[4] > FEConfig.FD_CONFIDENCE_THRESHOLD:
                bbox = bbox_[0:4]
                landmarks = landmarks_list[face_counter - 1, :].reshape((2, 5)).T
                nimg = preprocess(
                    img=face_img,
                    bbox=bbox,
                    landmark=landmarks,
                    image_size=FEConfig.FR_IMAGE_SIZE,
                )
                nimg = cv2.cvtColor(nimg, cv2.COLOR_BGR2RGB)
                aligned_face = np.transpose(nimg, (2, 0, 1))
                faces_list.append(aligned_face)
                bbox_list_conf.append(bbox_)
            face_counter += 1
        return (faces_list, bbox_list_conf)

    def getEmbedding(self, aligned_face):
        """
        Perform Face Detection and Alignment before passing to this function.
        input: aligned_face & cropped/resize face image
        output: AFIF embedding
        """
        embedding = None
        for flipid in [0, 1]:
            if flipid == 1:
                if FEConfig.FR_FLIP == 0:
                    break
                do_flip(aligned_face)
            if len(aligned_face.shape)==4:
                input_blob = aligned_face  
            elif len(aligned_face.shape)==3:
                input_blob = np.expand_dims(aligned_face, axis=0)
            data = mx.nd.array(input_blob)
            db = mx.io.DataBatch(data=(data,))
            # print("here",db.shape)
            self.model.forward(db, is_train=False)
            _embedding = self.model.get_outputs()[0].asnumpy()
            if embedding is None:
                embedding = _embedding
            else:
                embedding += _embedding
                embedding = embedding / 2
        embedding = sklearn_preprocessing.normalize(embedding)
        # embedding = sklearn_preprocessing.normalize(embedding).flatten()
        return embedding
