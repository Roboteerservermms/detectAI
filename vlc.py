import os, subprocess
import signal, threading
import logging
log = logging.getLogger('detect')
log.setLevel(logging.DEBUG)
log_handler = logging.StreamHandler()
log.addHandler(log_handler)

def str2bool(v):
   return str(v).lower() in ("yes", "true", "t", "1")

def handler(signum, frame):
    global exitThread
    exitThread = True

def play_and_pause(exitThread):
    os.system("bash vlc.sh")
    object_detect = str2bool(subprocess.getoutput('cat /sys/class/gpio/gpio65/value'))
    while exitThread:
        if object_detect:
            os.system("vlc-ctrl play")
        else:
            os.system("vlc-ctrl pause")



if __name__ == "__main__":
    exitThread = False
    #종료 시그널 등록
    signal.signal(signal.SIGINT, handler)
    #시리얼 열기
    #시리얼 읽을 쓰레드 생성
    log.info("vlc play running!")
    
    vlc_player = threading.Thread(target=play_and_pause, args=(exitThread))
    #시작!
    vlc_player.start()
