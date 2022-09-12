
import pyaudio
import wave
import time

class Microphone:

    def __init__(self, identifier='L1_right',chunk=4096, format=pyaudio.paInt16, channels=3, rate=44100, py=pyaudio.PyAudio()):

        # Start Tkinter and set Title
        self.collections = []
        self.identifier=identifier
        self.CHUNK = chunk
        self.FORMAT = format
        self.CHANNELS = channels
        self.RATE = rate
        self.p = py
        self.frames = []
        self.st = 1
        #self.stream = self.p.open(format=self.FORMAT, channels=self.CHANNELS, input_device_index=12,rate=self.RATE, input=True, frames_per_buffer=self.CHUNK)
        info = py.get_host_api_info_by_index(0)
        print(py.get_device_info_by_index(6))
        numdevices = info.get('deviceCount')
        for i in range(0, numdevices):
            if (py.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                print("Input Device id ", i, " - ", py.get_device_info_by_host_api_device_index(0, i).get('name'))




    def start_record(self):
        self.st = 1
        self.frames = []
        # input_device_index=self.input_device_index,
        stream = self.p.open(format=self.FORMAT,channels=self.CHANNELS, rate=self.RATE, input_device_index=0,input=True, frames_per_buffer=self.CHUNK)
        while self.st == 1:
            data = stream.read(self.CHUNK)
            self.frames.append(data)

        stream.close()
        filename='data-audio/'+self.identifier+'_'+str(time.time()).split('.')[0]+'.wav'
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(self.frames))
        wf.close()

    def stop(self):
        self.st = 0


