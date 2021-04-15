import queue
from flask import Flask, redirect, url_for, render_template, request, send_file, Response, session
from werkzeug.utils import secure_filename
import os, subprocess, queue
from multiprocessing import Process
import cv2
from flask_wtf import FlaskForm
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired
from wtforms import validators, SubmitField
from datetime import datetime
import pandas as pd
import crolling, video

app = Flask(__name__)
app.config['SECRET_KEY'] = '#$%^&*'
img_dir_path = "./uploads"
img_file_path = "./uploads/"
#app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 * 1024 #파일 업로드 용량 제한 단위:바이트
file_list = []
@app.errorhandler(404)
def page_not_found(error):
    app.logger.error(error)
    return render_template('page_not_found.html'), 404

#HTML 렌더링
@app.route('/')
def home_page():
	weather_data = crolling.nowcast("성수1가제1동").split("-")
	return render_template('home.html', now_weather=weather_data)


#업로드 HTML 렌더링
@app.route('/upload')
def upload_page():
	return render_template('upload.html')

#파일 업로드 처리
@app.route('/fileUpload', methods = ['GET', 'POST'])
def upload_file():
    playlist_path = "./playlist/"
    if request.method == 'POST':
        media_insert_queue.put(True)
        f = request.files['file']
        #저장할 경로 + 파일명
        f.save(playlist_path + secure_filename(f.filename))
        return render_template('check.html')
    else:
        return render_template('page_not_found.html')

class InfoForm(FlaskForm):
    startdate = DateField('Start Date', format='%Y-%m-%d', validators=(validators.DataRequired(),))
    enddate = DateField('End Date', format='%Y-%m-%d', validators=(validators.DataRequired(),))
    submit = SubmitField('Submit')

#다운로드 HTML 렌더링
@app.route('/downfile', methods = ['GET', 'POST'])
def down_page():
    form = InfoForm()
    if form.validate_on_submit():
        session['startdate'] = form.startdate.data
        session['enddate'] = form.enddate.data
        return redirect('fileDown')
    return render_template('filedown.html',form=form)

#파일 다운로드 처리
@app.route('/fileDown', methods = ['GET', 'POST'])
def down_file():
    zip_file_list=[]
    startdate = datetime.datetime.strptime(session['startdate'],'%Y-%m-%d')
    enddate = datetime.datetime.strptime(session['enddate'],'%Y-%m-%d')
    for f in os.listdir(img_dir_path):
        file = img_file_path + f
        if os.path.getctime(file) >= startdate and os.path.getctime(file) <= enddate:
            zip_file_list.append(file)
    if zip_file_list:
        subprocess.run("zip -r ./temp.zip {}".format(zip_file_list))
        path = "./"
        return send_file(path + "temp.zip",
                attachment_filename = "temp.zip",
                as_attachment=True)
    else:
        return render_template('page_not_found.html')

#쓰레드 종료용 시그널 함수
def handler(signum, frame):
    global exitThread
    exitThread = True

if __name__ == '__main__':
    global media_insert_queue
    media_insert_queue = queue.Queue()
    video_proc = Process(target=video.MainThread,args=(exitThread,media_insert_queue)).start()
    #서버 실행
    app.run(host='10.42.0.1', debug = True) ## 카메라 사용시 debug false해야만 가능 
