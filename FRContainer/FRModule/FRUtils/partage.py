import logging
import os
import time
import cv2
import threading
import socket
import sys
import selectors
import types
import queue
import re

# cwd = os.getcwd()
# logs_path = cwd+"/Logs/"
# image_saver_daemon_flag = True
# image_saver_thread_count = 3

#########################################################################################################################################################################
def init(EBI_host, EBI_port, Disp_host, Disp_port):
    global logger
    global Rpi_rec_queue  # , Disp_send_queue
    Rpi_rec_queue = queue.Queue()
    # Disp_send_queue = queue.Queue()
    logging.basicConfig(
        filename=Common_Var.logs_path + "DA_logs.log",
        format="%(asctime)s %(message)s",
        filemode="a+",
    )
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    Common_Var.EBI_host = EBI_host
    Common_Var.EBI_port = EBI_port
    Common_Var.Disp_host = Disp_host
    Common_Var.Disp_port = Disp_port


#########################################################################################################################################################################
class Common_Var:
    cwd = os.getcwd()
    logs_path = f"{cwd}/Logs/"
    image_saver_daemon_flag = True
    image_saver_thread_count = 3
    EBI_daemon_flag = True
    EBI_host = "127.0.0.1"
    EBI_port = 8080
    Disp_host = "192.168.0.1"
    Disp_port = 5007


#########################################################################################################################################################################


def image_files_in_folder(folder):
    return [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if re.match(r".*\.(jpg|jpeg|png)", f, flags=re.I)
    ]


##################################################################################################################################################################################################
def addRoundedRectangleBorder(img, red, green, blue):
    height, width, channel = img.shape

    border_radius = 40  # int(width * random.randint(1, 10)/100.0)
    line_thickness = 40  # int(max(width, height) * random.randint(1, 3)/100.0)
    edge_shift = int(line_thickness / 2.0)

    # red = random.randint(6,6)
    # green = random.randint(115,115)
    # blue = random.randint(8,8)
    color = (blue, green, red)

    # draw lines
    # top
    cv2.line(
        img,
        (border_radius, edge_shift),
        (width - border_radius, edge_shift),
        (blue, green, red),
        line_thickness,
    )
    # bottom
    cv2.line(
        img,
        (border_radius, height - line_thickness),
        (width - border_radius, height - line_thickness),
        (blue, green, red),
        line_thickness,
    )
    # left
    cv2.line(
        img,
        (edge_shift, border_radius),
        (edge_shift, height - border_radius),
        (blue, green, red),
        line_thickness,
    )
    # right
    cv2.line(
        img,
        (width - line_thickness, border_radius),
        (width - line_thickness, height - border_radius),
        (blue, green, red),
        line_thickness,
    )

    # corners
    cv2.ellipse(
        img,
        (border_radius + edge_shift, border_radius + edge_shift),
        (border_radius, border_radius),
        180,
        0,
        90,
        color,
        line_thickness,
    )
    cv2.ellipse(
        img,
        (width - (border_radius + line_thickness), border_radius),
        (border_radius, border_radius),
        270,
        0,
        90,
        color,
        line_thickness,
    )
    cv2.ellipse(
        img,
        (
            width - (border_radius + line_thickness),
            height - (border_radius + line_thickness),
        ),
        (border_radius, border_radius),
        10,
        0,
        90,
        color,
        line_thickness,
    )
    cv2.ellipse(
        img,
        (border_radius + edge_shift, height - (border_radius + line_thickness)),
        (border_radius, border_radius),
        90,
        0,
        90,
        color,
        line_thickness,
    )


##########################################################################################################################################################################################

#########################################################################################################################################################################
def rotate_image(frame):
    return frame
    # h,w = frame.shape[:2]
    # #print("height is {h} and width is {w}")
    # center= (w/2,h/2)
    # angle=90
    # scale=1
    # M= cv2.getRotationMatrix2D(center, angle,scale)
    # rotated_img= cv2.warpAffine(frame, M, (w,h))
    # return rotated_img


#########################################################################################################################################################################
def nearest_face(predictions, thr=1.2, limit=0.8):
    near_face = []
    # print("predictions NF: " , predictions)
    face_name, near_face = predictions[0]
    multi_flag = False
    # print(near_face)
    if len(predictions) > 1:
        old_values = []
        near_width = near_face[1] - near_face[3]
        near_height = near_face[2] - near_face[0]
        for name, face in predictions:
            # print('\n',face,'\n')
            (left, top, right, bottom, *_) = face
            width = right - left
            height = bottom - top
            if (
                width * height >= thr * near_width * near_height
            ):  # elif (bottom-top)-(nfl[2]-nfl[0])>npd and (right-left)-(nfl[1]-nfl[3])
                ## either area logic or width and height logic
                old_values = [near_width, near_height, near_face, face_name]
                near_width = width
                near_height = height
                near_face = (left, top, right, bottom)
                face_name = name
        psize = (old_values[0] * old_values[1]) / (near_width * near_height)
        if psize > limit:
            multi_flag = True
        # print("nearest face details: ",name,(left,top,right, bottom),width,height)
    return face_name, near_face, multi_flag


