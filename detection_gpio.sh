#!/bin/bash
timedatectl set-timezone Asia/Seoul
amixer cset -c 0 numid=10,iface=MIXER,name='LINEOUT Volume' 18.6
chmod 775 /sys/class/gpio/export
chmod 775 /sys/class/gpio/unexport
echo "Start AI Detection!"
for gpio in "65" "68" "70" "71" "72" "74" "111" "112" "113"; do
    GPIO_DIR=$(ls /sys/class/gpio/ | grep ${gpio})
    if [ -n "$GPIO_DIR" ]; then
            echo "GPIO already exist from past error"
            echo ${gpio} > /sys/class/gpio/unexport
            sleep 1
    fi
    echo ${gpio} > /sys/class/gpio/export
    sleep 1
    echo "out" > /sys/class/gpio/gpio${gpio}/direction
done
export PYTHONPATH="/home/orangepi/detectAI"
export PYTHONIOENCODING=UTF-8
cd $PYTHONPATH
git pull
if [ $? -eq 0 ];then
    echo "code update is running!"
else
    echo "internet does not connected"
fi
python3 detect.py & 
echo "camera start!" &
python3 LoRa.py & 
echo "LoRa start!"&
python3 video.py & 
filebrowser -a 10.42.0.1 -r ./filecontrol/



