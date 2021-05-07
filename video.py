# importing vlc module
# -*- coding: UTF-8 -*-
import vlc
import weather, schedule, signal, logging
import os, subprocess, time, pafy
import pandas as pd
log = logging.getLogger('detect')
log.setLevel(logging.DEBUG)
log_handler = logging.StreamHandler()
log.addHandler(log_handler)

video_dir="./filecontrol/playlist"
video_path="./filecontrol/playlist/"
def insert_media():
    media_list = instance.media_list_new()
    try:
        mrl = pd.read_csv("./filecontrol/broadcastlink.csv", encoding='utf-8')
    except pd.errors.EmptyDataError:
        media_list = instance.media_list_new()
        for m in os.listdir(video_dir):
            media = instance.media_new(video_path + m)
            media_list.add_media(media)
        medialistplayer.set_media_list(media_list)
        return 0
    f_line = mrl[mrl['실행여부'].str.contains("play", na=False)]
    broadcast_url =  f_line[["url"]].values[0][0]
    media = instance.media_new(broadcast_url)
    # elif broadcast_url.find("youtube"):
    #     video = pafy.new(broadcast_url)
    #     best = video.getbest()
    #     media = instance.media_new(best.url)
    media_list.add_media(media)
    medialistplayer.set_media_list(media_list)


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
    medialistplayer.set_playback_mode(vlc.PlaybackMode.loop)
    mediaplayer.video_set_marquee_int(vlc.VideoMarqueeOption.Enable, 1)
    mediaplayer.video_set_marquee_int(vlc.VideoMarqueeOption.Size, 24)  # pixels
    mediaplayer.video_set_marquee_int(vlc.VideoMarqueeOption.Position, 4)
    mediaplayer.video_set_marquee_int(vlc.VideoMarqueeOption.Timeout, 0) 
    mediaplayer.video_set_marquee_int(vlc.VideoMarqueeOption.Refresh, 1000)
    try:
        mediaplayer.video_set_marquee_string(vlc.VideoMarqueeOption.Text, weather.test_func())
    except:
        log.info("internet is not connected")
    schedule.every(40).minutes.do(setMarquee,mediaplayer)
    insert_media()
    medialistplayer.set_media_player(mediaplayer)
    time.sleep(10)
    medialistplayer.play()
    time.sleep(1)
    medialistplayer.pause()
    while not exitThread:
        try:
            schedule.run_pending()
        except:
            log.info("internet is not connected")
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
    