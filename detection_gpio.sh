#!/bin/bash
chmod 775 /sys/class/gpio/export
chmod 775 /sys/class/gpio/unexport
echo "Start AI Detection!"
GPIO=65
QRNG=$(dmesg | grep qrng | grep error)
GPIO_DIR=$(ls /sys/class/gpio/ | grep 65)

echo "Checking QRNG Security key"
if [ $QRNG ]; then
        echo "Please Check Security key!"
        exit 255
else
        echo "Found Security key!"
fi
if [ -z $GPIO_DIR ]; then
        echo "Start GPIO Running!"
        echo "$GPIO" > /sys/class/gpio/export
        sleep 5
        echo "out" > /sys/class/gpio/gpio$GPIO/direction
else
        echo "GPIO already exist from past error"
        echo "$GPIO" > /sys/class/gpio/unexport
        sleep 5
        echo "$GPIO" > /sys/class/gpio/export
        sleep 5
        echo "out" > /sys/class/gpio/gpio$GPIO/direction
fi
export PYTHONPATH="/home/orangepi/"
cd /home/orangepi/
python3 /home/orangepi/LoRa.py

