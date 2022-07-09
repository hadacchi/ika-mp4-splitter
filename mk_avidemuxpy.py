

templete_head = '''adm = Avidemux()
if not adm.loadVideo("{video_name}"):
    raise("Cannot load {video_name}")
adm.videoCodec("Copy")
adm.audioCodec(0, "copy");
'''

templete_body = '''
adm.markerA = {start}
adm.markerB = {end}
adm.save("{target}")
'''

def mk_avidemuxpy(video, video_dos, ranges):
    dirpath = '/'.join(video.split('/')[:-1])
    script_name = f'{dirpath}/tmp.py'

    with open(script_name, 'w') as f:
        f.write(templete_head.format(video_name = video_dos))
        for i, r in enumerate(ranges):
            x,y = r[0].split('.')
            y = (y + '000000')[:6]  # 6-digit number
            start = int(x+y)
            x,y = r[1].split('.')
            y = (y + '000000')[:6]  # 6-digit number
            end = int(x+y)
            target = video_dos + f'_{i:02d}.mp4'
            f.write(templete_body.format(start = start,
                end = end,
                target = target))

    return script_name
