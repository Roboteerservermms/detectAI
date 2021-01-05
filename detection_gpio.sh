#!/bin/bash
modprobe usbserial vendor=0x067b product=0x2303
chmod 775 /sys/class/gpio/export
chmod 775 /sys/class/gpio/unexport
echo "Start AI Detection!"
GPIO=65
QRNG=$(hexdump -C /dev/qrng-char -n 10)
GPIO_DIR=$(ls /sys/class/gpio/ | grep 65)

echo "Checking QRNG Security key"
if [ -n "$QRNG" ]; then
        echo "Found Security key!"
else
	echo "Please Check Security key!"
        exit 255
        
fi
if [ -z "$GPIO_DIR" ]; then
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
export PYTHONPATH="/home/orangepi/detectAI"
cd $PYTHONPATH
python3 LoRa.py

