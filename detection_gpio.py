# uncompyle6 version 3.6.4
# Python bytecode 3.6 (3379)
# Decompiled from: Python 2.7.17 (default, Jul 20 2020, 15:37:01)
# [GCC 7.5.0]
# Warning: this version has problems handling the Python 3 byte type in contants properly.

# Embedded file name: detection_gpio.py
# Compiled at: 2020-03-24 12:16:10
# Size of source mod 2**32: 3979 bytes
import argparse, platform, subprocess
from edgetpu.detection.engine import DetectionEngine
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import signal
import threading
import cv2, numpy as np, time, os
import sys
sys.path.append('./LoRa.py')
from LoRa import *

def ReadLabelFile(file_path):
    with open(file_path, 'r') as (f):
        lines = f.readlines()
    ret = {}
    for line in lines:
        pair = line.strip().split(maxsplit=1)
        ret[int(pair[0])] = pair[1].strip()

    return ret


def main():
    global accumulate, on_state
    global num_gpio, ontime, threshold

    num_gpio = 65
    ontime = 30
    threshold = 60

    print('Now using gpio{}'.format(num_gpio))
    arg_ontime = int(ontime)
    if not arg_ontime > 0:
        raise AssertionError
    time.sleep(3)

    print('Detection start')
    threshold = threshold / 100
    engine = DetectionEngine('human0716.tflite')
    labelfile = 'labels.txt'
    labels = ReadLabelFile(labelfile) if labelfile else None
    labelids = labels.keys()
    cap = cv2.VideoCapture(0)
    neg = True
    accumulate = 0
    on_state = False
    t_cur_1 = int(round(time.time() * 1000))
    t_cur_2 = int(round(time.time() * 1000))
    while neg:
        if on_state:
            accumulate += t_cur_2 - t_cur_1
        else:
            accumulate = 0
        t_cur_1 = int(round(time.time() * 1000))
        frame = cap.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        fontsize = 10
        font = ImageFont.truetype('Ubuntu-L.ttf', fontsize)
        draw = ImageDraw.Draw(img)
        ans = engine.DetectWithImage(img, threshold=threshold, keep_aspect_ratio=True, relative_coord=False, top_k=10)
        if ans:
            detect = 1
            for obj in ans:
                if obj.label_id in labelids:
                    box = obj.bounding_box.flatten().tolist()
                    draw.text(xy=(box[0], box[1] - (fontsize + 1)), text=(labels[obj.label_id]), font=font)
                    draw.rectangle(box, outline='yellow')
                    if obj.label_id == 0:
                        if detect == 1:
                            accumulate = 0
                            detect = 0
                            if not on_state:
                                    on_state = True
                                    print("light's on")
                                    os.system('sudo echo 1 > /sys/class/gpio/gpio{}/value'.format(num_gpio))
                                    accumulate = 0
                else:
                    neg = True
                if accumulate >= arg_ontime * 1000:
                    if on_state:
                        on_state = False
                        print("light's off")
                        os.system('sudo echo 0 > /sys/class/gpio/gpio{}/value'.format(num_gpio))
        else:
            neg = True
            if accumulate >= arg_ontime * 1000:
                if on_state:
                    on_state = False
                    print("light's off")
                    os.system('sudo echo 0 > /sys/class/gpio/gpio{}/value'.format(num_gpio))

        frame = np.array(img)
        frame = frame[:, :, ::-1].copy()
        cv2.imshow('detection', frame)
        if cv2.waitKey(1) == 27:
            print('exit program')
            os.system('sudo echo {} > /sys/class/gpio/unexport'.format(num_gpio))
            break
        t_cur_2 = int(round(time.time() * 1000))


if __name__ == '__main__':
    main()
