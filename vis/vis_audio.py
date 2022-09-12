import librosa
import librosa.display as dsp

import matplotlib.pyplot as plt
import numpy as np

path = 'data-audio\L3_right.wav'

def visualize_audio():

    # load audio file
    y1, sr1 = librosa.load(path, duration=60)
    y2, sr2 = librosa.load(path, duration=60)

    # display magnitude
    '''
    plt.plot(y1)
    plt.xlim([2000,3000])
    plt.show()
    '''

    fig, ax = plt.subplots(nrows=2, sharex=True,figsize=(10,7))
    librosa.display.waveshow(y1, sr=sr1, ax=ax[0])
    ax[0].set(title='Envelope view, mono')
    ax[0].label_outer()
    librosa.display.waveshow(y2, sr=sr2, ax=ax[1])
    ax[1].set(title='Envelope view, stereo')
    ax[1].label_outer()
    fig.show()