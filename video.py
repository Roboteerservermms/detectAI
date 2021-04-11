# importing vlc module
import vlc
import os, subprocess

video_dir="./playlist"
video_path="./playlist/"
on_state = False
instance = vlc.Instance('--input-repeat=-1', '--fullscreen', '--one-instance')
player = instance.media_list_player_new()
media_list = instance.media_list_new()
video_list = os.listdir(video_dir)
for v in video_list:
    media = instance.media_new(video_path + v)
    media_list.add_media(media)

player.set_media_list(media_list)

def str2bool(v):
   return str(v).lower() in ("yes", "true", "t", "1")

while True:
    object_detect = str2bool(subprocess.getoutput('cat /sys/class/gpio/gpio65/value'))
    if object_detect:
        if not on_state:
            player.play()
        on_state =True
        
    else:
        player.pause()