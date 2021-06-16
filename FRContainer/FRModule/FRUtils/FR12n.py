import os
import time
import sys
import argparse
import csv
import shutil
from Modular_code import partage
from Modular_code import Fr_Models
from Modular_code import Access_Fns
from Modular_code import trigger
from Registration import FR_Register
from Modular_code import DBInterface
from queue import Empty


class Operations:
    def __init__(self, args):

        model_path_FN = (
            "./Face_DB/ClassModelBase/hw_dlib_2.clf"  # "./DB/model/all_dlib_1.clf"
        )
        model_path_EAI = "./Face_DB/ClassModelBase/trained_knn_model_512_4.clf"  # trained_knn_model_512_3.clf"
        model_path_IF = "./Face_DB/ClassModelBase/IF_combined.clf"
        self.Grp = "HW"
        self.Face_DB_path = os.path.join(os.path.dirname(__file__), "Face_DB")
        self.picture_base = os.path.join(self.Face_DB_path, "PictureBase")
        self.group_base = os.path.join(self.picture_base, self.Grp)

        if args.ebi_flag == "1":
            self.ebi_flag = True
        elif args.ebi_flag == "0":
            self.ebi_flag = False
        else:
            print("selected invalid ebi option '-ebi 0 or 1'  ")
            sys.exit()

        if args.auth_mode == "12n":
            self.fr_12n = True
        elif args.auth_mode == "121":
            self.fr_12n = False
        else:
            print("selected invalid authentication mode '-a 12n or -a 121'  ")
            sys.exit()

        if len(args.camera_id) > 1:
            disp_host = args.camera_id.split("//")[1].split(":")[0]
        else:
            disp_host = "192.168.0.1"

        partage.init(
            EBI_host=args.ebi_host,
            EBI_port=args.ebi_port,
            Disp_host=disp_host,
            Disp_port=5007,
        )
        self.access = Access_Fns.Access(
            fr_12n=self.fr_12n, host="192.168.0.108", port=1097, ebi_flag=self.ebi_flag
        )

        try:
            camera_id = int(args.camera_id)
        except:
            camera_id = args.camera_id
        self.video_capture = self.access.CameraInitialisation(camera_id)

        assert (
            (args.model).upper() == "FN"
            or (args.model).upper() == "EAI"
            or (args.model).upper() == "IF"
        ), "For now only supports model = FN , IF or EAI"

        if (args.model).upper() == "FN":
            self.model_obj = Fr_Models.MTCNN_FN_FR(model_path_FN)
            self.model_name = "FN"
            # print("\n opted Model Face Net ")
        elif (args.model).upper() == "IF":
            self.model_obj = Fr_Models.MTCNN_IF_FR(model_path_IF, self.group_base, args)
            self.model_name = "IF"
            # print("\n opted Model Deep Insight Face ")
        elif (args.model).upper() == "EAI":
            self.model_obj = Fr_Models.EverAi_FR(model_path_EAI)
            self.model_name = "EAI"
            # print("\n opted Model Ever AI ")

        self.register = FR_Register.FR_Register(
            args, face_model_obj=self.model_obj.model
        )
        self.newface_m_oldtime = os.path.getmtime(self.register.train_dir)
        partage.logger.info(
            "\n\n\nAuthentication system initialised ..............\n\n\n"
        )
        print("\n\n\nAuthentication system initialised ..............\n\n\n")

    def fetch_card_reader(self, timeout=0):

        [key, mask, hid, card_id, allow, eid, enrolled, name] = [
            None,
            None,
            None,
            None,
            False,
            None,
            False,
            "",
        ]
        flag_121 = False
        # print(f"Got card id : {ser_data} of length {len(ser_data)}")
        try:
            print("waiting for card data .......")
            if timeout == 0:
                [ser_data, key, mask] = partage.Rpi_rec_queue.get()
            elif timeout > 0:
                try:
                    [ser_data, key, mask] = partage.Rpi_rec_queue.get(
                        block=True, timeout=timeout
                    )
                except Empty:
                    return [
                        key,
                        mask,
                        hid,
                        card_id,
                        allow,
                        eid,
                        enrolled,
                        name,
                        flag_121,
                    ]

            # print("prosessing Queue info")
            check_word, hid, card_id = ser_data.split(":")
            partage.Rpi_rec_queue.task_done()

            if check_word == "data":
                flag_121 = True
                eid = self.access.db_obj.get_eid(hid)
                print("got -Eid - hid ", eid, hid)
                if eid == "":
                    enrolled = False
                    partage.logger.info(f"card ID {hid} not enrolled in database!")
                elif len(eid) != 7:
                    enrolled = False
                    print("Enrolled Invalid EID, please correct the HID2EID database!")
                else:
                    enrolled = True
                    name = self.access.db_obj.get_name(eid)

        except:
            partage.logger.info(
                f"Error while recieving the card_id, recieved {ser_data}"
            )

        return [key, mask, hid, card_id, allow, eid, enrolled, name, flag_121]

    def ContinousRegistration_fun(self,):
        def ContinousRegistration():
            if os.path.getmtime(self.register.train_dir) > self.newface_m_oldtime:
                self.register.FR_Enroll(
                    model_save_path=self.register.combined_path, n_neighbors=1
                )
                self.newface_m_oldtime = os.path.getmtime(self.register.train_dir)

        return ContinousRegistration

    def FR_12N_fun(self,):
        [key, mask, hid, card_id, allow, eid, enrolled, name] = [
            None,
            None,
            None,
            None,
            False,
            None,
            False,
            "",
        ]

        if self.ebi_flag:
            print("\nWaiting for RPI connection .........\n")
            [_, key, mask] = partage.Rpi_rec_queue.get()
            partage.Rpi_rec_queue.task_done()
            print("\nEstablished connection from RPI\n")

        crf = self.ContinousRegistration_fun()

        close = False
        trigger_obj = trigger.TriggerClass(
            self.access, self.video_capture, self.model_obj
        )

        while not close:
            grabbed, _ = self.video_capture.read()
            if not grabbed:
                if not self.ebi_flag:
                    print("Camera source is not running .....")
                    time.sleep(2)
                    continue
                [
                    key,
                    mask,
                    hid,
                    card_id,
                    allow,
                    eid,
                    enrolled,
                    name,
                    flag_121,
                ] = self.fetch_card_reader(timeout=5)
                if hid != None:
                    self.access.RpiComm(enrolled, name, card_id, key, mask, bypass=True)
                    partage.logger.info("Allowed {} - using only card".format(eid))
                    print("Allowed {} - using only card".format(eid))
            else:
                if allow:
                    wait_time = 5
                else:
                    wait_time = 2

                multi_flag = trigger_obj.wait_for_trigger(
                    trigger_time=wait_time, ContReg=crf
                )
                allow = False
                # allow = self.access.access_check(self.video_capture,model=[self.model_name,self.model_obj], match=[False,eid,0.5,[hid,card_id,key,mask,enrolled,name]]) #match - [True - 121 else 12n, eid, FN - threshold,[hid,card_id,key,mask,enrolled]]
                try:
                    allow = self.access.access_check(
                        self.video_capture,
                        model=[self.model_name, self.model_obj],
                        match=[
                            False,
                            eid,
                            0.5,
                            [hid, card_id, key, mask, enrolled, name],
                        ],
                    )  # match - [True - 121 else 12n, eid, FN - threshold,[hid,card_id,key,mask,enrolled]]
                except:
                    partage.logger.info(f"Error while authenticating 12n!")
                    print(f"Error while authenticating 12n")
                    close = True

            while not partage.Rpi_rec_queue.empty():
                try:
                    partage.Rpi_rec_queue.get(block=False)
                    partage.Rpi_rec_queue.task_done()
                except Empty:
                    print("RPI Queue emptying error FR 12N !")

        return

    def FR_121_fun(self, Face=True):
        print("\nWaiting for RPI connection .........\n")
        [_, key, mask] = partage.Rpi_rec_queue.get()
        partage.Rpi_rec_queue.task_done()
        print("\nEstablished connection from RPI\n")
        ContReg = self.ContinousRegistration_fun()
        close = False

        while not close:

            ContReg()
            [
                key,
                mask,
                hid,
                card_id,
                allow,
                eid,
                enrolled,
                name,
                flag_121,
            ] = self.fetch_card_reader(timeout=5)

            grabbed, _ = self.video_capture.read()
            if not grabbed:
                if hid != None:
                    self.access.RpiComm(enrolled, name, card_id, key, mask, bypass=True)
                    partage.logger.info("Allowed {} - using only card".format(eid))
                    print("Allowed {} - using only card".format(eid))
            elif hid != None:
                if flag_121:
                    # allow = access.access_check(video_capture,model=[self.model_name,self.model_obj], match=[True,eid,0.5,[hid,card_id,key,mask,enrolled]]) #match - [True - 121 else 12n, eid, FN - threshold]
                    try:
                        allow = self.access.access_check(
                            self.video_capture,
                            model=[self.model_name, self.model_obj],
                            match=[
                                True,
                                eid,
                                0.5,
                                [hid, card_id, key, mask, enrolled, name],
                            ],
                        )  # match=[True,eid,0.5,[hid,card_id,key,mask,enrolled,name]]
                    except:
                        partage.logger.info(f"Error while authenticating {eid}-{hid}")
                        print(f"Error while authenticating {eid}-{hid}")
                        close = True

            while not partage.Rpi_rec_queue.empty():
                try:
                    partage.Rpi_rec_queue.get(block=False)
                    partage.Rpi_rec_queue.task_done()
                except Empty:
                    print("RPI Queue emptying error FR 121 !")

        return


