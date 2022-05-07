import argparse
from email.mime import audio
import os
from moviepy.editor import VideoFileClip

def file_exists(x):
    if not os.path.exists(x):
        raise argparse.ArgumentTypeError("{0} does not exist".format(x))
    return x

# video to audio
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='extract audio file from video')
    parser.add_argument('-i' '--in', dest="video_file", required=True, nargs=1, 
                        type=file_exists,
                        help='input video filepath')
    parser.add_argument('-o', '--out', dest='audio_file', nargs='?',
                        help='output audio filepath')

    args = parser.parse_args()
    video_path = os.path.abspath(args.video_file[0])
    if args.audio_file is not None:
        audio_path = os.path.abspath(args.audio_file)
    else:
        audio_path = os.path.splitext(video_path)[0] + '.wav'

    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path, ffmpeg_params=['-ar','16000','-ac','1'])
