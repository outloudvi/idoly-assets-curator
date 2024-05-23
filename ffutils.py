import os

import ffmpeg

dir_path = os.path.dirname(os.path.realpath(__file__))
ffmpeg_path = os.path.join(dir_path, "ffmpeg")


def ffmpeg_convert_format(byt, infmt, outfmt):
    try:
        (out, err) = ffmpeg.input("pipe:", format=infmt).output(
            "pipe:", format=outfmt).run(cmd=ffmpeg_path, input=byt, capture_stdout=True, capture_stderr=True)
        return out
    except ffmpeg.Error as e:
        print(f"Exception when calling ffmpeg: {e}")
        print(e.stderr)
        raise e


def wav_to_opus(byt):
    return ffmpeg_convert_format(byt, "wav", "opus")


def wav_to_mp3(byt):
    return ffmpeg_convert_format(byt, "wav", "mp3")
