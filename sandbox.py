import json
#from tkinter import W
#import matplotlib.pyplot as plt
#from PIL import Image
import csv
import cv2
#import time
import os
import toml
import numpy as np

def pick_frame(video_path, frame_num):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise Exception('Error')
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)

    ret, frame = cap.read()

    return frame


def frame_check(frame, coord, base_color):
    X,Y = coord
    rgb = np.array(frame[Y,X][::-1])  # opencv is bgr, pillow is rgb
    return np.linalg.norm(rgb-base_color)


config = 'config.toml'
video = '/mnt/e/編集中Videos/ika/IOHD0573.MP4'
jsonfile = f'{video}.json'
keyframefile = f'{video}_keyframes.txt'
rangefile = f'{video}_ranges.txt'

conf = toml.load(open(config))

ssample = conf['image']['start_sample']
esample = conf['image']['end_sample']

if not os.path.isfile(keyframefile):

    if not os.path.isfile(jsonfile):
        print('please search for keyframes')
        print('ffprobe -show_frames -select_streams v -print_format json video_path > json_path')
        raise Exception('no json')

    with open(jsonfile) as f:
        buf = json.load(f)['frames']

    key_frames = [f for f in buf if f['key_frame'] == 1]
    print(f'the num of all frames is {len(buf)}, there are {len(key_frames)} key frames')


    # 座標
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
            print([f['coded_picture_number'] for f in key_frames])
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
            print([f['coded_picture_number'] for f in key_frames])
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

    for fr_info in key_frames:
        frame = pick_frame(video, fr_info['coded_picture_number'])
        fr_num = fr_info['coded_picture_number']
        #cv2.imwrite(f'{fr_num}.jpg', frame)

        if frame_check(frame, scoord1, scolor1) < threshold and \
                frame_check(frame, scoord2, scolor2) < threshold:
            judges.append('s{0}'.format(fr_info['coded_picture_number']))
        elif frame_check(frame, ecoord1, ecolor1) < threshold and \
                frame_check(frame, ecoord2, ecolor2) < threshold:
            judges.append('e{0}'.format(fr_info['coded_picture_number']))

    with open(keyframefile, 'w') as f:
        for j in judges:
            f.write(j+'\n')
else:
    judges = open(keyframefile, 'r').read().rstrip().splitlines()

mode = ''
ranges = []

for l in judges:
    if mode == '' and l[0] == 's':
        ranges.append([l[1:], ])
        mode = 's'
    if mode == 's' and l[0] == 'e':
        mode = 'e'
        prev = l[1:]
    if mode == 'e' and l[0] == 's':
        ranges[-1].append(prev)
        ranges.append([l[1:], ])
        mode = 's'
ranges[-1].append(prev)

with open(rangefile, 'w') as f:
    cobj = csv.writer(f)
    cobj.writerows(ranges)
    #for r in ranges:
    #    f.write(r+'\n')


