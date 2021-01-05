import imp
import platform, subprocess
from edgetpu.detection.engine import DetectionEngine
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import signal
import threading
import cv2, numpy as np, time
import sys
import logging
import queue
import os
import time

def ReadLabelFile(file_path):
    with open(file_path, 'r') as (f):
        lines = f.readlines()
    ret = {}
    for line in lines:
        pair = line.strip().split(maxsplit=1)
        ret[int(pair[0])] = pair[1].strip()
    return ret


def detectThread(d_q ,exitThread):
    global accumulate, on_state, num_gpio, ontime, threshold

    num_gpio = 65
    ontime = 30
    threshold = 60

    log = logging.getLogger('detect')
    log.setLevel(logging.DEBUG)
    log_handler = logging.StreamHandler()
    log.addHandler(log_handler)
    
    log.info('Detection start')
    threshold = threshold / 100
    engine = DetectionEngine('human0716.tflite')
    labelfile = 'labels.txt'
    labels = ReadLabelFile(labelfile) if labelfile else None
    labelids = labels.keys()
    cap = cv2.VideoCapture(0)
    accumulate = 0
    on_state = False
    detect = 0
    lora_ret = False
    t_cur_1 = int(round(time.time()))
    t_cur_2 = int(round(time.time()))
    lock = threading.Lock()
    while not exitThread:
        if on_state:
            accumulate += t_cur_2 - t_cur_1
        else:
            accumulate = 0
        t_cur_1 = int(round(time.time() * 1000))
        ret, frame = cap.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        fontsize = 10
        font = ImageFont.truetype('Ubuntu-L.ttf', fontsize)
        draw = ImageDraw.Draw(img)
        ans = engine.detect_with_image(img, threshold=threshold, keep_aspect_ratio=True, relative_coord=False, top_k=10)
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
                            d_q.put(True)
                            if not on_state:
                                    on_state = True
                                    log.info("AI: light's on")
                                    os.system('echo 1 > /sys/class/gpio/gpio{}/value'.format(num_gpio))
                                    accumulate = 0
                                    frame = np.array(img)
                                    frame = frame[:, :, ::-1].copy()
                                    now = time.localtime()
                                    filename = "human_detect_%04d/%02d/%02d %02d:%02d.png"%(now.tm_year + now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min)
                                    cv2.imwrite(filename,frame)
                elif accumulate >= ontime * 1000:
                    if on_state:
                        on_state = False
                        log.info("light's off")
                        os.system('echo 0 > /sys/class/gpio/gpio{}/value'.format(num_gpio))
        else:
            if accumulate >= ontime * 1000:
                if on_state:
                    on_state = False
                    log.info("light's off")
                    os.system('echo 0 > /sys/class/gpio/gpio{}/value'.format(num_gpio))

        frame = np.array(img)
        frame = frame[:, :, ::-1].copy()
        cv2.imshow('detection', frame)
        if cv2.waitKey(1) == 27:
            log.error('exit program')
            break
        t_cur_2 = int(round(time.time() * 1000))