from numpy.core.fromnumeric import reshape
import pyaudio
import numpy as np
import threading
import atexit


class MicrophoneRecorder:
    def __init__(self,
                 format=pyaudio.paFloat32,
                 input_device_keyword="default",
                 chunk_size=1024,
                 maxInputChannels=1
                 ):
        self.maxInputChannels = maxInputChannels
        self.chunksize = chunk_size
        self.format = format
        self.lock = threading.Lock()
        self.stop = False
        self.frames = []
        atexit.register(self.close)
        if format is pyaudio.paFloat32:
            self.dtype = np.float32
        elif format is pyaudio.paInt16:
            self.dtype = np.int16
        # Open the stream
        self.p = pyaudio.PyAudio()
        self.__open_stream(input_device_keyword)

    def get_params(self):
        params_dict = {
            "RATE": self.rate,
            "CHUNK": self.chunksize,
            "CHANNELS": self.channels,
        }
        return params_dict

    def __open_stream(self, input_device_keyword):
        self.input_device_index = None
        self.input_device_name = None
        self.devices = []
        print(f"=========================================================")
        print(f"idx\tinCH\toutCh\tname")

        for k in range(self.p.get_device_count()):
            dev = self.p.get_device_info_by_index(k)
            self.devices.append(dev)
            device_name = dev["name"]
            device_index = dev["index"]
            maxInputChannels = int(dev["maxInputChannels"])
            maxOutputChannels = int(dev["maxOutputChannels"])

            if type(device_name) is bytes:
                device_name = device_name.decode("cp932")  # for windows

            print(f"{device_index}\t{maxInputChannels}\t{maxOutputChannels}\t{device_name}")

            if input_device_keyword in device_name \
                    and maxInputChannels == self.maxInputChannels:
                self.input_device_index = dev["index"]
                self.input_device_name = device_name
                self.rate = int(dev["defaultSampleRate"])
                self.channels = dev["maxInputChannels"]

        if self.input_device_index is not None:
            print(f"=========================================================")
            print(f"Input device:  {self.input_device_name} is OK.")
            print(f"\tIDX:       {self.input_device_index}")
            print(f"\tRATE:      {self.rate}")
            print(f"\tCHANNELS:  {self.channels}")
            print(f"\tCHUNK:     {self.chunksize}")
            print(f"=========================================================")
        else:
            print(f"\nWarning: Input device is not exist\n")

        self.stream = self.p.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            output=False,
            frames_per_buffer=self.chunksize,
            input_device_index=self.input_device_index,
            stream_callback=self.new_frame)

        return self

    def start(self):
        print('Started the microphone recorder')
        self.stream.start_stream()

    def new_frame(self, data, frame_count, time_info, status):
        data = np.frombuffer(data, dtype=self.dtype)
        sig = np.reshape(data, (self.chunksize, self.channels)).T
        with self.lock:
            self.frames.append(sig)
            if self.stop:
                return None, pyaudio.paComplete
        return None, pyaudio.paContinue

    def get_frames(self):
        with self.lock:
            frames = self.frames
            self.frames = []
            return frames

    def close(self):
        with self.lock:
            self.stop = True
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()


if __name__ == '__main__':
    import time
    import matplotlib.pyplot as plt

    recorder = MicrophoneRecorder()
    recorder.start()

    print('recording')
    time.sleep(1)
    frames = recorder.get_frames()
    recorder.close()
    data = frames[-1][0]
    # figure
    fig, (ax1, ax2) = plt.subplots(1, 2)
    # amplitude
    ax1.plot(data)
    # fft
    X = np.abs(np.fft.rfft(np.hanning(data.size) * data, n=1024))
    magnitude = 20 * np.log10(X + 1e-8)
    ax2.plot(magnitude)
    plt.show()