import serial
import time
import signal
import threading
from haversine import haversine
from detect import *

line = [] #라인 단위로 데이터 가져올 리스트 변수

port = '/dev/ttyS3' # 시리얼 포트
baud = 115200 # 시리얼 보드레이트(통신속도)

exitThread = False   # 쓰레드 종료용 변수
start = (0,0)
distance = None
sender_eui = "1f9b23"
exitThread = False

def protocol(tmp):
    if "RECV" in tmp: ## 어떤 데이터를 받게 되며
        sender_eui = tmp.split(":")[1]
        p = tmp.split(":")[3]
        print("protocol is {}".format(p))

        if p == "DETECT":
            lighton()
        elif p == "LOCATE":
            recvdata = tmp.split(":")[4]
             ## LOCATE 프로토콜은 위도 경도 순서로 보내지며 해당 프로토콜은 타 보드의 위치정보를 저장하는 용도로 사용된다.
            goal_latitude = recvdata.split(",")[0]
            goal_longitude = recvdata.split(",")[1]
            goal_latitude  = float(goal_latitude)
            goal_longitude = float(goal_longitude)
            goal = (goal_latitude, goal_longitude)
            distance = haversine(start, goal, unit='m') ## 위도 경도를 이용하여 거리를 계산한다.
            print("distance between {0} and me is {1}".format(sender_eui, distance))
            #ser.write(bytes("AT+DATA={0}:{1}".format(sender_eui, start),encoding='ascii'))

        elif p == "RANGE":
            recvdata = tmp.split(":")[4]
            # RANGE 프로토콜은 객체 검출 시 사용되는 거리 민감도수정 값을 반환한다
            dist_range = float(recvdata)
            print("change distance to send detection data")
            print("distance range changed {}".format(dist_range))

#쓰레드 종료용 시그널 함수
def handler(signum, frame):
    exitThread = True

#데이터 처리할 함수
def parsing_data(rawdata):
    # 리스트 구조로 들어 왔기 때문에
    # 작업하기 편하게 스트링으로 합침
    tmp = ''.join(rawdata)
    #출력!
    protocol(tmp)
    print(tmp)

#본 쓰레드
def loraThread(ser, exitThread):
    global line
    ## 초기화

    # 쓰레드 종료될때까지 계속 돌림
    while not exitThread:
        #데이터가 있있다면
        lock.acquire()
        for c in ser.read():
            #line 변수에 차곡차곡 추가하여 넣는다.
            line.append(chr(c))
            if c == 10: #라인의 끝을 만나면..
                #데이터 처리 함수로 호출
                parsing_data(line)
                del line[:]
        lock.release()



if __name__ == "__main__":

    start_latitude, start_longitude = input("위도와 경도를 입력하세요: ").split(",")
    start_latitude = float(start_latitude)
    start_longitude = float(start_longitude)
    start = (start_latitude, start_longitude)
    print("내 위도 경도는 {}".format(start))

    #종료 시그널 등록
    signal.signal(signal.SIGINT, handler)
    #시리얼 열기
    global ser = serial.Serial(port, baud, timeout=0)
    lock = threading.Lock()
    #시리얼 읽을 쓰레드 생성
    thread = threading.Thread(target=loraThread, args=(ser,exitThread))
    thread = threading.Thread(target=detectThread, args=(ser,exitThread))
    #시작!
    thread.start()
