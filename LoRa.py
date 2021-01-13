import serial
import time
import signal
import threading
import os
from haversine import haversine
from detect import detectThread
import logging
import queue

line = [] #라인 단위로 데이터 가져올 리스트 변수

port = '/dev/ttyS3' # 시리얼 포트
baud = 115200 # 시리얼 보드레이트(통신속도)
main_gpio = 65
camera_gpio = 111
audio_gpio = 112
pir_gpio = 113

exitThread = False   # 쓰레드 종료용 변수
start = (0,0)
distance = None
eui_data = "1f9f0c", "1f9f0d"

start_latitude, start_longitude = 37.540166, 127.056670
lora_detect = False
log = logging.getLogger('detect')
log.setLevel(logging.DEBUG)
log_handler = logging.StreamHandler()
log.addHandler(log_handler)

def protocol(tmp):
    global lora_detect
    if "RECV" in tmp: ## 어떤 데이터를 받게 되며
        if tmp.count(':') > 4:
            recv_eui = tmp.split(":")[1]
            p = tmp.split(":")[3]
            log.info("protocol is {}".format(p))
            if p == "CAMERA" |  p == "AUDIO" | p == "PIR": ## 센서 감지 프로토콜
                recvdata = tmp.split(":")[4]
                log.info("LoRa: receving data {0} from {1}".format(recvdata, recv_eui))
                if recvdata == "LIGHTON":
                    lora_detect = True
            elif p == "LOCATE":
                recvdata = tmp.split(":")[4]
                ## LOCATE 프로토콜은 위도 경도 순서로 보내지며 해당 프로토콜은 타 보드의 위치정보를 저장하는 용도로 사용된다.
                goal_latitude = recvdata.split(",")[0]
                goal_longitude = recvdata.split(",")[1]
                goal_latitude  = float(goal_latitude)
                goal_longitude = float(goal_longitude)
                goal = (goal_latitude, goal_longitude)
                distance = haversine(start, goal, unit='m') ## 위도 경도를 이용하여 거리를 계산한다.
                log.info("LoRa : distance between {0} and me is {1}".format(eui_data, distance))
                if recvdata == "RECV":
                    log.info("Locate command is sucess")

#쓰레드 종료용 시그널 함수
def handler(signum, frame):
    global exitThread
    exitThread = True

#본 쓰레드
def readThread(ser, exitThread):
    global line
    global on_state
    global lora_detect
    ## 초기화
    # 쓰레드 종료될때까지 계속 돌림
    on_state = False
    while not exitThread:
        reading = ser.readline().decode()
        protocol(reading)

        
            
def writeThread(ser, exitThread):
    start = time.time()
    command = ""
    while not exitThread:
        t = time.time() - start
        camera_detect = os.popen('cat /sys/class/gpio/gpio111/value').read()
        audio_detect = os.popen('cat /sys/class/gpio/gpio112/value').read()
        pir_detect = os.popen('cat /sys/class/gpio/gpio113/value').read()

        if camera_detect | audio_detect | pir_detect | lora_detect:
            if camera_detect:
                command = "CAMERA:LIGHTON"
                os.system('echo 0 > /sys/class/gpio/gpio{}/value'.format(camera_gpio))
            elif audio_detect:
                command = "AUDIO:LIGHTON"
                os.system('echo 0 > /sys/class/gpio/gpio{}/value'.format(audio_gpio))
            elif pir_detect:
                command = "PIR:LIGHTON"
                os.system('echo 0 > /sys/class/gpio/gpio{}/value'.format(pir_gpio))
            for eui in eui_data:
                ser.write(bytes(("AT+DATA={0}:{1}:\r\n").format(eui, command),'ascii'))
                log.info("{0} command send to {1}".format(command, eui))
            os.system('echo 1 > /sys/class/gpio/gpio{}/value'.format(main_gpio))
            start = time.time()
        else :
            t = time.time() - start
            if t >= 30:
                os.system('echo 0 > /sys/class/gpio/gpio{}/value'.format(main_gpio))
                log.info("light off")
    

if __name__ == "__main__":
    #종료 시그널 등록
    signal.signal(signal.SIGINT, handler)
    #시리얼 열기
    ser = serial.Serial(port, baud, timeout=0)
    lock = threading.Lock()
    #시리얼 읽을 쓰레드 생성
    read_t = threading.Thread(target=readThread, args=(ser,exitThread))
    camera_t = threading.Thread(target=detectThread, args=(exitThread))
    write_t = threading.Thread(target=writeThread, args=(ser, exitThread))
    #시작!
    read_t.start()
    camera_t.start()
    write_t.start()