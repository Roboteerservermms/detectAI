import vlc, subprocess
import pafy
import urllib.request

def str2bool(v):
   return str(v).lower() in ("yes", "true", "t", "1")

url = "https://youtu.be/GoXPbGQl-uQ"

video = pafy.new(url)
best = video.getbest()
playurl = best.url
ins = vlc.Instance()
player = ins.media_player_new()

code = urllib.request.urlopen(url).getcode()
if str(code).startswith('2') or str(code).startswith('3'):
    print('Stream is working')
else:
    print('Stream is dead')

Media = ins.media_new(playurl)
Media.get_mrl()
player.set_media(Media)
player.play()
light = ""
good_states = ["State.Playing", "State.NothingSpecial", "State.Opening"]
while str(player.get_state()) in good_states:
    light = str2bool(subprocess.getoutput('cat /sys/class/gpio/gpio65/value'))
    if not light:
        player.pause()
