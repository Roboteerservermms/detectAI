# importing vlc module
import vlc
import crolling, schedule, queue
import os, subprocess

video_dir="./playlist"
video_path="./playlist/"
on_state = False


def insert_media():
    media_list = instance.media_list_new()
    for m in os.listdir(video_dir):
        media = instance.media_new(video_path + m)
        media_list.add_media(media)
    medialistplayer.set_media_list(media_list)
    instance.vlm_set_loop("playlist", True)

def str2bool(v):
   return str(v).lower() in ("yes", "true", "t", "1")

def MainThread(exitThread, media_insert_sig):
    global instance
    instance = vlc.Instance('--input-repeat=-1', '--fullscreen')
    global medialistplayer
    medialistplayer = instance.media_list_player_new()
    mediaplayer = instance.media_player_new()
    mediaplayer.set_fullscreen(True)
    medialistplayer.set_media_player(mediaplayer)
    insert_media()
    while exitThread:
        if media_insert_sig.get():
            insert_media()
        object_detect = str2bool(subprocess.getoutput('cat /sys/class/gpio/gpio65/value'))
        if object_detect:
            if not on_state:
                medialistplayer.play()
            on_state =True
            
        else:
            if on_state:
                on_state = False
                medialistplayer.pause()

#쓰레드 종료용 시그널 함수
def handler(signum, frame):
    global exitThread
    exitThread = True

if __name__ == "__main__":
    media_insert_sig = queue.Queue()
    media_insert_sig.put(True)
    MainThread(exitThread, media_insert_sig)
    