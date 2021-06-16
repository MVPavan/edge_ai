import time
import math
import os
import sys
import os.path
from os import path
from datetime import timedelta
import argparse
import pickle
import cv2
import numpy as np
from sklearn import neighbors

# import everai
# import face_recognition
# from mtcnn.mtcnn import MTCNN
from threading import Thread
from Modular_code import partage

sys.path.append(os.path.join(os.path.dirname(__file__), "IF", "deploy"))
import face_model


class EmbedGen:
    def ImageFilesList(self, person_dir_path):
        person_image_path_list = []
        if os.path.isdir(person_dir_path):
            person_image_path_list = partage.image_files_in_folder(person_dir_path)

        return person_image_path_list

    def EmbeddingGenerator(self, model, person_image_path_list, verbose=True):
        [nimg, embedding] = [0, []]
        face_count = 0
        bad_faces = 0
        # print("came for the embedding")
        for img_path in person_image_path_list:
            try:
                img = cv2.imread(img_path)
                img = cv2.flip(img, 1)

            except:
                partage.logger.info("error in reading {}".format(img_path))
                print("error in reading {}".format(img_path))
                return

            [Face_list, face_bounding_boxes] = [[], []]
            [Face_list, face_bounding_boxes] = model.get_input(img)
            if len(face_bounding_boxes) != 1:
                if verbose:
                    print(
                        "Image {} not suitable for training: {}".format(
                            img_path,
                            "Didn't find a face"
                            if len(face_bounding_boxes) < 1
                            else "Found more than one face",
                        )
                    )
                    bad_faces = bad_faces + 1
            else:
                fv = []
                try:
                    fv = model.get_feature(Face_list[0])
                    nimg = nimg + 1
                    face_count = face_count + 1

                except:
                    print("error while generating the embedding!!!")
                    sys.exit()

                if nimg == 1:
                    embedding = fv
                else:
                    embedding = embedding + fv

        if nimg > 1:
            embedding = embedding / nimg
        # print("returned the embedding")
        return embedding


class MTCNN_FN_FR:
    def __init__(self, model_path):
        self.detector = MTCNN(min_face_size=150, steps_threshold=[0.6, 0.7, 0.8])
        # dir_path = os.path.dirname(os.path.realpath(__file__))
        cwd = os.getcwd()
        # self.db_path = cwd+"/DB/train/eid_db/"
        self.db_path = cwd + "/DB/train/12n/upload/"
        # /home/honeywell/SLM/FR_DA/DB/train/12n/upload
        with open(model_path, "rb") as f:
            self.knn_clf = pickle.load(f)

    def detect_faces_MTCNN(self, frame):
        faces = []
        bbox_pred = []
        faces = self.detector.detect_faces(frame)
        if faces != []:
            bbox_pred = [("unknown", face["box"]) for face in faces]
        return bbox_pred

    def MTCNN_FN_Recognition(self, frame, match, nb=1, distance_threshold=0.5, resf=1):
        face_available = False
        result = []
        face_encodings = []
        face_locations = []
        predictions = []
        ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}
        rgb_frame = frame
        result = self.detector.detect_faces(rgb_frame)
        face_locations_o = []
        if result != []:
            face_available = True
            for face in result:
                box = face["box"]
                face_locations_o.append(
                    [box[1], box[0] + box[2], box[1] + box[3], box[0]]
                )

            face_locations = [tuple(int(t / resf) for t in x) for x in face_locations_o]
            face_encodings = face_recognition.face_encodings(
                frame, face_locations
            )  # ,model="small")

        else:
            face_locations = []
            face_encodings = []

        if not match[0]:
            if len(face_locations) != 0:
                closest_distances = self.knn_clf.kneighbors(
                    face_encodings, n_neighbors=nb
                )
                # print("closest distances are:{}".format(closest_distances))
                are_matches = [
                    closest_distances[0][i][0] <= distance_threshold
                    for i in range(len(face_locations))
                ]
                predictions = [
                    (pred, loc) if rec else ("unknown", loc)
                    for pred, loc, rec in zip(
                        self.knn_clf.predict(face_encodings),
                        face_locations,
                        are_matches,
                    )
                ]
                # print("prediction for the face are:")

                face_available = True
            else:
                face_available = False
            return (face_available, predictions)

        elif match[0]:
            # print("inside 1:1 loop")
            if len(face_locations) != 0:
                fv_path = (
                    self.db_path
                    + str(match[1]).lower()
                    + "/"
                    + str(match[1]).lower()
                    + ".npy"
                )
                if not path.exists(fv_path):
                    print(
                        "user facial vector is not available!! checking for user picture in Date base ...."
                    )
                    [user_pic_available, image] = [False, []]
                    for tail in ALLOWED_EXTENSIONS:
                        img_path = (
                            self.db_path
                            + str(match[1]).lower()
                            + "/"
                            + str(match[1]).lower()
                            + tail
                        )
                        print("Image path is:{}".format(img_path))
                        if path.exists(img_path):
                            try:
                                image = face_recognition.load_image_file(img_path)
                                user_pic_available = True
                                break
                            except:
                                partage.logger.info(
                                    "error in reading {}".format(img_path)
                                )
                                print("error in reading {}".format(img_path))

                    if not user_pic_available:
                        print("user picture is not availbale in db!!")
                        partage.logger.info(
                            f"No picture available with eid : {match[1]}"
                        )
                        return (False, [])
                    else:
                        # image = face_recognition.load_image_file(img_path)
                        print(
                            f"facial vector for {match[1]} is not available, a new one is being generated!"
                        )
                        partage.logger.info(f"Facial vector generated for {match[1]}")
                        reference_encoding = face_recognition.face_encodings(
                            image, num_jitters=100
                        )
                        print(reference_encoding)
                        x_ = np.array(reference_encoding[0])
                        np.save(
                            self.db_path
                            + str(match[1]).lower()
                            + "/"
                            + str(match[1]).lower()
                            + ".npy",
                            x_,
                        )

                reference_encoding = np.load(fv_path)
                reference_encoding = np.array(reference_encoding.tolist())
                match_result = face_recognition.compare_faces(
                    face_encodings, reference_encoding, match[2]
                )
                predictions = [
                    (match[1], loc) if rec else ("unknown", loc)
                    for loc, rec in zip(face_locations, match_result)
                ]
                face_available = True
            else:
                face_available = False
            return (face_available, predictions)


