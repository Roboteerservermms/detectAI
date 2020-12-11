# -*- coding: utf-8 -*-
"""
Created on Wed May  6 14:05:46 2020
Content: patially reuse code from ml-sound-classifier-master\..\realtime_predictor.py
@author: magicalme
"""
import scipy
import numpy as np
import librosa
import pyaudio
import pandas as pd
import shutil
from os import listdir
from os.path import isfile, join
# import struct
import queue
import array

from collections import deque

#import tensorflow as tf
from tensorflow.keras import losses, models, optimizers
from tensorflow.keras.activations import softmax
from tensorflow.keras.layers import (Convolution2D, BatchNormalization, Flatten, MaxPool2D, Activation, Input, Dense)

import time
import datetime
from time import strftime

class Config(object):
    def __init__(self,
                 sampling_rate=16000, audio_duration=2, n_classes=41,
                 use_mfcc=False, n_folds=10, learning_rate=0.0001, 
                 max_epochs=50, n_mfcc=20):
        self.sampling_rate = sampling_rate
        self.audio_duration = audio_duration
        self.n_classes = n_classes
        self.use_mfcc = use_mfcc
        self.n_mfcc = n_mfcc
        self.n_folds = n_folds
        self.learning_rate = learning_rate
        self.max_epochs = max_epochs

        self.audio_length = self.sampling_rate * self.audio_duration
        if self.use_mfcc:
            self.dim = (self.n_mfcc, 1 + int(np.floor(self.audio_length/512)), 1)
        else:
            self.dim = (self.audio_length, 1)
                    
def prepare_data_fileinput(file_path, config):
    X = np.empty(shape=(1, config.dim[0], config.dim[1], 1))
    input_length = config.audio_length
    
    #print(file_path)
    data, _ = librosa.core.load(file_path, sr=config.sampling_rate, res_type="kaiser_fast")
    
    # Remove silence or noise or things like that

    # Random offset / Padding
    if len(data) > input_length:
        max_offset = len(data) - input_length
        offset = np.random.randint(max_offset)
        data = data[offset:(input_length+offset)]
    else:
        if input_length > len(data):
            max_offset = input_length - len(data)
            offset = np.random.randint(max_offset)
        else:
            offset = 0
        data = np.pad(data, (offset, input_length - len(data) - offset), "constant")

    #data = librosa.feature.mfcc(data, sr=config.sampling_rate, n_mfcc=config.n_mfcc)
    S = librosa.feature.melspectrogram(data, sr=config.sampling_rate, n_fft=2048, hop_length=512, n_mels=config.n_mfcc)
    S_DB = librosa.power_to_db(S, ref=np.max)
    
    data = np.expand_dims(S_DB, axis=-1)
    X[0,] = data
        
    return X

def prepare_data_streaminput(data, config):
    X = np.empty(shape=(1, config.dim[0], config.dim[1], 1))
    input_length = config.audio_length
    
    # Remove silence or noise or things like that

    # Random offset / Padding
    if len(data) > input_length:
        max_offset = len(data) - input_length
        offset = np.random.randint(max_offset)
        data = data[offset:(input_length+offset)]
    else:
        if input_length > len(data):
            max_offset = input_length - len(data)
            offset = np.random.randint(max_offset)
        else:
            offset = 0
        data = np.pad(data, (offset, input_length - len(data) - offset), "constant")

    #data = librosa.feature.mfcc(data, sr=config.sampling_rate, n_mfcc=config.n_mfcc)
    S = librosa.feature.melspectrogram(data, sr=config.sampling_rate, n_fft=2048, hop_length=512, n_mels=config.n_mfcc)
    S_DB = librosa.power_to_db(S, ref=np.max)
    
    data = np.expand_dims(S_DB, axis=-1)
    X[0,] = data
        
    return X

def get_2d_conv_model(config):
    
    nclass = config.n_classes
    
    inp = Input(shape=(config.dim[0],config.dim[1],1))
    x = Convolution2D(32, (4,10), padding="same")(inp)
    x = BatchNormalization()(x)
    x = Activation("relu")(x)
    x = MaxPool2D()(x)
    
    x = Convolution2D(32, (4,10), padding="same")(x)
    x = BatchNormalization()(x)
    x = Activation("relu")(x)
    x = MaxPool2D()(x)
    
    x = Convolution2D(32, (4,10), padding="same")(x)
    x = BatchNormalization()(x)
    x = Activation("relu")(x)
    x = MaxPool2D()(x)
    
    x = Convolution2D(32, (4,10), padding="same")(x)
    x = BatchNormalization()(x)
    x = Activation("relu")(x)
    x = MaxPool2D()(x)

    x = Flatten()(x)
    x = Dense(64)(x)
    x = BatchNormalization()(x)
    x = Activation("relu")(x)
    out = Dense(nclass, activation=softmax)(x)

    model = models.Model(inputs=inp, outputs=out)
    opt = optimizers.Adam(config.learning_rate)

    model.compile(optimizer=opt, loss=losses.categorical_crossentropy, metrics=['acc'])
    
    return model 

