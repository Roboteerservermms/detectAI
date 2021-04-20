# importing vlc module
# -*- coding: UTF-8 -*-
import vlc
import weather, schedule, signal
import os, subprocess, time

video_dir="./filecontrol/playlist"
video_path="./filecontrol/playlist/"
def insert_media():
    media_list = instance.media_list_new()
    for m in os.listdir(video_dir):
        media = instance.media_new(video_path + m)
        media_list.add_media(media)
    medialistplayer.set_media_list(media_list)
    instance.vlm_set_loop("playlist", True)

def str2bool(v):
   return str(v).lower() in ("yes", "true", "t", "1")

def setMarquee(mediaplayer):
    mediaplayer.video_set_marquee_string(vlc.VideoMarqueeOption.Text, weather.test_func())

def MainThread(exitThread):
    on_state = False
    global instance
    instance = vlc.Instance('--input-repeat=-1', '--fullscreen')
    global medialistplayer
    past_video = os.listdir(video_dir)
    medialistplayer = instance.media_list_player_new()
    mediaplayer = instance.media_player_new()
    mediaplayer.set_fullscreen(True)
    mediaplayer.video_set_marquee_int(vlc.VideoMarqueeOption.Enable, 1)
    mediaplayer.video_set_marquee_int(vlc.VideoMarqueeOption.Size, 24)  # pixels
    mediaplayer.video_set_marquee_int(vlc.VideoMarqueeOption.Position, 4)
    mediaplayer.video_set_marquee_int(vlc.VideoMarqueeOption.Timeout, 0) 
    mediaplayer.video_set_marquee_int(vlc.VideoMarqueeOption.Refresh, 1000)
    mediaplayer.video_set_marquee_string(vlc.VideoMarqueeOption.Text, weather.test_func())
    schedule.every(40).minutes.do(setMarquee,mediaplayer)
    insert_media()
    medialistplayer.set_media_player(mediaplayer)
    medialistplayer.play()
    time.sleep(1)
    medialistplayer.pause()
    while not exitThread:
        schedule.run_pending()
        object_detect = str2bool(subprocess.getoutput('cat /sys/class/gpio/gpio65/value'))
        if object_detect:
            if not on_state:
                medialistplayer.play()
            on_state =True
            
        else:
            if on_state:
                on_state = False
                medialistplayer.pause()
        if past_video != os.listdir(video_dir):
            insert_media()
        

#쓰레드 종료용 시그널 함수
def handler(signum, frame):
    global exitThread
    exitThread = True

if __name__ == "__main__":
    exitThread=False
    MainThread(exitThread)
    