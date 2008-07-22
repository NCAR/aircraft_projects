#!/bin/sh

source /root/.profile

PATH=/var/tmp/bin:$PATH
export LD_LIBRARY_PATH=/var/tmp/lib

dsm -d '$ADS3/projects/$PROJECT/$AIRCRAFT/nidas/cvi.xml'

