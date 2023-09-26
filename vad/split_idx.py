import os
from .vad import vad
import sys
import threading
import re
import subprocess
import logging

dir_list = []
cnt = 0
log_file = "error.log"

def get_vad(start, end):
    global dir_list
    global cnt
    for i in range(start, end):
        try:
            vad(dir_list[i][0], dir_list[i][1], dir_list[i][2])
            cnt += 1
            print(cnt)
        except Exception as e:
            logging.error(f"An error occurred for dir_list[{i}]: {str(e)}")
            logging.error(f"dir_list[{i}], values: {dir_list[i]}")

def doc_vad(audio, lab):
    global dir_list
    global log_file
    logging.basicConfig(filename=log_file, level=logging.ERROR)
    if os.path.exists("./vad_json"):
        subprocess.run(["rm", "-r", "./vad_json"])
        subprocess.run(["mkdir", "./vad_json"])
    else:
        subprocess.run(["mkdir", "./vad_json"])
    song_id2info = {}
#    song_dir = audio
#    song_list = os.listdir(song_dir)
#    for num in song_list:
#        new_dir = song_dir + num
#        songs = os.listdir(new_dir)
#        for song in songs:
#            exact_dir = new_dir + '/' + song
#            song_id = song[:-14]
#            song_id2info[song_id] = {"song_dir": exact_dir.replace('//', '/'), "output": ("./vad_json" + '/' + song_id + "_vad.json").replace('//', '/')}
#    
#    lab_dir = lab
#    lab_list = os.listdir(lab_dir)
#    for lab in lab_list:
#        song_id = lab[:-10]
#        if song_id2info.get(song_id):
#            song_id2info[song_id]["lab_dir"] = (lab_dir + '/' + lab).replace('//', '/')
#    
#    dir_list = []
#    for key, val in song_id2info.items():
#        if val.get("song_dir") and val.get("lab_dir"):
#            dir_list.append([val["song_dir"], val["lab_dir"], val["output"]])
    
    song_dir = audio
    song_list = os.listdir(song_dir)
    for doc in song_list:
        new_dir = (song_dir + '/' + doc + '/' + "vocals.wav").replace('//', '/')
        song_id = doc
        song_id2info[song_id] = {"song_dir": new_dir, "output": ("./vad_json" + '/' + song_id + "_vad.json").replace('//', '/')}
    lab_dir = lab
    lab_list = os.listdir(lab_dir)
    for lab in lab_list:
        song_id = re.findall(r'^(.*)\_', lab)[0]
        song_id2info[song_id]["lab_dir"] = (lab_dir + '/' + lab).replace('//', '/')

    for key, val in song_id2info.items():
        if val.get("song_dir") and val.get("lab_dir"):
            dir_list.append([val["song_dir"], val["lab_dir"], val["output"]])
    
    num_threads = 50
    thread_ranges = []
    step = len(dir_list) // num_threads
    for i in range(num_threads):
        start = i * step
        end = (i + 1) * step if i < num_threads - 1 else len(dir_list)
        thread_ranges.append((start, end))
        print(start, end)

    threads = []
    for start, end in thread_ranges:
        thread = threading.Thread(target=get_vad, args=(start, end))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
