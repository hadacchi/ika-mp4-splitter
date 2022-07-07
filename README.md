# mp4 splitter

スプラ動画の開始フレームと終了フレーム (IDR) を自動検出し，1試合ごとに自動で切り出す

# requirements

- ffprobe コマンドが使えること
- python 3.10以降が動作すること
    - 以下のライブラリが導入されていること
        - numpy
        - opencv
        - toml
        - Pillow
        - tkinter

# usage

```shell
keyframe.sh *.MP4
vi sandbox.py       # change video_path
python sandbox.py   # 開始フレーム，終了フレームの画像を各1枚準備する
python get_coordinate.py  # 判定に使う画素を指定する
python sandbox.py   # 逐次処理 (start end の判定をされたフレームを出力するだけ)
```

# TODO

- 複数の連続したstart/end判定の最初と最後を指定する
- avidemuxでlossless自動切り出し
- 長い動画で誤判定となるパターンがないか検証
- githubで公開