import datetime
import subprocess
import threading
from edgetpu.detection.engine import DetectionEngine
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import cv2, numpy as np, time
import logging

from flask import Response
from flask import Flask
from flask import render_template
import argparse

outputFrame = None
lock = threading.Lock()
app = Flask(__name__)

@app.route("/")
def index():
    # return the rendered template
    return render_template("index.html")

def ReadLabelFile(file_path):
    with open(file_path, 'r') as (f):
        lines = f.readlines()
    ret = {}
    for line in lines:
        pCamerar = line.strip().split(maxsplit=1)
        ret[int(pCamerar[0])] = pCamerar[1].strip()
    return ret

log = logging.getLogger('detect')
log.setLevel(logging.DEBUG)
log_handler = logging.StreamHandler()
log.addHandler(log_handler)

img_file_path= './snapshot/'

log.info('Detection start')
threshold = 0.6
engine = DetectionEngine('models.tflite')
labelfile = 'labels.txt'
labels = ReadLabelFile(labelfile) if labelfile else None
labelids = labels.keys()

cap = cv2.VideoCapture(0)
time.sleep(2.0)

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

def detect_filesave(img, object):
    now= datetime.datetime.now()
    img_file_name = '{0}{1}{2}.jpg'.format( img_file_path,now.strftime("%Y_%m_%d-%H_%M_%S"),object)
    img.save(img_file_name, "JPEG", quality=80, optimize=True, progressive=True)
    subprocess.getoutput("sync")

def generate():
    # grab global references to the output frame and lock variables
    global outputFrame, lock
    # loop over frames from the output stream
    while True:
        # wait until the lock is acquired
        with lock:
            # check if the output frame is available, otherwise skip
            # the iteration of the loop
            if outputFrame is None:
                continue
            # encode the frame in JPEG format
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
            # ensure the frame was successfully encoded
            if not flag:
                continue
        # yield the output frame in the byte format
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
            bytearray(encodedImage) + b'\r\n')

@app.route("/video_feed")
def video_feed():
    # return the response generated along with the specific media
    # type (mime type)
    return Response(generate(),
        mimetype = "multipart/x-mixed-replace; boundary=frame")

def detectThread(exitThread):
    global  threshold, engine, labelids,vs

    try :
        detect = 0
        frames = 0

        # detection for moving vehicle
        store_boxes = [] # past boxes for calculating IOU
        curr_boxes = [] # boxes in current frame
        num_store = 4
        ret_ious = [0] * num_store # ious between (current-2 and current), (current-1 and current) frames
        moving_threshold = [0.5, 0.80]

        while not exitThread:
            ret, frame = cap.read()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            fontsize = 5
            font = ImageFont.truetype('./NanumGothic.ttf', fontsize)
            draw = ImageDraw.Draw(img)
            time_start = time.time()*1000
            ans = engine.detect_with_image(img, threshold=threshold, keep_aspect_ratio=True, relative_coord=False, top_k=10)
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
                                detect = 0
                                detect_filesave(img,object="person")
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
                            detect = 0
                            detect_filesave(img,object="moving_vehicle")
                        break

            frame = np.array(img)
            with lock:
                outputFrame = frame[:, :, ::-1].copy()
    except cv2.error as error:
        log.error("[Error]: {}".format(error))

if __name__ == '__main__':
    exitThread = False
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--ip", type=str, required=True,
        help="ip address of the device")
    ap.add_argument("-o", "--port", type=int, required=True,
        help="ephemeral port number of the server (1024 to 65535)")
    args = vars(ap.parse_args())
    t = threading.Thread(target=detectThread, args=(
        exitThread,))
    t.daemon = True
    t.start()
    # start the flask app
    app.run(host=args["ip"], port=args["port"], debug=True,
        threaded=True, use_reloader=False)
vs.stop()