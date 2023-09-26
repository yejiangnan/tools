import librosa
import numpy as np
import librosa.display
import matplotlib.pyplot as plt
import sys
import time
import os

def get_offset(audio, lab):
    sample_rate = 16000
    song_time_length = 10
    song_frame_length = 160
    song_frame_shift = 160
    word_frame_length = 10
    word_frame_shift = 10
    #search_range_half = 300
    search_range_half = 100
    step = 1 / 15

    args = sys.argv
    y, sr = librosa.load(audio, sr=sample_rate, mono=True)
    y = y[:len(y) // song_time_length * song_time_length]

    pad = np.zeros(song_frame_length // 2, dtype=np.float32)
    y = np.concatenate((pad, y))
    pad_len = len(y) // song_frame_length * song_frame_length
    if pad_len < len(y):
        pad_len = pad_len + song_frame_length - len(y)
    else:
        pad_len = pad_len - len(y)
    y = np.concatenate((y, np.ones(pad_len) * 1e-5))

    song_energy = []
    song_energy = np.sum((y.reshape(-1, song_frame_length) ** 2), axis=1)

    word_energy = []
    lines = []
    with open(lab, 'r') as file:
        sample_time = 0
        for line in file:
            parts = line.split(' ', 2)
            parts = [int(parts[i]) // 10000 if i < 2 else parts[i][:-1] for i in range(3)]
            lines.append(parts)
            while sample_time <= parts[1]:
                if parts[2] == "<SIL>":
                    word_energy.append(0)
                else:
                    word_energy.append(1)
                sample_time += word_frame_length

    for i in range(len(lines) - 1):
        pre = lines[i]
        ne = lines[i + 1]
        if pre[2] != "<SIL>" and ne[2] != "<SIL>":
            s = 1
            for i in range(max(0, int(pre[1] / 10) - 15), min(int(pre[1] / 10), len(word_energy) - 1)):
                word_energy[i] = s
                s -= step
            s = 0
            for i in range(max(0, int(ne[0] / 10)), min(int(ne[0] / 10) + 15, len(word_energy) - 1)):
                word_energy[i] = s
                s += step

    if len(song_energy) > len(word_energy):
        song_energy = song_energy[:len(word_energy)]
    else:
        word_energy = word_energy[:len(song_energy)]

    song_energy = [1 if item == 0 else item for item in song_energy]
    song_energy = np.log10(song_energy)
    song_mean = np.mean(song_energy)
    song_std = np.std(song_energy)
    if song_std:
        song_energy = [(x - song_mean) / song_std for x in song_energy]
    word_mean = np.mean(word_energy)
    word_std = np.std(word_energy)
    if word_std:
        word_energy = [(x - word_mean) / word_std for x in word_energy]

    xcorr = np.correlate(word_energy, song_energy, mode="full")
    lag_range = np.arange(-search_range_half, search_range_half)
    lagged_correlation = xcorr[len(word_energy) - 1 + lag_range]
    mx = np.argmax(lagged_correlation)

    offset = (mx - search_range_half) * song_time_length
    return -int(offset)

