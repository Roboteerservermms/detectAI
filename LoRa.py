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
eui_data = {"1f9b23":{"":False}, "1f9b25":{"":False}, "1f9f0f":{"":False}}
start_latitude, start_longitude = 37.540166, 127.056670
lora_detect = False
sending_data = {"":False}
log = logging.getLogger('detect')
log.setLevel(logging.DEBUG)
log_handler = logging.StreamHandler()
log.addHandler(log_handler)

def protocol(rawdata):
    global lora_detect
    global sending_data

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
                eui_data[recv_eui]["{}:RECV".format(p)] = False
        elif p == "LOCATE":
             ## LOCATE 프로토콜은 위도 경도 순서로 보내지며 해당 프로토콜은 타 보드의 위치정보를 저장하는 용도로 사용된다.
            goal_latitude = recvdata.split(",")[0]
            goal_longitude = recvdata.split(",")[1]
            goal_latitude  = float(goal_latitude)
            goal_longitude = float(goal_longitude)
            goal = (goal_latitude, goal_longitude)
            distance = haversine(start, goal, unit='m') ## 위도 경도를 이용하여 거리를 계산한다.
            log.info("LoRa : distance between {0} and me is {1}".format(eui_data, distance))

        elif p == "RANGE":
            recvdata = tmp.split(":")[4]
            # RANGE 프로토콜은 객체 검출 시 사용되는 거리 민감도수정 값을 반환한다
            dist_range = float(recvdata)
            log.info("LoRa : change distance to send detection data")
            log.info("LoRa : distance range changed {}".format(dist_range))

        if recvdata == "RECV":
            eui_data[recv_eui]["{}:LIGHTON".format(p)] = True
            log.info("command is sucess")


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

    ## 수신여부 성공했을때
    detect_ret = False
    ## 초기화
    # 쓰레드 종료될때까지 계속 돌림
    on_state = False

    lock = threading.Lock()
    while not exitThread:
        lock.acquire()
        if not detect_q.empty():
            detect_ret = detect_q.get()
            for eui in eui_data.keys():
                if detect_ret:
                    for eui in eui_data.keys():
                        eui_data[eui]["DETECT:LIGHTON"] = False
        lock.release()
        #데이터가 있있다면
        for c in ser.read():
            #line 변수에 차곡차곡 추가하여 넣는다.
            line.append(chr(c))
            if c == 10: #라인의 끝을 만나면..
                #데이터 처리 함수로 호출
                protocol(line)
                del line[:]
        lock.acquire()
        lora_q.put(lora_detect)
        lock.release()
        
        for eui in eui_data.keys():
            for command in eui_data[eui].keys():
                if eui_data[eui][command]:
                    log.info("{0}:{1} command's success is {2}".format(eui, command, sending_data.pop(command)))
                    del eui_data[eui][command]
                    eui_data[eui] = {"":False} 
                else:
                    if command:
                        if "RECV" in command:
                            ser.write(bytes(("AT+DATA={0}:{1}:\r\n").format(eui, command),'ascii'))
                            del eui_data[eui][command]
                            eui_data[eui] = {"":False}
                        else:
                            ser.write(bytes(("AT+DATA={0}:{1}:\r\n").format(eui, command),'ascii'))
                        time.sleep(0.044)
                        log.info("{0} send to {1}".format(command, eui))
            

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
