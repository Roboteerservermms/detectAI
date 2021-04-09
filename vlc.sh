video_list=$(ls -tr ./playlist/)
for num in $video_list; do
    sudo -u orangepi -H sh -c "vlc  --loop --fullscreen --video-on-top --one-instance --playlist-enqueue ./playlist/$num"
done
sudo -u orangepi -H sh -c "vlc-ctrl pause"