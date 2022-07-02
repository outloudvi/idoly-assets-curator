import os

import ffmpeg

dir_path = os.path.dirname(os.path.realpath(__file__))
ffmpeg_path = os.path.join(dir_path, "ffmpeg")


def ffmpeg_convert_format(byt, infmt, outfmt):
    return (
        ffmpeg
        .input("pipe:", format=infmt)
        .output("pipe:", format=outfmt)
        .run(cmd=ffmpeg_path, input=byt, capture_stdout=True)
    )[0]


def wav_to_opus(byt):
    return ffmpeg_convert_format(byt, "wav", "opus")


def wav_to_mp3(byt):
    return ffmpeg_convert_format(byt, "wav", "mp3")
