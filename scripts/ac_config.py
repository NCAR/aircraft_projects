#!/usr/bin/env python3
#
# Generic script to return aircraft, project, and instrument configuration
# onboard
#
# Get operations will be for specific actions using '.' to denote hierarchy.
#
# Current top level are: aircraft, project, cameras, dropsonde
#
#  examples: aircraft.tailnumber, project.path, project.name,
#            project.flightnumber, cameras.path, toga.path, mtp.path,
#            dropsonde.path
#
#  COPYRIGHT: University Corporation for Atmospheric Research, 2015

import os
import sys

# PostGreSQL
import psycopg2

instrument_path_base = '/var/r1/'
www_path_base = '/var/www/html'

ac_config_dict = {
	'aircraft.tailnumber' : os.getenv("AIRCRAFT"),
	'project.name' : os.getenv("PROJECT"),
	'project.path' : os.getenv("PROJ_DIR")
	} 


def connect_db():
  return psycopg2.connect(database="real-time", user="ads", host="acserver")

# For ground testing.
def connect_db_ground():
  return psycopg2.connect(database="real-time-C130", user="ads",
                          host="eol-rt-data.ml-ext.ucar.edu")


def get_config(key):

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

  ac_config_dict['toga.path'] = instrument_path_base + \
                                ac_config_dict['project.name'] + '/toga'
  ac_config_dict['mtp.path'] = instrument_path_base + \
                               ac_config_dict['project.name'] + '/mtp'
  ac_config_dict['dropsonde.raw_path'] = instrument_path_base + '/dropsondes'
  ac_config_dict['dropsonde.skewt_path'] = www_path_base + '/skewt'

  db.close()

  return ac_config_dict.get(key, None)
