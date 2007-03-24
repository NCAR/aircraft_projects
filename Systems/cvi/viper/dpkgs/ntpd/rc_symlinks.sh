#!/bin/sh

# set -x

cd etc
 
[ -d rc0.d ] || mkdir rc0.d
[ -d rc1.d ] || mkdir rc1.d
[ -d rc2.d ] || mkdir rc2.d
[ -d rc6.d ] || mkdir rc6.d

cd rc0.d
[ -L K77ntpd ] || ln -s ../init.d/ntpd K77ntpd

cd ../rc1.d
[ -L K77ntpd ] || ln -s ../init.d/ntpd K77ntpd

cd ../rc6.d
[ -L K77ntpd ] || ln -s ../init.d/ntpd K77ntpd

cd ../rc2.d
[ -L S21gps ] || ln -s ../init.d/gps S21gps
[ -L S22ntpdate ] || ln -s ../init.d/ntpdate S22ntpdate
[ -L S23ntpd ] || ln -s ../init.d/ntpd S23ntpd
