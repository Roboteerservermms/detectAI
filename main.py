
def init():
    log.info("Initialize System to AI Detect!")
    start = (start_latitude, start_longitude)
    log.info("LoRa:my latitiude longtitude = {}".format(start))
    ## 내가 누구인가
    ser.write(bytes(("AT+GEUI\r\n"),'ascii'))
        for c in ser.read():
        #line 변수에 차곡차곡 추가하여 넣는다.
        line.append(chr(c))
        if c == 10: #라인의 끝을 만나면..
            #데이터 처리 함수로 호출
            rawdata= ''.join(line)
            if find(rawdata)
                me = rawdata
            del line[:] 

if __name__ == "__main__":
    global lock
    start = (start_latitude, start_longitude)
    log.info("LoRa:my latitiude longtitude = {}".format(start))

    #종료 시그널 등록
    signal.signal(signal.SIGINT, handler)
    #시리얼 열기
    ser = serial.Serial(port, baud, timeout=0)
    lock = threading.Lock()
    detect_share_queue = queue.Queue(1)
    time_share_queue = queue.Queue(1)




    #시리얼 읽을 쓰레드 생성
    lorathread = threading.Thread(target=readThread, args=(ser,share_queue))
    detectthread = threading.Thread(target=detectThread, args=(share_queue, exitThread))
    #시작!
    lorathread.start()
    detectthread.start()