#########################################################################################################################################################################
def check_min_image_size_xyz(tl_x, tl_y, br_x, br_y):
    # print("inside image_size_check_function")
    tl_x1 = 270
    tl_y1 = 135
    br_x2 = 369
    br_y2 = 291
    # print("tl_x1,tl_y1, br_x2, br_y2")
    height_min = br_y2 - tl_y1
    width_min = br_x2 - tl_x1
    if br_x - tl_x << width_min or br_y - tl_y << height_min:
        # print("Image size is less than min size so, image not suitable for recognition")
        return False
    else:
        # print("Image suitable for recognition")
        return True


#############################################################################################################################################################################
def check_image_area_wrt_ref(tl_x3, tl_y3, br_x4, br_y4):
    ref_x1 = 179
    ref_y1 = 29
    ref_x2 = 510
    ref_y2 = 392
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

    # print("w_cap_img={}".format(w_cap_img))
    # print("h_cap_img={}".format(h_cap_img))
    # print("area of captured image={}".format(area_cap_img))

    # print("inter_tl_x5={}".format(inter_tl_x5))
    # print("inter_tl_y5={}".format(inter_tl_y5))
    # print("inter_br_x6={}".format(inter_br_x6))
    # print("inter_br_y6={}".format(inter_br_y6))
    # print("w_inter={}".format(w_inter))
    # print("h_inter={}".format(h_inter))
    if area_inter >> 0.70 * area_cap_img:
        # print("Image is suitable for recognition")
        return True
    else:
        # print("Person's location is not correct so, image is notsuitable for recognition ")
        return False


###################################################################################################################################################################################


