#import math
#import os
from PIL import Image, ImageTk  # 外部ライブラリ
import tkinter
import toml

config = 'config.toml'
conf = toml.load(open(config))
#del config['target']


def start_point_get(event):
    '''ドラッグ開始時
    '''
    global start_x, start_y  # グローバル変数に書き込みを行なうため宣言

    canvas1.delete("rect1")  # すでに"rect1"タグの図形があれば削除

    # canvas1上に四角形を描画（rectangleは矩形の意味）
    canvas1.create_rectangle(event.x, event.y,
                             event.x + 1, event.y + 1,
                             outline="red",
                             tag="rect1")
    # グローバル変数に座標を格納
    start_x, start_y = event.x, event.y
    # 座標を表示
    show_coord([start_x, start_y])


def release_action(event):
    '''リリース時
    '''
    global start_x, start_y, end_x, end_y, X, Y  # global variables
    # "rect1"タグの画像の座標を元の縮尺に戻して取得
    start_x, start_y, end_x, end_y = [
        n * resize_ratio for n in canvas1.coords("rect1")
    ]
    
    X = round((start_x + end_x)/2)
    Y = round((start_y + end_y)/2)
    show_coord([X, Y])

    # 座標を取得し出力
    get_coord()


def show_msg():
    '''display target
    '''
    tag, msg = target_list[target_idx]
    canvas1.create_text(int(img_resized.width * 0.05),
                        int(img_resized.height * 0.05),
                        text=msg,
                        fill='red',
                        anchor=tkinter.NW,
                        tag=tag)


def show_coord(arr):
    '''show coordinate
    '''
    canvas1.delete('coord')
    canvas1.create_text(int(img_resized.width * 0.05),
                        int(img_resized.height * 0.1),
                        text=' '.join([str(e) for e in arr]),
                        fill='red',
                        anchor=tkinter.NW,
                        tag='coord')


def get_coord():
    '''get coordinate
    '''
    global target_idx
    if target_idx < len(target_list):
        tag = target_list[target_idx][0]
        dict_tag = tag.format(img_path)
        # 画素値ゲット
        val = img.getpixel((X,Y))

        out[dict_tag] = [X, Y]
        out[dict_tag + '_col'] = val

        canvas1.delete('color')
        canvas1.create_text(int(img_resized.width * 0.05),
                            int(img_resized.height * 0.15),
                            text=str(val),
                            fill='red',
                            anchor=tkinter.NW,
                            tag='color')

        canvas1.delete(tag)
        target_idx += 1
        if target_idx < len(target_list):
            show_msg()
        else:
            conf['coord'] = out
            toml.dump(conf, open(config, 'w'))
            canvas1.create_text(int(img_resized.width * 0.05),
                                int(img_resized.height * 0.05),
                                text='Please Cmd-w to close image',
                                fill='red',
                                anchor=tkinter.NW,
                                tag=tag)


out = {}

target_list = [
    ['1{0}', 'Where is 1st point?'],
    ['2{0}', 'Where is 2nd point?'],
]

if __name__ == "__main__":

    # 表示する画像の取得（frame）
    ssample = conf['image']['start_sample']
    esample = conf['image']['end_sample']

    for img_path in [ssample, esample]:
        target_idx = 0
        img = Image.open(img_path)

        # スクリーンショットした画像は表示しきれないので画像リサイズ
        h = min(img.height, 800)
        resize_ratio = img.height / h
        print(f'resize ratio is {resize_ratio}')
        img_resized = img.resize(size=(int(img.width // resize_ratio),
                                       int(img.height // resize_ratio)),
                                 resample=Image.Resampling.BILINEAR)

        root = tkinter.Tk()
        root.attributes("-topmost", True)  # tkinterウィンドウを常に最前面に表示

        # tkinterで表示できるように画像変換
        img_tk = ImageTk.PhotoImage(img_resized)

        # Canvasウィジェットの描画
        canvas1 = tkinter.Canvas(root,
                                 bg="black",
                                 width=img_resized.width,
                                 height=img_resized.height)
        # Canvasウィジェットに取得した画像を描画
        canvas1.create_image(0, 0, image=img_tk, anchor=tkinter.NW)

        # 領域指定
        show_msg()

        # Canvasウィジェットを配置し、各種イベントを設定
        canvas1.pack()
        canvas1.bind("<ButtonPress-1>", start_point_get)
        #canvas1.bind("<Button1-Motion>", rect_drawing)
        canvas1.bind("<ButtonRelease-1>", release_action)

        root.mainloop()
