import pyaudio

audio = pyaudio.PyAudio()
for i in range(audio.get_device_count()):
    dev = audio.get_device_info_by_index(i)
    print((i,dev['name'],dev['maxInputChannels']))
#print([audio.get_device_info_by_index(i)] for i in range(audio.get_device_count()))