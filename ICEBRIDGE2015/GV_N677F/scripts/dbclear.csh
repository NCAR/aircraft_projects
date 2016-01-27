#!/bin/csh
setenv PGHOST eol-rt-data.guest.ucar.edu
setenv PGDATABASE real-time-GV

/usr/bin/psql < /h/eol/ads/ICEBRIDGE/sql.cmds.txt