'''
    test_files_one_by_one("Data/test/Car_crash", "Car_crash")
'''
def test_files_one_by_one(file_path, class_name):
    model = get_2d_conv_model(config)
    file_names = [f for f in listdir(file_path) if isfile(join(file_path, f))]
    n = 0
    t1 = time.time()
    for name in file_names:
        X_test = prepare_data_fileinput(file_path + "\\" + name, config)
        test_prediction = model.predict(X_test, batch_size=2, verbose=0)
        top1_max = np.array(LABELS)[np.argsort(-test_prediction, axis=1)[:, :1]]
        print("File_{} predicted {}".format(name, top1_max[0][0]))
        if(top1_max[0][0] in class_name):
            n = n + 1
    
    print("Success/Total: {}/{}".format(n, len(file_names)))
    print("Accuracy %.2f %%" %(100 * n/len(file_names)))
    print("Done testing files!")
    
    t2 = time.time()
    print('Run time:', t2 - t1, '(s)')
    
def callback(in_data, frame_count, time_info, status):
    wave = array.array('h', in_data)
    raw_frames.put(wave, True)
    return (None, pyaudio.paContinue)

def on_predicted():
    global k
    global current_index
    
    if (len(pred_queue) == PRED_TIMES):
        label_indexes = []
        predictions = []
        
        for i in range(PRED_TIMES):
            predictions.append(pred_queue.popleft())    
    
        for pred in predictions:
            #label_index
            label_indexes.append(np.argsort(-pred, axis=1)[:, :1][0][0])
            if (DEBUG):
                raw_audio_data = audio_data_queue.popleft()
                k = k + 1
                partial_file_name = np.array(LABELS)[np.argsort(-pred, axis=1)[:, :1]][0][0]
                # partial_file_name = "Car_crash"
                fpath = WAVE_OUTPUT_FILENAME + "_" + partial_file_name + "_" + str(k) + ".wav"
                scipy.io.wavfile.write(fpath, RATE, np.array(raw_audio_data).astype('int16'))
        
        current_datetime = datetime.datetime.now()

        if (current_index > -1):
            print("{}    {}".format(current_datetime.strftime("%Y-%m-%d %H:%M:%S"), LABELS[current_index]))
        
        if (DEBUG):
            print("Current index: " + str(current_index))
        
        if (current_index != label_indexes[0]):
            result = np.array(LABELS)[np.argsort(-predictions[0], axis=1)[:, :1]][0][0]
            
            print("-"*100)
            print("{}    {}    ({} %)".format(current_datetime.strftime("%Y-%m-%d %H:%M:%S"), result, round(100 * np.max(predictions[0])/np.sum(predictions[0]),2)))
            
            # result = LABELS[0]
            # if(label_indexes[0] == 1 or label_indexes[0] == 2):
            #     result = "Car"
            # elif(label_indexes[0] == 3 or label_indexes[0] == 4):  
            #     result = "Human"
            # elif(label_indexes[0] == 5):
            #     result = "Danger"
            # print("{}    {}    ({} %)".format(current_datetime.strftime("%Y-%m-%d %H:%M:%S"), result, round(100 * np.max(predictions[0])/np.sum(predictions[0]),2)))
    
            current_index = label_indexes[0]
            if (DEBUG):
                print("Updated index: " + str(current_index))
        
        number_of_results = len(label_indexes)
        for i in range(number_of_results):
            if (i + 1 < number_of_results and label_indexes[i + 1] != label_indexes[i]):
                top1_max = np.array(LABELS)[np.argsort(-predictions[i + 1], axis=1)[:, :1]]
                
                print("-"*100)
                print("{}    {}    ({} %)".format(current_datetime.strftime("%Y-%m-%d %H:%M:%S"), top1_max[0][0], round(100 * np.max(predictions[i + 1])/np.sum(predictions[i + 1]),2)))
    
                # if(label_indexes[i + 1] == 1 or label_indexes[i + 1] == 2):
                #     result = "Car"
                # elif(label_indexes[i + 1] == 3 or label_indexes[i + 1] == 4):  
                #     result = "Human"
                # elif(label_indexes[i + 1] == 5):
                #     result = "Danger"
                # print("{}    {}    ({} %)".format(current_datetime.strftime("%Y-%m-%d %H:%M:%S"), result, round(100 * np.max(predictions[0])/np.sum(predictions[0]),2)))   
        
                current_index = label_indexes[i + 1]
                if (DEBUG):
                    print("Updated index: " + str(current_index))
    
