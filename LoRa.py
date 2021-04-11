from typing import Iterator
import serial
import time
import signal
import threading
import os
import logging
import subprocess
from playsound import playsound
import vlc

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
lora_detect = False
log = logging.getLogger('detect')
log.setLevel(logging.DEBUG)
log_handler = logging.StreamHandler()
log.addHandler(log_handler)
eui_data=0x1f9eb7
    
def protocol(recv):
    global lora_detect
    tmp = ''.join(recv)
    if "RECV" in tmp: ## 어떤 데이터를 받게 되며
        if tmp.count(':') > 4:
            recv_eui = tmp.split(":")[1]
            p = tmp.split(":")[3]
            log.info("protocol is {}".format(p))
            if p == "CAMERA" or  p == "AUDIO" or p == "PIR": ## 센서 감지 프로토콜
                recvdata = tmp.split(":")[4]
                log.info("LoRa: receving data {0} from {1}".format(recvdata, recv_eui))
                if recvdata == "LIGHTON":
                    log.info("lora detect")
                    lora_detect = True

#쓰레드 종료용 시그널 함수
def handler(signum, frame):
    global exitThread
    exitThread = True

def str2bool(v):
   return str(v).lower() in ("yes", "true", "t", "1")
#본 쓰레드
def readThread(ser, exitThread):
    global line
    global on_state
    global lora_detect
    ## 초기화
    # 쓰레드 종료될때까지 계속 돌림
    on_state = False
    while not exitThread:
        bytesToRead = ser.inWaiting()
        if bytesToRead:
            for c in ser.read():
                line.append(chr(c))
                if c == 10:            
                    protocol(line)
                    del line[:]

def writeThread(ser, exitThread):
    on_state = False
    start = time.time()
    command = ""
    camera_detect = ""
    audio_detect = ""
    pir_detect = ""
    while not exitThread:
        camera_detect = str2bool(subprocess.getoutput('cat /sys/class/gpio/gpio111/value'))
        audio_detect = str2bool(subprocess.getoutput('cat /sys/class/gpio/gpio112/value'))
        pir_detect = str2bool(subprocess.getoutput('cat /sys/class/gpio/gpio113/value'))
        if camera_detect or audio_detect or pir_detect or lora_detect:
            if camera_detect:
                log.info("camera detect")
                command = "CAMERA:LIGHTON"
                subprocess.getoutput("echo 0 > /sys/class/gpio/gpio111/value")
            if audio_detect:
                log.info("audio detect")
                command = "AUDIO:LIGHTON"
            if pir_detect:
                log.info("pir detect")
                command = "PIR:LIGHTON"
                subprocess.getoutput('echo 0 > /sys/class/gpio/gpio113/value')
            subprocess.getoutput('echo 1 > /sys/class/gpio/gpio65/value & echo 1 > /sys/class/gpio/gpio74/value')
            os.system('sudo -u orangepi -H sh -c "vlc-ctrl play"')
            command = ""
            on_state = True
            start = time.time()
            playsound("teemo.mp3")
        else :
            if on_state:
                t = time.time() - start
                if t >= ontime:
                    log.info("light off")
                    os.system('sudo -u orangepi -H sh -c "vlc-ctrl pause"')
                    on_state = False
                    subprocess.getoutput('echo 0 > /sys/class/gpio/gpio65/value & echo 1 > /sys/class/gpio/gpio74/value')


if __name__ == "__main__":
    global ontime
    ontime = 30
    #종료 시그널 등록
    signal.signal(signal.SIGINT, handler)
    #시리얼 열기
    ser = serial.Serial(port, baud, timeout=0)
    #시리얼 읽을 쓰레드 생성
    log.info("LoRa & gpio handler is running!")
    
    write_t = threading.Thread(target=writeThread, args=(ser,exitThread))
    #시작!
    write_t.start()
