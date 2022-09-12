import sys
import os
import numpy as np
import pyqtgraph as pg
import librosa

from pyqtgraph.Qt import QtGui, QtCore
from utils.loading import load_config_from_yaml
from modules.MicrophoneRecorder import MicrophoneRecorder

# load configuration
assert os.path.exists(sys.argv[1])
config = load_config_from_yaml(sys.argv[1])
config.Application['n_freqs'] = config.MicrophoneRecorder.chunk_size // 2 + 1

# PyAudio
recorder = MicrophoneRecorder(**config.MicrophoneRecorder)
recorder.start()

# shapes
shape = (recorder.channels, recorder.chunksize)
n_ch, n_chunk = shape
window = np.hamming(n_chunk)

# application
app = QtGui.QApplication([]) 
win = pg.GraphicsLayoutWidget()
win.setWindowTitle('VAT Audio')
win.resize(*config.Application.size)
win.show()

# signals
sig = np.zeros(shape, dtype=recorder.dtype)
x = np.zeros(n_chunk)
pw = np.zeros(n_chunk)
specs = np.zeros(config.Application.n_freqs)
iter = 0
idx = 0
pos = 0

# update signal and data
def update():
    global sig, x, pw, specs, iter, idx, pos
    frames = recorder.get_frames()
    if len(frames) == 0:
        sig[:] = np.zeros(shape, dtype=recorder.dtype)
        x = np.zeros(n_chunk)
    else:
        sig[:] = frames[-1]
        x = 0.5 * (sig[0] + sig[1])
    x_window = x * window
    specs[:] = np.abs(np.fft.rfft(x_window)) ** 2
    pw = np.sqrt(np.mean(x ** 2))
    idx = iter % config.Application.n_frames
    pos = idx + 1 if idx < config.Application.n_frames else 0
    iter += 1

timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(1./config.Application.fps * 1000)

# Chroma
chroma_plot = win.addPlot(title='Chroma')
chroma_plot.showGrid(x=True, y=True)
chroma_plot.enableAutoRange('xy', False)
chroma_plot.setXRange(0, config.Application.n_frames)
chroma_plot.setYRange(0, config.Chroma.n_chroma)
chroma_plot.setLabel('left', 'Pitch Class')

plots = []
for k in range(config.Chroma.n_chroma):
    plots.append(chroma_plot.plot(pen=pg.mkPen((k, config.Chroma.n_chroma), width=3)))

chroma = np.zeros(config.Chroma.n_chroma)
chroma_pre = np.zeros(config.Chroma.n_chroma)
chromafb = librosa.filters.chroma(sr=recorder.rate, n_fft=n_chunk, n_chroma=config.Chroma.n_chroma)
chromafb **= 2
chroma_frames = np.zeros((config.Application.n_frames, config.Chroma.n_chroma))

def update_chroma():
    global chroma
    chroma[:] = np.dot(chromafb, specs)
    chroma[:] = chroma / (np.max(chroma) + 1e-16)
    chroma[:] = 0.3 * chroma + 0.7 * chroma_pre
    chroma_frames[idx] = chroma[:]
    for k in range(config.Chroma.n_chroma):
        alpha = chroma_frames[idx, k] * 0.9
        alpha = alpha if pw > 1e-3 else 0.0
        plots[k].setAlpha(alpha, False)
        chroma_frames[idx, k] += k
        plots[k].setData(np.r_[chroma_frames[pos:config.Application.n_frames,k],chroma_frames[0:pos,k]])
    chroma_pre[:] = chroma

chroma_timer = QtCore.QTimer()
chroma_timer.timeout.connect(update_chroma)
chroma_timer.start(1./config.Application.fps * 1000)

# spectrogram
pwd = win.addPlot(title='Power Spectrogram')
pwd_image = pg.ImageItem()
cmap = pg.colormap.getFromMatplotlib('jet')
bar = pg.ColorBarItem(colorMap=cmap)
bar.setImageItem(pwd_image)
pwd.addItem(pwd_image)

waterfall_frames = np.zeros((config.Application.n_frames, config.Application.n_freqs))
def update_spec():
    global pwd_image, waterfall_frames
    waterfall_frames[idx, :] = specs
    pwd_image.setImage(np.r_[waterfall_frames[pos:config.Application.n_frames], waterfall_frames[0:pos]], ref=np.median)

timer_fft = QtCore.QTimer()
timer_fft.timeout.connect(update_spec)
timer_fft.start(1./config.Application.fps * 1000)

# start next row
win.nextRow()

# waterfall plot
waterfall_plot = win.addPlot(title='Power Spectrogram in Decibel')
waterfall_plot.setLabel('left', 'Decibel', units='dB')
waterfall_image = pg.ImageItem()
cmap = pg.colormap.getFromMatplotlib('jet')
bar = pg.ColorBarItem(colorMap=cmap)
bar.setImageItem(waterfall_image)
waterfall_plot.addItem(waterfall_image)

def update_waterfall():
    global waterfall_image
    waterfall_image.setImage(librosa.power_to_db(
        np.r_[waterfall_frames[pos:config.Application.n_frames], waterfall_frames[0:pos]], ref=np.median))

timer_waterfall = QtCore.QTimer()
timer_waterfall.timeout.connect(update_waterfall)
timer_waterfall.start(1./config.Application.fps * 1000)

# mel spectrogram
mel_plot = win.addPlot(title='Mel Spectrogram')
mel_plot.setMouseEnabled(x=False, y=False)
mel_plot.setLabel('left', 'Mel Frequency Bins')
#mel_plot.setXRange(0, config.Application.n_frames)
#mel_plot.setYRange(0, config.MelSpectrogram.n_mels)
mel_image = pg.ImageItem()
cmap = pg.colormap.getFromMatplotlib('jet')
bar = pg.ColorBarItem(colorMap = cmap)
bar.setImageItem(mel_image)
mel_plot.addItem(mel_image)

melfb = librosa.filters.mel(sr=recorder.rate, n_fft=n_chunk,n_mels= config.MelSpectrogram.n_mels)
melfeqs = librosa.mel_frequencies(n_mels=config.MelSpectrogram.n_mels)
melspecs = np.zeros((config.Application.n_frames, config.MelSpectrogram.n_mels))

def update_mel():s
    global mel_image, melspecs
    melspecs[idx, :] = np.dot(melfb, specs)
    mel_image.setImage(librosa.power_to_db(
        np.r_[melspecs[pos:config.Application.n_frames],melspecs[0:pos]], ref=np.max))

timer_mel = QtCore.QTimer()
timer_mel.timeout.connect(update_mel)
timer_mel.start(1./config.Application.fps * 1000)

if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec()