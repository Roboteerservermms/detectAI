#!/bin/bash
chmod 775 /sys/class/gpio/export
chmod 775 /sys/class/gpio/unexport
echo "Start AI Detection!"
for gpio in "65" "111" "112" "113"; do
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
cd $PYTHONPATH
echo "compile pir!"
g++ -o pir pir.cpp -std=c++11
pir=$(./pir /dev/ttyS2)
echo "load program!"
python3 LoRa.py && $pir

