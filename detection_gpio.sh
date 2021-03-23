#!/bin/bash
timedatectl set-timezone Asia/Seoul
chmod 775 /sys/class/gpio/export
chmod 775 /sys/class/gpio/unexport
echo "Start AI Detection!"
for gpio in "65" "74" "111" "112" "113"; do
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
echo 1 > /sys/class/gpio/gpio74/value ## to control relay
export PYTHONPATH="/home/orangepi/detectAI"
cd $PYTHONPATH
python3 detect.py & 
echo "camera start!" &
python3 LoRa.py & 
echo "LoRa start!" &
python3 server/app.py &
echo "server start!"


