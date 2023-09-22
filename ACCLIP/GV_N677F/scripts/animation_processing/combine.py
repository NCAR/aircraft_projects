#! /usr/bin/env python3

import os
import subprocess
import sys

# determine the length of the original movies and the flight track animations
Duration1 = float(subprocess.check_output('ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 ACCLIP_RF01.mp4', shell=True))
Duration2 = float(subprocess.check_output('ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 flight_track_RF01.mp4', shell=True))
scalefactor = str(Duration1 / Duration2)
# combine the movies and the flight track animations
os.system('ffmpeg -i flight_track_RF01.mp4 -filter:v setpts=' + scalefactor + '*PTS mid_flight_track_RF01.mp4')
os.system('ffmpeg -i ACCLIP_RF01.mp4 -vf "movie=mid_flight_track_RF01.mp4, scale=514:192 -1 [inner]; [in][inner] overlay=main_w-(overlay_w +0):0 [out]" combined_flight_track_RF01.mp4')

# determine the length of the combined flight track animations and the altitude animations
Duration1 = float(subprocess.check_output('ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 combined_flight_track_RF01.mp4', shell=True))
Duration2 = float(subprocess.check_output('ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 altitude_RF01.mp4', shell=True))
scalefactor = str(Duration1 / Duration2)
# combine the movies with flight track animations and the altitude animations
os.system('ffmpeg -i altitude_RF01.mp4 -filter:v setpts=' + scalefactor + '*PTS mid_altitude_RF01.mp4')
os.system('ffmpeg -i combined_flight_track_RF01.mp4 -vf "movie=mid_altitude_RF01.mp4, scale=514:192 -1 [inner]; [in][inner] overlay=main_w-(overlay_w +0):192 [out]" RF01_combined.mp4')
