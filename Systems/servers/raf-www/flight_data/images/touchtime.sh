#!/bin/bash

for i in ls /var/www/html/flight_data/images/*ops* 
do 
	if [ "$i" != "ls" ]; then
		DATE=$(echo $i | awk -F. '{print $3}')
		touch --date="${DATE:0:4}-${DATE:4:2}-${DATE:6:2} ${DATE:8:2}:${DATE:10:2}" $i
	fi
done