if __name__ == "__main__":

    # try:
    if True:
        parser = argparse.ArgumentParser(
            description="Facial Recognition ",
            usage="python FR12n.py -a 12n -c 0  - To register place new images in eid_hid_name folder inside Registration/RegNewFace ",
        )
        parser.add_argument(
            "-c", "--camera_id", action="store", dest="camera_id", default="1"
        )
        parser.add_argument("-m", "--model", action="store", dest="model", default="IF")
        parser.add_argument(
            "-a",
            "--authentication",
            action="store",
            dest="auth_mode",
            default="12n",
            help=" 12n, 121 , reg, query",
        )
        parser.add_argument(
            "-EBI_IP",
            "--tcp_ip",
            action="store",
            dest="ebi_host",
            default="192.168.0.180",
            help=" EBI Server IP",
        )
        parser.add_argument(
            "-EBI_Port",
            "--tcp_port",
            action="store",
            dest="ebi_port",
            default=1096,
            help=" EBI Server Port",
        )
        parser.add_argument(
            "-q",
            "--dbquery",
            action="store",
            dest="dbquery",
            default="",
            help=" Custom data base query ",
        )
        parser.add_argument(
            "-dhid",
            "--dbdelete_hid",
            action="store",
            dest="dbdelete_hid",
            default="",
            help=" delete data base with hid ",
        )
        parser.add_argument(
            "-ebi",
            "--ebi_flag",
            action="store",
            dest="ebi_flag",
            default="1",
            help=" 0 for disable 1 enable ",
        )

        # parser = argparse.ArgumentParser(description='face model test')
        parser.add_argument("--image-size", default="112,112", help="")
        parser.add_argument(
            "--IF_model",
            default="./models/model-r100-ii/model,0",
            help="path to load model.",
        )
        parser.add_argument("--gpu", default=0, type=int, help="gpu id")
        parser.add_argument(
            "--det",
            default=0,
            type=int,
            help="mtcnn option, 1 means using R+O, 0 means detect from begining",
        )
        parser.add_argument(
            "--flip", default=0, type=int, help="whether do lr flip aug"
        )
        parser.add_argument(
            "--threshold", default=1.24, type=float, help="ver dist threshold"
        )

        args = parser.parse_args()

        if args.auth_mode == "reg":
            register = FR_Register.FR_Register(args)
            register.FR_Enroll(model_save_path=register.combined_path, n_neighbors=1)
            sys.exit(0)
        elif args.auth_mode == "query":
            register = FR_Register.FR_Register(args, reg=False)
            if args.dbquery != "":
                data = register.frdb.sqlquery.CustomQuery(
                    args.dbquery
                )  # """DELETE from EID2HID where eid = 'xxxxx'"""
                print("output of the custom query : ", data)
            elif args.dbdelete_hid != "":
                eid = register.frdb.get_eid(args.dbdelete_hid)
                if eid != "":
                    name = register.frdb.get_name(eid)
                    data = register.frdb.sqlquery.delete(eid)
                    shutil.move(
                        os.path.join(
                            register.group_base,
                            "{}_{}_{}".format(eid, int(args.dbdelete_hid), name),
                        ),
                        register.deleted_base,
                    )
                    register.KNN_Model(
                        model_save_path=register.combined_path, n_neighbors=1
                    )
                    print("output of db delete : ", data, eid, name)
                else:
                    print("No user with hid - {}".format(args.dbdelete_hid))
            else:
                print("No query passed !!")
            sys.exit(0)

        ops = Operations(args)

        start = time.monotonic()

        if not ops.fr_12n:
            ops.FR_121_fun()

        elif ops.fr_12n:
            ops.FR_12N_fun()

        end = time.monotonic()
        print(f"\ntime for Authorization end to end {end-start}\n")

    # except :
    #     sys.exit()
