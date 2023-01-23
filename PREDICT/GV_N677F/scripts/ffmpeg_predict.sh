#! /usr/bin/bash

ffmpeg -pattern_type glob -i '*.jpg' -c:v libx264 -r 15 -pix_fmt yuv420p -y output.mp4
