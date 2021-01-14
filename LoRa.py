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
eui_data = "1f9f0c"

start_latitude, start_longitude = 37.540166, 127.056670
lora_detect = False
log = logging.getLogger('detect')
log.setLevel(logging.DEBUG)
log_handler = logging.StreamHandler()
log.addHandler(log_handler)

def protocol(rawdata):
    tmp = ''.join(rawdata)
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
        for c in ser.read():
            line.append(chr(c))
            if c == 10:
               protocol(line)
               del line

def writeThread(ser, exitThread):
    on_state = False
    start = time.time()
    command = ""
    while not exitThread:
        camera_detect = os.popen('cat /sys/class/gpio/gpio111/value').read()
        audio_detect = os.popen('cat /sys/class/gpio/gpio112/value').read()
        pir_detect = os.popen('cat /sys/class/gpio/gpio113/value').read()
        if camera_detect == "1" or audio_detect == "1" or pir_detect == "1" or lora_detect == "1":
            if camera_detect:
                command = "CAMERA:LIGHTON"
                os.system("echo 0 > /sys/class/gpio/gpio111/value")
            elif audio_detect:
                command = "AUDIO:LIGHTON"
                os.system('echo 0 > /sys/class/gpio/gpio112/value')
            elif pir_detect:
                command = "PIR:LIGHTON"
                os.system('echo 0 > /sys/class/gpio/gpio113/value')
            if not command :
                ser.write(bytes(("AT+DATA={0}:{1}:\r\n").format(eui, command),'ascii'))
                log.info("{0} command send to {1}".format(command, eui))
                command = ""
            on_state = True
            os.system('echo 1 > /sys/class/gpio/gpio{}/value'.format(main_gpio))
            start = time.time()
        else :
            if on_state:
            	t = time.time() - start
            	if t >= ontime:
                	os.system('echo 0 > /sys/class/gpio/gpio{}/value'.format(main_gpio))
                	log.info("light off")
                	on_state = False

if __name__ == "__main__":
    global ontime
    ontime = 30
    #종료 시그널 등록
    signal.signal(signal.SIGINT, handler)
    #시리얼 열기
    ser = serial.Serial(port, baud, timeout=0)
    #시리얼 읽을 쓰레드 생성
    read_t = threading.Thread(target=readThread, args=(ser,exitThread))
    camera_t = threading.Thread(target=detectThread, args=(ontime,exitThread))
    write_t = threading.Thread(target=writeThread, args=(ser,exitThread))
    #시작!
    read_t.start()
    camera_t.start()
    write_t.start()