import librosa
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import json

def vad(audio, lab, output):
    sample_rate = 16000
    song_time_length = 10
    song_frame_length = 160
    song_frame_shift = 160
    word_frame_length = 10
    word_frame_shift = 10
    search_range_half = 300
    step = 1 / 15
    minus = 30
    minus_long = 30
    len_to_change = 100

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
    sil2seg = {}
    with open(lab, 'r') as file:
        sample_time = 0
        for line in file:
            parts = line.split(' ', 2)
            parts = [int(parts[i]) // 10000 if i < 2 else parts[i][:-1] for i in range(3)]
            lines.append(parts)
            while sample_time <= parts[1]:
                if parts[2] == "<SIL>":
                    word_energy.append(0)
                    sil2seg[len(word_energy) - 1] = (parts[0] * 10000, parts[1] * 10000)
                else:
                    word_energy.append(1)
                sample_time += word_frame_length

    sil2point = {}
    for i in range(len(lines) - 1):
        pre = lines[i]
        ne = lines[i + 1]
        if pre[2] != "<SIL>" and ne[2] != "<SIL>":
            if int(pre[1] / 10) - 15 < 0:
                continue
            s = 1
            for i in range(max(0, int(pre[1] / 10) - 15), min(int(pre[1] / 10), len(word_energy) - 1)):
                word_energy[i] = s
                s -= step
                sil2point[i] = pre[1] * 10000
            s = 0
            for i in range(max(0, int(ne[0] / 10)), min(int(ne[0] / 10) + 15, len(word_energy) - 1)):
                word_energy[i] = s
                s += step
                sil2point[i] = pre[1] * 10000

    if len(song_energy) > len(word_energy):
        song_energy = song_energy[:len(word_energy)]
    else:
        word_energy = word_energy[:len(song_energy)]

    song_energy = [1 if item == 0 else item for item in song_energy]
    song_energy = np.log10(song_energy)
    song_energy = [item * 10 for item in song_energy]

    split_idx = []
    json_file = []
    mi = abs(min(song_energy))
    song_energy = [item + mi for item in song_energy]
    max_energy = max(song_energy)

    i = 0
    while i < len(word_energy):
        if word_energy[i] != 1:
            point_info = {}
            if word_energy[i] == 0:
                point_info["type"] = "Seg_sil"
                point_info["seg_info"] = sil2seg[i]
            else:
                point_info["type"] = "V_sil"
                point_info["seg_info"] = sil2point[i]
            
            j = i
            while j < len(word_energy) and  word_energy[j] != 1:
                j += 1
            
            idx, min_energy, found = i, max_energy, False
            for k in range(i, j):
                if song_energy[k] <= max_energy - minus and song_energy[k] <= min_energy:
                    found = True
                    idx = k
                    min_energy = song_energy[idx]
            if j - idx >= len_to_change:
                u = idx
                for k in range(idx, j - idx):
                    if song_energy[k] <= max_energy - minus_long:
                        u = k
                idx = u
            if found:
                point_info["energy_diff"] = max_energy - song_energy[idx]
                point_info["time_of_point"] = idx * 10
                json_file.append(point_info)
                split_idx.append(idx)
            i = j
        else:
            i += 1
    
    with open(output, 'w') as file:
        json.dump(json_file, file)
        
