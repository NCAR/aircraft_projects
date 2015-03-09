#!/usr/bin/python
#
# Generic script to return aircraft, project, and instrument configuration onboard
#
# Get operations will be for specific actions using '.' to denote hierarchy.
#
# Current top level are: aircraft, project, cameras
#
#  examples: aircraft.tailnumber, project.path, project.name, project.flightnumber, cameras.path
#		toga.path, mtp.path, avaps.path
#
#  COPYRIGHT: University Corporation for Atmospheric Research, 2015

import os
import sys

# PostGreSQL
import psycopg2

instrument_path_base = '/mnt/r1/'

ac_config_dict = {
	'aircraft.tailnumber' : os.getenv("AIRCRAFT"),
	'project.name' : os.getenv("PROJECT"),
	'project.path' : os.getenv("PROJ_DIR")
	} 


def connect_db():
  return psycopg2.connect(database="real-time", user="ads", host="acserver")

# For ground testing.
def connect_db_ground():
  return psycopg2.connect(database="real-time-C130", user="ads", host="eol-rt-data.fl-ext.ucar.edu")


if len(sys.argv) < 2:
  sys.exit(1)



# Open real-time onboard database
db = connect_db()
cur = db.cursor()

# Get flight number from database.
cur.execute("SELECT value FROM global_attributes WHERE key='FlightNumber';")
rows = cur.fetchall()
ac_config_dict['project.flightnumber'] = rows[0][0]


# Assemble camera path.
cpath = instrument_path_base + ac_config_dict['project.name']
cpath += '/camera_images/flight_number_'
cpath += ac_config_dict['project.flightnumber']

ac_config_dict['cameras.path'] = cpath

ac_config_dict['toga.path'] = instrument_path_base + ac_config_dict['project.name'] + '/toga'
ac_config_dict['mtp.path'] = instrument_path_base + ac_config_dict['project.name'] + '/mtp'
ac_config_dict['avaps.path'] = instrument_path_base + ac_config_dict['project.name'] + '/avaps'


db.close()

print ac_config_dict[sys.argv[1]]