class WebcamVideoStream:
    def __init__(self, src=0, name="WebcamVideoStream"):
        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;0"
        # initialize the video camera stream and read the first frame
        # from the stream
        self.src = src
        self.stream = cv2.VideoCapture(self.src)
        (self.grabbed, self.frame) = self.stream.read()

        # initialize the thread name
        self.name = name

        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False

    def VideoCaptureObject(self):
        return cv2.VideoCapture(self.src)

    def start(self):
        # start the thread to read frames from the video stream
        t = threading.Thread(target=self.update, name=self.name, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:

            if self.stopped:
                return

            (self.grabbed, self.frame) = self.stream.read()

            if not self.grabbed:
                time.sleep(1)
                self.stream = self.VideoCaptureObject()

    def read(self):
        # return the frame most recently read
        # print(len(self.frame))
        return self.grabbed, self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True


###################################################################################################################################################################################


class SaveThread(threading.Thread):
    def __init__(self, im_queue):
        self.im_queue = im_queue
        self.rlock = threading.RLock()
        super(SaveThread, self).__init__()

    def run(self):
        while True:
            time.sleep(0.1)
            with self.rlock:
                [content, folname] = self.im_queue.get()
            self.save(content, folname)
            self.im_queue.task_done()

    def save(self, content, folname):
        temp = time.ctime()
        fname = folname + "_"
        for c in temp:
            if c == " " or c == ":":
                fname = fname + "_"
            else:
                fname = fname + c
        if folname == "multiple":
            counter = 0
            for frame in content:
                # print("saving 'multiple' error to logs  ")
                img_path = f"{Common_Var.logs_path}{folname}/{fname}_{counter}.jpg"
                cv2.imwrite(img_path, frame)
                counter = counter + 1
        elif folname == "allowed":
            for frame in content:
                # print("saving 'allowed' to logs  ")
                img_path = f"{Common_Var.logs_path}{folname}/{fname}.jpg"
                cv2.imwrite(img_path, frame)
        if folname == "denied":
            for frame in content:
                # print("saving 'denied' to logs  ")
                img_path = f"{Common_Var.logs_path}{folname}/{fname}.jpg"
                cv2.imwrite(img_path, frame)
        if folname == "noface":
            for frame in content:
                # print("saving 'noface' to logs  ")
                img_path = f"{Common_Var.logs_path}{folname}/{fname}.jpg"
                cv2.imwrite(img_path, frame)
        if folname == "temp":
            counter = 0
            for frame in content:
                # print("saving 'temp' to logs  ")
                img_path = f"{Common_Var.logs_path}{folname}/{fname}_{counter}.jpg"
                cv2.imwrite(img_path, frame)
                counter = counter + 1
        return


#########################################################################################################################################################################
class ShowThread(threading.Thread):
    def __init__(self, frame):
        self.frame = frame
        self.rlock = threading.RLock()
        self.counter_val = 500
        self.reset_flag = True
        super(ShowThread, self).__init__()

    def show_reset(self, new_frame):
        with self.rlock:
            self.frame = new_frame
            self.reset_flag = True

    def run(self):
        time.sleep(0.1)
        if len(self.frame) != 0:
            self.show()

    def show(self):
        # pass
        while self.reset_flag:
            self.reset_flag = False
            cv2.imshow("Access", self.frame)
            time_counter = 0
            while True:
                time_counter = time_counter + 1
                # # Hit 'q' on the keyboard to quit!
                if cv2.waitKey(10) & 0xFF == ord("q"):
                    break
                if time_counter > self.counter_val:
                    break
                if self.reset_flag:
                    break
        # cv2.destroyAllWindows()
        cv2.destroyWindow("Access")


#########################################################################################################################################################################


class LiveShowThread(threading.Thread):
    def __init__(self, frame=None):
        self.frame = frame
        self.rlock = threading.RLock()
        self.stopped = False
        super(LiveShowThread, self).__init__()

    def stream(self, new_frame):
        with self.rlock:
            self.frame = new_frame
            self.stopped = False

    def run(self):
        time.sleep(0.1)
        if len(self.frame) != 0:
            self.show_live()

    def show_live(self):
        while not self.stopped:
            self.stopped = True
            cv2.imshow("Camera", self.frame)
            while True:
                if cv2.waitKey(1) == ord("q"):
                    break
                if not self.stopped:
                    break
        cv2.destroyWindow("Camera")
        # cv2.destroyAllWindows()

    def stop(self):
        self.stopped = True


#########################################################################################################################################################################
class RelayThread(threading.Thread):
    def __init__(self, delay_flag=False, on_flag=False, seconds=5):
        self.off_cmd = "sudo bash ./USB_Relay/usbrelayoff.sh"
        self.on_cmd = "sudo bash ./USB_Relay/usbrelayon.sh"
        self.rlock = threading.RLock()
        self.delay_flag = delay_flag
        self.on_flag = on_flag
        self.seconds = seconds
        super(RelayThread, self).__init__()

    def relay_reset(self, seconds):
        # print("got hrer")
        with self.rlock:
            self.delay_flag = True
            self.seconds = seconds

    def run(self):
        time.sleep(0.1)
        if self.on_flag:
            self.relay_on()
            with self.rlock:
                self.on_flag = False

        while self.delay_flag:
            with self.rlock:
                self.delay_flag = False
            time.sleep(self.seconds)
        self.relay_off()

    def relay_off(self):
        pass
        # k=os.system(self.off_cmd)
        # print("switched off the relay")
        return

    def relay_on(self):
        pass
        # k=os.system(self.on_cmd)
        # print("switched on the relay")
        return


#########################################################################################################################################################################


class EBISocketThread(threading.Thread):
    def __init__(self, EBI_sock=None, ebi_queue=[]):
        self.ebi_queue = ebi_queue
        self.connected = False
        self.rlock = threading.RLock()
        if EBI_sock is None:
            self.EBI_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.EBI_sock = EBI_sock
        super(EBISocketThread, self).__init__()

    def run(self):
        while True:
            time.sleep(0.1)
            if not self.connected:
                try:
                    self.connect_EBI(Common_Var.EBI_host, Common_Var.EBI_port)
                    self.connected = True
                except:
                    continue

            with self.rlock:
                [msg] = self.ebi_queue.get()
            self.Send2EBI(msg)
            self.ebi_queue.task_done()
        self.EBI_sock.close()
        self.connected = False

    def connect_EBI(self, host, port):
        self.EBI_sock.connect((host, port))

    def Send2EBI(self, msg):
        msg = msg.encode("utf-8")
        MSGLEN = len(msg)
        totalsent = 0
        while totalsent < MSGLEN:
            sent = self.EBI_sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent
        print(f"Communicated {msg} of lenght {MSGLEN} bits to EBI")


#################################################################################################################################################################################


class DisplaySocketThread(threading.Thread):
    def __init__(self, Disp_sock=None, Disp_queue=[]):
        self.Disp_queue = Disp_queue
        self.connected = False
        self.rlock = threading.RLock()
        # if Disp_sock is None:
        #     self.Disp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # else:
        #     self.Disp_sock = Disp_sock
        super(DisplaySocketThread, self).__init__()
        print("Disp thread initialised")

    def run(self):
        while True:
            time.sleep(0.5)
            # print("++++++++++ Display thread running +++++++++++++")
            if not self.connected:
                try:
                    self.connect2Disp(Common_Var.Disp_host, Common_Var.Disp_port)
                    self.connected = True
                    print(
                        f"****** Connection established {Common_Var.Disp_host}:{Common_Var.Disp_port}**********"
                    )
                except:
                    # print(f"****** Failed to Connect {Common_Var.Disp_host}:{Common_Var.Disp_port}**********")
                    continue

            with self.rlock:
                [msg] = self.Disp_queue.get()
            self.Send2Disp(msg)
            self.Disp_sock.close()
            self.connected = False
            self.Disp_queue.task_done()
        self.Disp_sock.close()
        self.connected = False

    def connect2Disp(self, host, port):
        self.Disp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.Disp_sock.connect((host, port))

    def Send2Disp(self, msg):
        msg = msg.encode("utf-8")
        MSGLEN = len(msg)
        totalsent = 0
        while totalsent < MSGLEN:
            sent = self.Disp_sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent
        print(f"*****Communicated {msg} of lenght {totalsent} bits to Display")
        # self.Disp_sock.
        # print(msg)
        # sent = self.Disp_sock.sendall(bytes(msg,'utf-8'))
        # print(f"*****Communicated {msg} of lenght {sent} bits to Display")


#################################################################################################################################################################################


class RpiSocketThread(threading.Thread):
    def __init__(self, host, port):
        self.rlock = threading.RLock()
        self.sel = selectors.DefaultSelector()
        self.Rpi_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.Rpi_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.Rpi_sock.bind((host, port))
        self.Rpi_sock.listen()
        print("listening on", (host, port))
        self.Rpi_sock.setblocking(False)
        self.sel.register(self.Rpi_sock, selectors.EVENT_READ, data=None)
        super(RpiSocketThread, self).__init__()

    def run(self):
        while True:
            time.sleep(0.2)
            with self.rlock:
                events = self.sel.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        self.accept_wrapper(key.fileobj)
                    else:
                        self.service_connection(key, mask)
        self.sel.close()

    def accept_wrapper(self, sock):
        conn, addr = sock.accept()  # Should be ready to read
        print("accepted connection from", addr)
        conn.setblocking(False)
        data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.sel.register(conn, events, data=data)

    def service_connection(self, key, mask):
        self.key = key
        self.mask = mask
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(1024)  # Should be ready to read
            recv_data = recv_data.decode()
            if recv_data:
                # data.outb += recv_data
                with self.rlock:
                    Rpi_rec_queue.put([recv_data, key, mask])
                    # print("pushed data in Queue!")
            else:
                print("closing connection to", data.addr, recv_data)
                self.sel.unregister(sock)
                sock.close()

    def Send2Rpi(self, key, mask, msg):
        key = self.key
        mask = self.mask
        msg = msg.encode("utf-8")
        MSGLEN = len(msg)
        # print(f"have to send {MSGLEN}")
        sock = key.fileobj
        data = key.data
        totalsent = 0
        while totalsent < MSGLEN:
            sent = sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent
        # print(f"sent {msg} of length {MSGLEN} to {data.addr}")


#################################################################################################################################################################################
class Thread_Handlers:
    def __init__(self, im_queue_handler):
        self.save_thread_count = Common_Var.image_saver_thread_count
        self.save_thread_list = []
        for i in range(self.save_thread_count):
            save_thread = self.save_thread_assigner(im_queue_handler)
            self.save_thread_list.append(save_thread)

    def relay_start(self, delay_flag, on_flag, seconds):
        relay_thread = RelayThread(delay_flag, on_flag, seconds)
        relay_thread.start()
        return relay_thread

    def save_thread_assigner(self, queue):
        save_thread = SaveThread(queue)
        save_thread.setDaemon(Common_Var.image_saver_daemon_flag)
        save_thread.start()
        return save_thread

    def show_start(self, frame):
        show_thread = ShowThread(frame)
        show_thread.start()
        return show_thread

    def live_show(self, frame):
        liveShow_thread = LiveShowThread(frame)
        liveShow_thread.start()
        return liveShow_thread

    def ebi_socket_handler(self, queue):
        sock_thread = EBISocketThread(ebi_queue=queue)
        # sock_thread.connect_EBI(Common_Var.EBI_host,Common_Var.EBI_port)
        sock_thread.setDaemon(Common_Var.EBI_daemon_flag)
        sock_thread.start()
        return sock_thread

    def disp_socket_handler(self, queue):
        sock_thread = DisplaySocketThread(Disp_queue=queue)
        # sock_thread.connect_EBI(Common_Var.EBI_host,Common_Var.EBI_port)
        sock_thread.setDaemon(Common_Var.EBI_daemon_flag)
        sock_thread.start()
        return sock_thread

    def rpi_socket_handler(self, host, port):
        rpi_sock_thread = RpiSocketThread(host, port)
        rpi_sock_thread.setDaemon(True)
        rpi_sock_thread.start()
        return rpi_sock_thread


#################################################################################################################################################################################
