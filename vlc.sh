video_list=$(ls -tr ./playlist/)
vlc  --loop --fullscreen --video-on-top --one-instance
for num in $video_list; do
    vlc  --playlist-enqueue ./playlist/$num
done