class EverAi_FR:
    def __init__(self, model_path):
        self.session = everai.Session()
        cwd = os.getcwd()
        self.db_path = cwd + "/DB/train/12n/upload/"
        with open(model_path, "rb") as f:
            self.knn_clf = pickle.load(f)

    def EAI_Recognition(self, frame, match, nb=1, distance_threshold=1, resf=1):
        face_available = False
        result = []
        face_encodings = []
        face_locations = []
        predictions = []

        # modified_frame = cv2.resize(frame, (0, 0), fx=resf, fy=resf)
        rgb_frame = frame
        result = self.session.compute_embeddings(rgb_frame)
        face_locations_o = []
        if result[1] != -1:
            for face in result[0]:
                box = face.bounding_box
                face_locations_o.append(
                    [
                        box.top_left.y,
                        box.bottom_right.x,
                        box.bottom_right.y,
                        box.top_left.x,
                    ]
                )
                face_encodings.append(face.embedding)
            face_locations = [tuple(int(t / resf) for t in x) for x in face_locations_o]
            face_encodings = np.array(face_encodings)
        else:
            face_locations = []
            face_encodings = []

        if not match[0]:
            if len(face_locations) != 0:
                closest_distances = self.knn_clf.kneighbors(
                    face_encodings, n_neighbors=nb
                )
                are_matches = [
                    closest_distances[0][i][0] <= distance_threshold
                    for i in range(len(face_locations))
                ]
                predictions = [
                    (pred, loc) if rec else ("unknown", loc)
                    for pred, loc, rec in zip(
                        self.knn_clf.predict(face_encodings),
                        face_locations,
                        are_matches,
                    )
                ]
                face_available = True
            else:
                face_available = False

        elif match[0]:
            if len(face_locations) != 0:
                img_path = (
                    self.db_path
                    + str(match[1]).lower()
                    + "/"
                    + str(match[1]).lower()
                    + ".jpg"
                )
                if not path.exists(img_path):
                    print("user picture is not availbale in db!!")
                    partage.logger.info(f"No picture available with eid : {match[1]}")
                    return (False, [])
                image = face_recognition.load_image_file(img_path)
                result_ = self.session.compute_embeddings(image)
                if result[1] != -1:
                    match_var = []
                    for face in result[0]:
                        dis = np.sum((face.embedding - result_[0][0].embedding) ** 2)
                        match_var.append(dis < 0.8)

                predictions = [
                    (match[1], loc) if rec else ("unknown", loc)
                    for loc, rec in zip(face_locations, match_var)
                ]
                face_available = True
            else:
                face_available = False
            return (face_available, predictions)

        return (face_available, predictions)


