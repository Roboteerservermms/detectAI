import vlc, subprocess

vlc_instance = vlc.Instance('--fullscreen')
player = vlc_instance.media_player_new()
media = vlc_instance.media_new('video.mp4')
player.set_media(media)    
on_state = False
def play():
