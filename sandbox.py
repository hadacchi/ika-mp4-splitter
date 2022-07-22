import json
#from tkinter import W
#import matplotlib.pyplot as plt
#from PIL import Image
import csv
import cv2
#import time
import os
import subprocess
import toml
import tqdm
import numpy as np

import mk_avidemuxpy

def dos_path(path):
    buf = path.replace('/mnt/','').replace('/','\\\\')
    return buf[0] + ':' + buf[1:]

def pick_frame(video_path, frame_num):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise Exception('Error')
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(frame_num))

    ret, frame = cap.read()

    return frame


def frame_check(frame, coord, base_color):
    X,Y = coord
    rgb = np.array(frame[Y,X][::-1])  # opencv is bgr, pillow is rgb
    return np.linalg.norm(rgb-base_color)


config = 'config.toml'
conf = toml.load(open(config))

videos = conf['target']['filename']

for video in videos:
    video_dos = dos_path(video)

    jsonfile = f'{video}.json'
    csvfile = f'{video}.csv'
    keyframefile = f'{video}_keyframes.txt'
    rangefile = f'{video}_ranges.txt'


    ffprobe = conf['win']['ffprobe']
    avidemux = conf['win']['avidemux']

    ssample = conf['image']['start_sample']
    esample = conf['image']['end_sample']

    if not os.path.isfile(keyframefile):

        #if not os.path.isfile(jsonfile):
        if not os.path.isfile(csvfile):
            print('creating keyframe file...')
            subprocess.run(
                f'{ffprobe} -show_frames -select_streams v:0 -show_entries frame=key_frame,pkt_pts_time,coded_picture_number -of csv=p=0 {video_dos} |grep "^1" > {csvfile}',
                #f'{ffprobe} -show_frames -select_streams v:0 -show_entries frame=key_frame,pkt_pts_time,coded_picture_number -print_format json {video_dos} > {jsonfile}',
                shell=True,
                text=True
                )

        with open(csvfile) as f:
            cobj = csv.reader(f)
            key_frames = list(cobj)
            #buf = json.load(f)['frames']

        print(f'there are {len(key_frames)} key frames')


        # 座標指定がない場合
        if 'coord' not in conf:
            # サンプル画像がなかったら切り出しをするよう指示
            if not os.path.isfile(ssample):
                print(f'please store picture when game starts by name `{ssample}\'')
                print(f'''import cv2
            def showpic(video_path, frame_num):
                cap = cv2.VideoCapture(video_path)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
                ret, frame = cap.read()
                cv2.imshow('img', frame)          # preview picture
                cv2.waitKey()
                return frame

            cv2.imwrite('{ssample}', frame)   # write picture
            ''')
                print('list of keyframes are')
                print([c[2] for c in key_frames])
                raise Exception(f'no {ssample}')

            if not os.path.isfile(esample):
                print(f'please store picture when game ends by name `{esample}\'')
                print(f'''import cv2
            def showpic(video_path, frame_num):
                cap = cv2.VideoCapture(video_path)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
                ret, frame = cap.read()
                cv2.imshow('img', frame)          # preview picture
                cv2.waitKey()
                return frame

            cv2.imwrite({esample}, frame)   # write picture
            ''')
                print('list of keyframes are')
                print([c[2] for c in key_frames])
                raise Exception(f'no {esample}')

            print('get two coordinates of start_sample and end_sample')
            print('do `python get_coordinate.py`')
            raise Exception(f'no coordinate')

        threshold = 10

        scoord1 = conf['coord'][f'1{ssample}']
        scolor1 = np.array(conf['coord'][f'1{ssample}_col'])
        scoord2 = conf['coord'][f'2{ssample}']
        scolor2 = np.array(conf['coord'][f'2{ssample}_col'])

        ecoord1 = conf['coord'][f'1{esample}']
        ecolor1 = np.array(conf['coord'][f'1{esample}_col'])
        ecoord2 = conf['coord'][f'2{esample}']
        ecolor2 = np.array(conf['coord'][f'2{esample}_col'])

        judges = []

        print('searching all keyframes for start/end points...')
        for c in tqdm.tqdm(key_frames):
            frame = pick_frame(video, c[2])

            if frame_check(frame, scoord1, scolor1) < threshold and \
                    frame_check(frame, scoord2, scolor2) < threshold:
                judges.append('s{0}'.format(c[1]))
            elif frame_check(frame, ecoord1, ecolor1) < threshold and \
                    frame_check(frame, ecoord2, ecolor2) < threshold:
                judges.append('e{0}'.format(c[1]))

        with open(keyframefile, 'w') as f:
            for j in judges:
                f.write(j+'\n')
    else:
        judges = open(keyframefile, 'r').read().rstrip().splitlines()

    if not os.path.isfile(rangefile):
        mode = ''
        ranges = []

        print('indicate start/end point for each game...')
        for l in judges:
            if mode == '' and l[0] == 's':
                ranges.append([l[1:], ])
                mode = 's'
            if mode == 's' and l[0] == 'e':
                mode = 'e'
                prev = l[1:]
            if mode == 'e':
                if l[0] == 's':
                    ranges[-1].append(prev)
                    ranges.append([l[1:], ])
                    mode = 's'
                else:
                    prev = l[1:]
        ranges[-1].append(prev)

        with open(rangefile, 'w') as f:
            cobj = csv.writer(f)
            cobj.writerows(ranges)
    else:
        ranges = list(csv.reader(open(rangefile)))
        print(ranges)


    script_path = mk_avidemuxpy.mk_avidemuxpy(video, video_dos, ranges)
    script_dos = dos_path(script_path)

    print('trimming...')

    proc = subprocess.run(f'"{avidemux}" --run "{script_dos}"',
        shell = True,
        text = True
    )