class MTCNN_IF_FR:
    def __init__(self, model_path, db_path, args):
        self.model = face_model.FaceModel(args)
        # self.detector  = MTCNN(min_face_size=150, steps_threshold=[0.6,0.7,0.8])
        # dir_path = os.path.dirname(os.path.realpath(__file__))
        cwd = os.getcwd()
        # self.db_path = cwd+"/DB/train/eid_db/"
        self.db_path = db_path
        self.model_path = model_path
        self.KNN_oldctime = os.path.getmtime(self.model_path)
        # self.db_path = cwd+"/DB/train/12n/upload/"
        # /home/honeywell/SLM/FR_DA/DB/train/12n/upload
        print("opening pickle")
        with open(self.model_path, "rb") as f:
            self.knn_clf = pickle.load(f)
        print("opened pickle successfully")

    def KNN_Reload(self,):
        if os.path.getmtime(self.model_path) > self.KNN_oldctime:
            with open(self.model_path, "rb") as f:
                self.knn_clf = pickle.load(f)
            self.KNN_oldctime = os.path.getmtime(self.model_path)
            print("KNN reloaded successfully")

    def detect_faces_MTCNN(self, frame):
        bbox_list = []
        bbox_pred = []
        [bbox_list, *_] = self.model.IF_detect_face(frame)
        if bbox_list != []:
            bbox_pred = [("unkown", bbox) for bbox in bbox_list]
        return bbox_pred

    def MTCNN_IF_Recognition(self, frame, match, nb=1, distance_threshold=0.9, resf=1):
        face_available = False
        face_encodings = []
        face_locations = []
        predictions = []

        frame = cv2.flip(frame, 1)
        # ret = self.model.IF_detect_face(frame)
        [Face_list, bbox_list] = self.model.get_input(frame)
        face_locations_o = []
        face_counter = 0
        if len(bbox_list) >= 1:
            face_available = True
            for face in Face_list:
                face_counter = face_counter + 1
                f1 = self.model.get_feature(face)
                box = bbox_list[face_counter - 1][0:4]
                # print(box)
                face_locations_o.append([box[0], box[1], box[2], box[3]])
                face_encodings.append(f1)
            # print('got all feature vectors')
            face_locations = [tuple(int(t / resf) for t in x) for x in face_locations_o]
        else:
            face_locations = []
            face_encodings = []

        if not match[0]:
            self.KNN_Reload()
            if len(face_locations) != 0:
                closest_distances = self.knn_clf.kneighbors(
                    face_encodings, n_neighbors=nb
                )
                are_matches = [
                    closest_distances[0][i][0] <= distance_threshold
                    for i in range(len(face_locations))
                ]
                predictions = [
                    (pred, loc) if rec else ("unknown", loc)
                    for pred, loc, rec in zip(
                        self.knn_clf.predict(face_encodings),
                        face_locations,
                        are_matches,
                    )
                ]
                # print("closest distances are:{}".format([self.knn_clf.predict(face_encodings), closest_distances[0]]))
                # print("predictions FR: ", predictions)
                face_available = True
            else:
                face_available = False
            return (face_available, predictions)

        elif match[
            0
        ]:  # match - [True - 121 else 12n, eid, FN - threshold,[hid,card_id,key,mask,enrolled,name]]
            # print("121 using Insight Face!")
            [hid, _, _, _, _, uname] = match[3]
            eid = match[1]
            user_folder = "{}_{}_{}".format(eid, hid, uname)
            user_folder_path = os.path.join(self.db_path, user_folder)
            if len(face_locations) != 0:
                fv_path = os.path.join(user_folder_path, "{}_IF.npy".format(eid))
                if not path.exists(fv_path):
                    print(
                        "user facial vector is not available!! checking for user picture in Date base ...."
                    )
                    fvgen = EmbedGen()
                    img_path_list = fvgen.ImageFilesList(user_folder_path)
                    if len(img_path_list) == 0:
                        print("user picture is not availbale in db!!")
                        partage.logger.info(
                            "No picture available with eid : {}".format(eid)
                        )
                        return (False, [])
                    else:
                        # image = face_recognition.load_image_file(img_path)
                        print(
                            "Found {} picture, a new embedding is being generated!!!".format(
                                eid
                            )
                        )
                        partage.logger.info(
                            "Facial vector generated for {}".format(eid)
                        )
                        embedding = fvgen.EmbeddingGenerator(self.model, img_path_list)
                        if len(embedding) == 0:
                            partage.logger.info(
                                f"picture of {match[1]} available in DB not suitable for registration "
                            )
                            return (False, [])
                        x_ = np.array(embedding)
                        # print(fv_path)
                        np.save(fv_path, x_)
                        # print("saved")

                # print(fv_path)
                reference_encoding = np.load(fv_path)
                reference_encoding = np.array(reference_encoding.tolist())
                similarity = np.dot(
                    np.array(reference_encoding), np.array(face_encodings).T
                )
                # print(similarity)
                match_result = similarity > 0.5
                # dist = np.sum(np.square(np.array(reference_encoding) - np.array(face_encodings)))
                # print(dist)
                predictions = [
                    (match[1], loc) if rec else ("unknown", loc)
                    for loc, rec in zip(face_locations, match_result)
                ]
                face_available = True
            else:
                face_available = False
            return (face_available, predictions)
