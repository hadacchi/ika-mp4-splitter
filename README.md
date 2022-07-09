# mp4 splitter

動画の開始フレームと終了フレーム (IDR) を自動検出し，1試合ごとに自動で切り出す．  
PJ名にikaとついているのは，スプラトゥーンのプレイ動画を想定しているためだが，
get_coordinate.pyで判定する場所と画素値を指定すれば，任意の動画で同じように処理
できる．

# requirements

- windowsのwsl環境のubuntuを前提にコードは作成されている
- ffprobe コマンドが使えること
- python 3.10以降が動作すること
    - 以下のライブラリが導入されていること．入ってない時は requirements.txt でインストール
        - numpy
        - opencv-python
        - toml
        - Pillow
        - tkinter

# usage

```shell
vi sandbox.py       # change video_path
python sandbox.py   # 開始フレーム，終了フレームの画像を各1枚準備する
python get_coordinate.py  # 判定に使う画素を指定する場合
```

# TODO

