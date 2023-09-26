import os
import sys
import csv
import subprocess
import re

def gen_lab(file_type, lab):
    new_folder = "./lab_xcorr"
#    path = lab
#    lab_list = os.listdir(path)
#    song_id2info = {}
#    for item in lab_list:
#        if file_type == "song":
#            song_id = re.findall(r'^[0-9]+', item)[0]
#        else:
#            song_id = re.findall(r'^[0-9]+-[0-9]+', item)[0]
#        song_id2info[song_id] = {"src_dir": (path + '/' + item).replace('//', '/'), 'tgt_dir': (new_folder + '/' + song_id + "_xcorr.lab").replace('//', '/')}
    path = lab
    lab_list = os.listdir(path)
    song_id2info = {}
    for lab in lab_list:
        song_id = re.findall(r'(.*)\.', lab)[0]
        song_id2info[song_id] = {"src_dir": (path + '/' + lab).replace('//', '/'), "tgt_dir": (new_folder + '/' + song_id + "_xcorr.lab").replace('//', '/')}

    with open("output.csv", 'r') as file:
        for line in file:
            line_list = line.split(',')
            line_list[-1] = line_list[-1][:-1]
            if song_id2info.get(line_list[0]):
                song_id2info[line_list[0]]["offset"] = int(line_list[1])
    
    if os.path.exists(new_folder):
        subprocess.run(["rm", "-r", new_folder], check=True)
        subprocess.run(["mkdir", new_folder], check=True)
    else:
        subprocess.run(["mkdir", new_folder], check=True)

    for key, val in song_id2info.items():
        if val.get("src_dir") and val.get("tgt_dir"):
            if len(val) < 3:
                continue
            src = val["src_dir"]
            tgt = val["tgt_dir"]
            offset = val["offset"]
            output = []
            with open(src, 'r') as file:
                for line in file:
                    line_list = line.split(' ', 2)
                    line_list = [int(line_list[i]) // 10000 if i < 2 else line_list[i] for i in range(3)]
                    output.append(line_list)
                if offset > 0:
                    for i in range(len(output)):
                        if i != 0:
                            output[i][0] += offset
                        output[i][1] += offset
                else:
                    for i in range(len(output)):
                        output[i][0] += offset
                        output[i][1] += offset
            if offset >= 0:
                with open(tgt, 'w') as file:
                    for i in range(len(output)):
                        item = output[i]
                        file.write(str(item[0] * 10000) + ' ' + str(item[1] * 10000) + ' ' + item[2])
            else:
                with open(tgt, 'w') as file:
                    has_start = 0
                    for i in range(len(output)):
                        item = output[i]
                        if item[0] <= 0 and item[1] <= 0:
                            continue
                        elif item[0] <= 0 and item[1] > 0:
                            has_start = 1
                            file.write(str(0) + ' ' + str(item[1] * 10000) + ' ' + item[2])
                        else:
                            if has_start:
                                file.write(str(item[0] * 10000) + ' ' + str(item[1] * 10000) + ' ' + item[2])
                            else:
                                has_start = 1
                                file.write(str(0) + ' ' + str(item[1] * 10000) + ' ' + item[2])



                
