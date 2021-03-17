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
import os


def ReadLabelFile(file_path):
    with open(file_path, 'r') as (f):
        lines = f.readlines()
    ret = {}
    for line in lines:
        pCamerar = line.strip().split(maxsplit=1)
        ret[int(pCamerar[0])] = pCamerar[1].strip()
    return ret

def ious(box1):
  #[x1, y1, x2, y2]
  box1 = np.array(box1)
  def inner_iou(box2):
    box2 = np.array(box2)
    inter_upleft = np.maximum(box1[..., :2], box2[:2])
    inter_botright = np.minimum(box1[..., 2:4], box2[2:4])
    inter_wh = inter_botright - inter_upleft
    inter = inter_wh[:, 0] * inter_wh[:, 1]
    area_target = (box2[2] - box2[0]) * (box2[3] - box2[1])
    area_box1 = (box1[..., 2] - box1[..., 0])
    area_box1 *= (box1[..., 3] - box1[..., 1])
    union = area_target + area_box1 - inter
    iou = inter / union
    return iou
  return inner_iou


def detectThread(exitThread):
    global accumulate, on_state, num_gpio, threshold

    num_gpio = 111
    threshold = 60

    log = logging.getLogger('detect')
    log.setLevel(logging.DEBUG)
    log_handler = logging.StreamHandler()
    log.addHandler(log_handler)
    
    log.info('Detection start')
    threshold = threshold / 100
    engine = DetectionEngine('models.tflite')
    labelfile = 'labels.txt'
    labels = ReadLabelFile(labelfile) if labelfile else None
    labelids = labels.keys()
    cap = cv2.VideoCapture(0)
    #cap = cv2.VideoCapture("./0724/vehicle_20m_01.mp4")
    accumulate = 0
    on_state = False
    detect = 0
    frames = 0
    path = "./snapshot/"
    
    # detection for moving vehicle
    store_boxes = [] # past boxes for calculating IOU
    curr_boxes = [] # boxes in current frame
    num_store = 4
    ret_ious = [0] * num_store # ious between (current-2 and current), (current-1 and current) frames
    moving_threshold = [0.5, 0.80]
    
    class State(object):
        count = 0
        def __init__(self, logger):
            self.logger = logger
        
        def update_state(self, on=None, on_state=None):
            if on is not None and on_state is not None:
                if on:
                    if not on_state:
                        on_state = True
                        self.logger.info("Camera: light's on")
                        accumulate = 0
                        os.system('echo 1 > /sys/class/gpio/gpio{}/value'.format(num_gpio))
                        return on_state
                else:
                    if on_state:
                        on_state = False
                        return on_state
        def save_img_file(self, img=""):
            disk_usage=int(subprocess.getoutput("bash check_disk_percent.sh"))
            img_file_name = '{0}{1}.bmp'.format(path, self.count)
            if img_file_name == subprocess.getoutput("ls | grep {}".format(img_file_name)):
                if disk_usage < 96:
                    self.count += 1
                    self.save_img_file()
                else : 
                    count = 0
                    os.system("rm -rf {}".format(path))
                    img.save(img_file_name, 'BMP')
                    return 0
            else:
                img.save(img_file_name, 'BMP')
                count += 1
                return 0
    
    state = State(log)
    count = 0
    while not exitThread:
        ret, frame = cap.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        fontsize = 20
        font = ImageFont.truetype('Ubuntu-L.ttf', fontsize)
        draw = ImageDraw.Draw(img)
        time_start = time.time()*1000
        ans = engine.detect_with_image(img, threshold=threshold, keep_aspect_ratio=True, relative_coord=False, top_k=10)
        draw.text(xy=(30, 10), text='frame: {}'.format(frames), font=ImageFont.truetype('Ubuntu-L.ttf', 20), fill=(255,255,0))
        frames += 1
        if ans:
            detect = 1
            for obj in ans:
                if obj.label_id in labelids:
                    box = obj.bounding_box.flatten().tolist()
                    draw.text(xy=(box[0], box[1] - (fontsize + 1)), text=(labels[obj.label_id]), font=font)
                    draw.text(xy=(box[0], box[1] - (fontsize + 1) * 2), text="{}ms".format(int(time.time()*1000 - time_start)), font=font)
                    draw.rectangle(box, outline='yellow')
                    if obj.label_id == 0:
                        if detect == 1:
                            accumulate = 0
                            detect = 0
                            on_state = state.update_state(on=True, on_state=on_state)
                            state.save_img_file(img=img)
                    else:
                        curr_boxes.append(box)



        # detection for moving vehicle
        store_boxes.append(np.expand_dims(np.array(curr_boxes), axis=0))
        curr_boxes = []
        
        if len(store_boxes) > num_store:
            del store_boxes[0]
            
            for i in range(num_store - 1):
                if store_boxes[i].any() and store_boxes[-1].any():
                    ret_ious[i] = np.apply_along_axis(ious(store_boxes[i].reshape((-1, 4))), 1, store_boxes[-1].reshape((-1, 4)))
                else:
                    ret_ious[i] = np.array([])
            
            is_moving = ret_ious.copy()
            for moving in is_moving:
                moving = np.asarray(moving)
                moving = moving[moving > moving_threshold[0]]
                moving = moving[moving <= moving_threshold[1]]
                if moving.any():
                    print("vehicle is moving")
                    if detect == 1:
                      accumulate = 0
                      detect = 0
                      os.system('echo 1 > /sys/class/gpio/gpio{}/value'.format(num_gpio))
                      on_state = state.update_state(on=True, on_state=on_state)
                      state.save_img_file(img=img)
                    break
        
        frame = np.array(img)
        frame = frame[:, :, ::-1].copy()
        cv2.imshow('detection', frame)
        if cv2.waitKey(1) == 27:
            log.error('exit program')
            break
        
if __name__ == '__main__':
    global ontime
    ontime = 10
    exitThread = False
    #종료 시그널 등록
    detectThread(exitThread)
