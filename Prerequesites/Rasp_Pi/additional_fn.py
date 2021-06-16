import time
from time import sleep
import array as arr
import RPi.GPIO as GPIO
import socket
import threading

DATA0_IN = 15
DATA1_IN = 16

DATA0_OUT = 31  # output DATA0 (Green) to Controller
DATA1_OUT = 32  # output DATA1 (White) to Controller

TCP_IP = "192.168.0.108"
TCP_PORT = 1097

TO_MICRO_SEC = 1000000.0
max_bits = 100
wait_time = 3000
card_len = 35
facility_code = 0
card_code = 0
bitcount = 0
flagdone = 1
tmp = 0
s = 0
FR_Connect = False

data_bits = [0] * 100
no_data_counter = 300


def ISR_INT0(DATA0_IN):
    flagdone = 0
    global bitcount
    # print(bitcount)
    data_bits[bitcount] = 0
    print("{}: {}".format(bitcount, data_bits[bitcount]))
    bitcount += 1


def ISR_INT1(DATA1_IN):
    flagdone = 0
    global bitcount
    # print(bitcount)
    data_bits[bitcount] = 1
    print("{}: {}".format(bitcount, data_bits[bitcount]))
    bitcount = bitcount + 1


def send_Card_Data_FR():
    MESSAGE = "data:" + str(card_code) + ":"
    # print(MESSAGE)
    # s.sendall(MESSAGE.encode('utf-8'))
    st = [str(i) for i in data_bits[0:35]]
    res = "".join((st))
    MESSAGE = MESSAGE + res

    try:
        s.sendall(MESSAGE.encode("utf-8"))
    except:
        print("Exception Handled: could not send card data to FR")

    print("message length={}".format(len(MESSAGE)))
    # sleep(2)
    # data= s.recv(1024)
    # s.close()
    # print("received data={}".format(data))


def send_dummy_data():
    MESSAGE = "Data sending to FR"
    s.sendall(MESSAGE.encode("utf-8"))
    print("message length={}".format(len(MESSAGE)))


def receive_FR_data():
    bits_received = 0
    bits_expected = 35
    data_rcv_from_FR = [0] * 100
    data_rcv_from_FR_decode = [0] * 100
    global s
    global FR_Connect
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("socket open")
    while True:
        try:
            s.connect((TCP_IP, TCP_PORT))
            send_dummy_data()
            print("socket connected")
            FR_Connect = True
            break
        except:
            bitcount = 0
            continue
    # while bits_received<bits_expected:
    while True:
        # if s.stillconnected() is flase:
        # print("data is available")
        data_rcv_from_FR = s.recv(1024)
        if len(data_rcv_from_FR) == 0:
            print("Lost connection and trying to reconnect ...")
            s.close()
            FR_Connect = False
            sleep(1)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print("socket reopened")
            while True:
                try:
                    s.connect((TCP_IP, TCP_PORT))
                    send_dummy_data()
                    print("socket reconnected")
                    FR_Connect = True
                    break
                except:
                    bitcount = 0
                    continue
            continue
        data_rcv_from_FR_decode = data_rcv_from_FR.decode()
        bits_received = len(data_rcv_from_FR_decode)
        print("bits_received={}".format(bits_received))
        if bits_received == 35:
            # s.close()
            print("received_data={}".format(data_rcv_from_FR_decode))
            sendCardData_Ctrl(data_rcv_from_FR_decode)
            data_rcv_from_FR = []
            data_rcv_from_FR_decode = []
        else:
            print(f"recieved broken package of length {len(data_rcv_from_FR)}")

    # s.close()


def sendCardData_Ctrl(card_data):
    data_len = len(card_data)
    for i in range(0, data_len):
        if card_data[i] == "0":
            GPIO.output(DATA0_OUT, False)
            time.sleep(20 / TO_MICRO_SEC)
            GPIO.output(DATA0_OUT, True)
        elif card_data[i] == "1":
            GPIO.output(DATA1_OUT, False)
            time.sleep(20 / TO_MICRO_SEC)
            GPIO.output(DATA1_OUT, True)
        time.sleep(20 / TO_MICRO_SEC)


def init_RP():

    GPIO.setmode(GPIO.BOARD)

    GPIO.setup(DATA0_OUT, GPIO.OUT)
    GPIO.setup(DATA1_OUT, GPIO.OUT)

    GPIO.output(DATA0_OUT, True)
    GPIO.output(DATA1_OUT, True)

    GPIO.setup(DATA0_IN, GPIO.IN)  # pull_up_down=GPIO.PUD_UP)
    GPIO.setup(DATA1_IN, GPIO.IN)  # , pull_up_down=GPIO.PUD_UP)

    GPIO.add_event_detect(DATA0_IN, GPIO.FALLING, callback=ISR_INT0)
    GPIO.add_event_detect(DATA1_IN, GPIO.FALLING, callback=ISR_INT1)

    time.sleep(20 / TO_MICRO_SEC)


def init_socket():

    receive_thread = threading.Thread(target=receive_FR_data)
    receive_thread.start()


def main():
    st_time = time.time()
    # print("Start_time={}".format(st_time))
    global flagdone
    global bitcount
    global tmp
    global card_code
    global facility_code
    global data_bits
    global FR_Connect
    while True:

        wait_count = 0
        while bitcount < 35:
            if bitcount > 0:
                if wait_count == 10:
                    break
                wait_count = wait_count + 1
            sleep(0.1)

        if bitcount == 35:
            for i in range(0, 1):
                tmp <<= 1
                tmp |= data_bits[i]
            for i in range(2, 14):
                facility_code <<= 1
                facility_code |= data_bits[i]
            for i in range(15, 34):
                card_code <<= 1
                card_code |= data_bits[i]
            # print("tmp={}".format(tmp))
            print("card_code={}".format(card_code))
            # print("facility_code={}".format(facility_code))
            if FR_Connect:
                send_Card_Data_FR()
            else:
                st = [str(i) for i in data_bits[0:35]]
                res = "".join((st))
                sendCardData_Ctrl(res)
                print("access granted for :", res)

        bitcount = 0
        data_bits = [0] * 100
        tmp = 0
        card_code = 0
        facility_code = 0


# print("Hi")
init_RP()
init_socket()

# while(True):
main()
GPIO.cleanup()
