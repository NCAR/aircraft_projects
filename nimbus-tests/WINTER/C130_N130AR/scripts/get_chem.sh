#!/bin/bash

cd /var/www/html/flight_data/images

wget http://www.eol.ucar.edu/flight_data/C130/images/urban_NOx.png -O tmp.png

if [ -s tmp.png ]; then
  /bin/mv tmp.png urban_NOx.png
fi

/bin/rm tmp.png