def main_process(models, on_predicted):
    # Pool audio data
    global raw_audio_buffer
    while not raw_frames.empty():
        raw_audio_buffer.extend(raw_frames.get())
        if len(raw_audio_buffer) >= MAX_NUMBER_SAMPLES: break
    if len(raw_audio_buffer) < MAX_NUMBER_SAMPLES: return
    
    # print("raw buffer: " + str(len(raw_audio_buffer)))
    audio_to_convert = np.array(raw_audio_buffer[:MAX_NUMBER_SAMPLES]) / 32767
    # print("audio_to_convert: " + str(len(audio_to_convert)))
    # print(audio_to_convert)
    
    if (DEBUG):
        audio_data_queue.append(raw_audio_buffer[:MAX_NUMBER_SAMPLES])
    
    raw_audio_buffer = raw_audio_buffer[STEP_NUMBER_SAMPLES:]
    # print("raw buffer after convert: " + str(len(raw_audio_buffer)))
    
    X_test = prepare_data_streaminput(audio_to_convert, config)
    #test_prediction = models[0].predict(X_test, batch_size=1, verbose=0)
    test_predictions = [model.predict(X_test, batch_size=1, verbose=0) for model in models]
    
    ensemble_prediction = np.ones_like(test_predictions[0])
    for test_prediction in test_predictions:
        ensemble_prediction = ensemble_prediction * test_prediction

    ensemble_prediction = ensemble_prediction**(1./len(test_predictions))
 
    pred_queue.append(ensemble_prediction)
    on_predicted()    
    
def run_predictor():
    models = []
    # range(1) means ensamble learning is not used to get faster inference
    # model_0.h5 is the best one chosen among models
    # range(5) means we have 5 models and want to apply ensamble learning into these 5 models
    for i in range(2):
        model = get_2d_conv_model(config)
        #model.load_weights(MODEL_FOLDER + '/model_0.h5')  
        model.load_weights(MODEL_FOLDER + '/model_%d.h5'%i)
        models.append(model)
        
    # realtime recording
    audio = pyaudio.PyAudio()
    stream = audio.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                #input_device_index=0,
                frames_per_buffer=SAMPLES_PER_CHUNK,
                start=False,
                stream_callback=callback
            )
    
    # print(audio.get_sample_size(FORMAT))
    # sample_width = audio.get_sample_size(FORMAT)
    
    # main loop
    stream.start_stream()
    while stream.is_active():
        main_process(models, on_predicted)
        time.sleep(0.001)
    stream.stop_stream()
    stream.close()
    # finish
    audio.terminate()
    models.clear()
    exit(0)
    

if __name__ == "__main__":
    DEBUG = False

    SAMPLES_PER_CHUNK = 4096
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    RECORD_SECONDS = 2
    
    WAVE_OUTPUT_FILENAME = "recordings/" + strftime("%Y%m%d_%H%M%S") + "_output_"
    MODEL_FOLDER = "models"
    MAX_NUMBER_SAMPLES = RATE * RECORD_SECONDS
    
    # STEP_NUMBER_SAMPLES = 4410
    # PRED_TIMES = 20
    
    # STEP_NUMBER_SAMPLES = 5880
    # PRED_TIMES = 15
    
    # STEP_NUMBER_SAMPLES = 8820
    # PRED_TIMES = 10
    
    # STEP_NUMBER_SAMPLES = 11025
    # PRED_TIMES = 8
    
    STEP_NUMBER_SAMPLES = 17640
    PRED_TIMES = 5
    
    # STEP_NUMBER_SAMPLES = 22050
    # PRED_TIMES = 4
    
    # STEP_NUMBER_SAMPLES = 44100
    # PRED_TIMES = 2
    
    # STEP_NUMBER_SAMPLES = 88200
    # PRED_TIMES = 1
    
    '''
        ['Back_ground','Car_crash','Car_passing_by','Clapping','Crowd_clapping','Screaming']
        
        output new class names based on their index depending on the requirement   
            0 (Back_ground)
            1 (Car_crash)      ---> Danger
            2 (Car)            ---> Car
            3 (Clapping)       ---> Human
            4 (Crowd_clapping) ---> Human
            5 (Screaming)      ---> Danger
    '''
    train = pd.read_csv("csv/label_original.csv")
    LABELS = list(train.label.unique())
    
    '''
        these variables below are shared between recording thread and main thread (main process)
    '''
    raw_frames = queue.Queue(maxsize=100)
    raw_audio_buffer = []
    pred_queue = deque(maxlen=PRED_TIMES) # save PRED_TIMES of results for every two seconds
    audio_data_queue = deque(maxlen=PRED_TIMES) # write recording files in DEBUG mode
    
    config = Config(sampling_rate=44100, audio_duration=2, learning_rate=0.001, use_mfcc=True, n_mfcc=40, n_classes=len(LABELS))  
    k = 0
    current_index = -1
    run_predictor()
    