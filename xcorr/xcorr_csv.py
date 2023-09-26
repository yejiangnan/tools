import os
import threading
from .offset import get_offset
import sys
import re
import logging

song_id2offset = {}
dir_list = []
log_file = "error.log"
cnt = 0

def calculate_xcorr(start, end):
    global dir_list
    global song_id2offset
    global log_file
    global cnt
    for i in range(start, end):
        try:
            xcorr = get_offset(dir_list[i][2], dir_list[i][1])
            song_id2offset[dir_list[i][0]] = xcorr
        except Exception as e:
            logging.error(f"An error occurred for dir_list[{i}]: {str(e)}")
            logging.error(f"dir_list[{i}] values: {dir_list[i]}")
        cnt += 1
        print(cnt)

def make_csv(file_type, audio, lab):       
    global dir_list
    global song_id2offset
    global log_file
    logging.basicConfig(filename=log_file, level=logging.ERROR)

#    song_id2dir = {}
#    path = audio
#    num_list = os.listdir(path)
#    
#    for num in num_list:
#        sub_path = path + '/' + num
#        song_list = os.listdir(sub_path)
#        for song in song_list:
#            if file_type == "song":
#                song_id = song[:song.find('-')]
#            else:
#                song_id = re.findall(r'^[0-9]+-[0-9]+', song)[0]
#            song_id2dir[song_id] = {"song": (sub_path + '/' + song).replace('//', '/')}
#
#    path = lab
#    lab_list = os.listdir(path)
#    for lab in lab_list:
#        song_id = lab[:lab.find('_')]
#        if song_id2dir.get(song_id):
#            song_id2dir[song_id]["lab"] = (path + '/' + lab).replace('//', '/')
    
    song_id2dir = {}
    path = audio
    doc_list = os.listdir(path)
    for doc in doc_list:
        song_dir = (path + '/' + doc + "/vocals.wav").replace('//', '/')
        song_id2dir[doc] = {"song": song_dir}

    path = lab
    lab_list = os.listdir(path)
    for lab in lab_list:
        song_id = re.findall(r'^(.*)\.', lab)[0]
        if song_id2dir.get(song_id):
            song_id2dir[song_id]["lab"] = (path + '/' + lab).replace('//', '/')

    dir_list = [[key, val["lab"], val["song"]] for key, val in song_id2dir.items() if val.get("lab") and val.get("song")]
    
    for item in dir_list:
        print(item)

    num_threads = 20
    thread_ranges = []
    step = len(dir_list) // num_threads
    for i in range(num_threads):
        start = i * step
        end = (i + 1) * step if i < num_threads - 1 else len(dir_list)
        thread_ranges.append((start, end))
        print(start, end)
    
    threads = []
    for start, end in thread_ranges:
        print(start, end)
        thread = threading.Thread(target=calculate_xcorr, args=(start, end))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    with open("output.csv", 'w') as file:
        for key, val in song_id2offset.items():
            line = str(key) + ',' + str(val) + '\n'   
            file.write(line)
    
