#! /usr/bin/env python3

import os
import subprocess
import sys

Duration1 = float(subprocess.check_output('ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 PREDICT_RF01.mp4', shell=True))
Duration2 = float(subprocess.check_output('ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 PREDICT_RF01_FlightTrack.mp4', shell=True))

scalefactor = str(Duration1 / Duration2)

os.system('ffmpeg -i PREDICT_RF01_FlightTrack.mp4 -filter:v setpts=' + scalefactor + '*PTS mid_PREDICT_RF01_FlightTrack.mp4')

os.system('ffmpeg -i PREDICT_RF01.mp4 -vf "movie=mid_PREDICT_RF01_FlightTrack.mp4, scale=512:384 -1 [inner]; [in][inner] overlay=main_w-(overlay_w +0):0 [out]" combined_RF01.mp4')
