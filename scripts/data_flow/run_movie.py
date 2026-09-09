#!/usr/bin/env python
from _setup import Setup #setup, myLogger
import subprocess
import sys

setup = Setup()

# Now that the processing has completed, attempt to run the movie-generation script
if setup.FLIGHT.upper().startswith(('RF', 'TF', 'FF')):
  try:
    script = "/home/local/aircraft_movies_animations/timeseries_animation.py"
    subprocess.run([script, "-f", setup.FLIGHT], check=True)
  except subprocess.CalledProcessError as e:
      print(f"Movie generation failed: {e.stderr}")
else:
    print("Not an RF/TF/FF flight. Movie generation skipped.")
