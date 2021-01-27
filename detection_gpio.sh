#!/bin/bash
chmod 775 /sys/class/gpio/export
chmod 775 /sys/class/gpio/unexport
echo "Start AI Detection!"
for gpio in "65" "74" "111" "113"; do
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

audio_gpio="112"
GPIO_DIR=$(ls /sys/class/gpio/ | grep ${audio_gpio})
if [ -n "$GPIO_DIR" ]; then
        echo "GPIO already exist from past error"
        echo ${audio_gpio} > /sys/class/gpio/unexport
        sleep 1
fi
echo ${audio_gpio} > /sys/class/gpio/export
sleep 1
echo "in" > /sys/class/gpio/gpio${audio_gpio}/direction

export PYTHONPATH="/home/orangepi/detectAI"
cd $PYTHONPATH
g++ -o pir pir.cpp -std=c++11
python3 detect.py & 
echo "camera start!" &
python3 LoRa.py & 
echo "LoRa start!" &
./pir /dev/ttyS2 &
echo "pir start!"


