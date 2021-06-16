import os, time
import threading
import cv2



class WebcamVideoStream:
    '''
    Taken from imutils Package
    '''
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
        return(cv2.VideoCapture(self.src))

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
        return self.grabbed,self.frame


    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True