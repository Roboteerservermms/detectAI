#!/bin/bash
echo "Start detection_gpio.sh!"
GPIO=65
QRNG=$(dmesg | grep qrng | grep error)
GPIO_DIR=$(ls /sys/class/gpio/ | grep 65)

echo "Checking QRNG Security key"
if [ -z $QRNG ]; then
	echo "Please Check Security key!"
	exit 255
else
	echo "Found Security key!"
fi
if [ -z $GPIO_DIR ]; then
	echo "Start GPIO Running!"
	echo $GPIO > /sys/class/gpio/export
	echo "out" > /sys/class/gpio/gpio$GPIO/direction
else
	echo "GPIO already exist from past error"
	echo $GPIO > /sys/class/gpio/unexport
	sleep 2
	echo $GPIO > /sys/class/gpio/export
	echo "out" > /sys/class/gpio/gpio$GPIO/direction
fi

export PYTHONPATH=/data/edgetpu/
cd /data/edgetpu/edgetpu/demo/
python3 /data/edgetpu/edgetpu/demo/detection_gpio.py
