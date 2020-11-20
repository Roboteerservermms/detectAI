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

exitThread = False   # 쓰레드 종료용 변수
start = (0,0)
distance = None
sender_eui = "1f9b23 1f9b25 1f9f0f"
start_latitude, start_longitude = 37.540166, 127.056670
lora_detect = False
send_success = ""
sending_data = ""

log = logging.getLogger('detect')
log.setLevel(logging.DEBUG)
log_handler = logging.StreamHandler()
log.addHandler(log_handler)

def protocol(rawdata, lora_q):
    global lora_detect
    global send_success ## 수신여부 성공했을때
    global sending_data
    global accumulate
    tmp = ''.join(rawdata)    
    if "RECV" in tmp: ## 어떤 데이터를 받게 되며
        recv_eui = tmp.split(":")[1]
        p = tmp.split(":")[3]
        recvdata = tmp.split(":")[4]
        log.info("protocol is {}".format(p))
        if p == "DETECT":
            log.info("LoRa: receving data {}".format(recvdata))
            if recvdata == "LIGHTON":
                lora_detect = True
                sending_data += "{}:RECV ".format(p)
                accumulate = 0
                lora_q.put(True)
            if recvdata == "LIGHTOFF":
                lora_detect = False
                sending_data += "{}:RECV ".format(p)
                lora_q.put(False)
            if recvdata == "RECV":
                log.info("past command send okay")
                send_success += "{}_True".format(recv_eui)
        elif p == "LOCATE":
             ## LOCATE 프로토콜은 위도 경도 순서로 보내지며 해당 프로토콜은 타 보드의 위치정보를 저장하는 용도로 사용된다.
            goal_latitude = recvdata.split(",")[0]
            goal_longitude = recvdata.split(",")[1]
            goal_latitude  = float(goal_latitude)
            goal_longitude = float(goal_longitude)
            goal = (goal_latitude, goal_longitude)
            distance = haversine(start, goal, unit='m') ## 위도 경도를 이용하여 거리를 계산한다.
            log.info("LoRa : distance between {0} and me is {1}".format(sender_eui, distance))
            sending_data += "{}:RECV ".format(p)
        elif p == "RANGE":
            recvdata = tmp.split(":")[4]
            # RANGE 프로토콜은 객체 검출 시 사용되는 거리 민감도수정 값을 반환한다
            dist_range = float(recvdata)
            log.info("LoRa : change distance to send detection data")
            log.info("LoRa : distance range changed {}".format(dist_range))
        if recvdata == "RECV":
            send_success = True
            log.info("LoRa : Locate data sending success")

#쓰레드 종료용 시그널 함수
def handler(signum, frame):
    global exitThread
    exitThread = True

#본 쓰레드
def readThread(ser, lora_q, detect_q, exitThread):
    global line
    global lock
    global on_state
    global lora_detect
    global sending_data

    detect_ret = False
    ## 초기화
    # 쓰레드 종료될때까지 계속 돌림
    on_state = False

    lock = threading.Lock()
    while not exitThread:
        lock.acquire()
        if not detect_q.empty():
            detect_ret = detect_q.get()
            if detect_ret:
                on_state = True
                sending_data += "DETECT:LIGHTON "
            elif on_state:
                sending_data += "DETECT:LIGHTOFF "
        lock.release()
            
        
        #데이터가 있있다면
        for c in ser.read():
            #line 변수에 차곡차곡 추가하여 넣는다.
            line.append(chr(c))
            if c == 10: #라인의 끝을 만나면..
                #데이터 처리 함수로 호출
                protocol(line, lora_q)
                del line[:]
        lock.acquire()
        lora_q.put(lora_detect)
        lock.release()
        if sending_data:
            for command in sending_data.split():
                for eui in sender_eui.split():
                    log.info("Sending command {0}:{1}".format(eui, command))
                    ser.write(bytes(("AT+DATA={0}:{1}:\r\n").format(eui, command),'ascii'))
                    time.sleep(0.034)
                sending_data.rstrip(command)

if __name__ == "__main__":
    global lock
    #종료 시그널 등록
    signal.signal(signal.SIGINT, handler)
    #시리얼 열기
    ser = serial.Serial(port, baud, timeout=0)
    lora_share_queue = queue.Queue(1)
    detect_share_queue = queue.Queue(1)


    #시리얼 읽을 쓰레드 생성
    lorathread = threading.Thread(target=readThread, args=(ser,lora_share_queue,detect_share_queue, exitThread))
    detectthread = threading.Thread(target=detectThread, args=(lora_share_queue, detect_share_queue, exitThread))
    #시작!
    lorathread.start()
    detectthread.start()
