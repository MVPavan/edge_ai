import cv2
import time
from Modular_code import Fr_Models
from Modular_code import partage
import sys


class TriggerClass:
    def __init__(self, accessobj, video_cap, model_obj):
        self.video = video_cap
        self.model = model_obj
        self.accessobj = accessobj
        self.last_trigger_time = time.time()

    def check_min_image_size(self, frame, tl_x, tl_y, br_x, br_y):
        # print("inside image_size_check_function")
        ym, xm = frame.shape[0:2]
        # print(xm,ym)
        tl_x1 = int((xm - 60) / 2)
        tl_y1 = int((ym - 100) / 2)
        br_x2 = int((xm + 60) / 2)
        br_y2 = int((ym + 100) / 2)
        # print("tl_x1,tl_y1, br_x2, br_y2")
        height_min = br_y2 - tl_y1
        width_min = br_x2 - tl_x1

        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.rectangle(frame, (tl_x1, tl_y1), (br_x2, br_y2), (0, 255, 0), 2)
        if br_x - tl_x < width_min or br_y - tl_y < height_min:
            # print("Image size is less than min size so, image not suitable for recognition")
            cv2.putText(
                frame, "Failed min size", (br_x2, br_y2), font, 0.5, (0, 255, 0), 1
            )
            return False
        else:
            # print("Image suitable for recognition")
            cv2.putText(
                frame, "Succeeded min size", (br_x2, br_y2), font, 0.5, (0, 255, 0), 1
            )
            return True

    def check_image_area_wrt_ref(self, frame, tl_x3, tl_y3, br_x4, br_y4):
        ym, xm = frame.shape[0:2]
        # print(xm,ym)
        ref_x1 = int(xm / 4)
        ref_y1 = int((ym / 4) * 0.75)
        ref_x2 = int(3 * xm / 4)
        ref_y2 = int((3 * ym / 4) * 1.4)

        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.rectangle(frame, (ref_x1, ref_y1), (ref_x2, ref_y2), (0, 0, 255), 2)

        w_cap_img = br_x4 - tl_x3
        h_cap_img = br_y4 - tl_y3
        area_cap_img = max(0, w_cap_img) * max(0, h_cap_img)

        inter_tl_x5 = max(ref_x1, tl_x3)
        inter_tl_y5 = max(ref_y1, tl_y3)
        inter_br_x6 = min(ref_x2, br_x4)
        inter_br_y6 = min(ref_y2, br_y4)
        w_inter = inter_br_x6 - inter_tl_x5
        h_inter = inter_br_y6 - inter_tl_y5
        area_inter = max(0, w_inter) * max(0, h_inter)

        if area_inter > 0.80 * area_cap_img:
            # print("Image is suitable for reconition")
            cv2.putText(
                frame, "Inside ref area", (ref_x2, ref_y2), font, 0.5, (0, 0, 255), 1
            )
            return True
        else:
            # print("Person's location is not correct so, image is notsuitable for recognition ")
            cv2.putText(
                frame, "Outside ref area", (ref_x2, ref_y2), font, 0.5, (0, 0, 255), 1
            )
            return False

    def wait_for_trigger(self, trigger_time=5, trigger_frame_count=5, ContReg=None):
        frame_count = 0
        frame = []
        wait = True
        last_reg_time = 0
        while wait:

            if frame_count == 0:
                if (time.time() - last_reg_time > 5) and ContReg != None:
                    ContReg()
                    last_reg_time = time.time()

            if time.time() - self.last_trigger_time < trigger_time:
                time.sleep(0.2)
                continue

            multi_flag = False
            grabbed, frame = self.video.read()
            if not grabbed:
                return False
            frame = partage.rotate_image(frame)
            frame = cv2.flip(frame, 1)
            # Using MTCNN Face detection get the faces in the frame
            bbox_pred = []
            bbox_pred = self.model.detect_faces_MTCNN(frame)

            if len(bbox_pred) != 0:
                frame_count = frame_count + 1
                # check for nearest face
                _, face_box, multi_flag = partage.nearest_face(
                    predictions=bbox_pred, thr=1.2
                )
                # if multi_flag:
                #     return multi_flag
                face_box = [int(coord) for coord in face_box]
                # Check for minimum face size
                face_size_valid = self.check_min_image_size(
                    frame, face_box[0], face_box[1], face_box[2], face_box[3]
                )
                # Check for face location in the frame reference are
                face_in_ref_frame = self.check_image_area_wrt_ref(
                    frame, face_box[0], face_box[1], face_box[2], face_box[3]
                )
                # Check trigger conditions are TRUE for 10 frames
                if (
                    face_size_valid
                    and face_in_ref_frame
                    and frame_count > trigger_frame_count
                ):
                    # save the time to compute the delay for next trigger
                    self.last_trigger_time = time.time()
                    wait = False
                cv2.rectangle(
                    frame,
                    (face_box[0], face_box[1]),
                    (face_box[2], face_box[3]),
                    (255, 0, 0),
                    2,
                )
            else:
                frame_count = 0

            # # print("here")
            if len(frame) != 0:  # and len(bbox_pred) != 0:
                if self.accessobj.show_thread.isAlive():
                    self.accessobj.show_thread.show_reset(new_frame=frame)
                else:
                    self.accessobj.show_thread = self.accessobj.thread_handler.show_start(
                        frame=frame
                    )
        return multi_flag

    pass
