#!/usr/bin/python

#
#  COPYRIGHT: University Corporation for Atmospheric Research, 2014
#

import urllib
import urllib2

nasaResp = urllib2.urlopen("http://asp2.arc.nasa.gov/dashlite/dash.php?ACTION=FETCH_LAST_POS&CALLSIGN=NASA426")

sRes = nasaResp.read()
aIWG = sRes.split(",")

P3_kml_file = '/var/www/html/flight_data/GE/P3_current_pos.kml'
#P3_kml_file = './P3_current_pos.new.kml'

dt_tm = aIWG[1].split("T")
time =  dt_tm[1]
lat = aIWG[2]
lon = aIWG[3]
alt = aIWG[6]
temp = aIWG[20]
dp = aIWG[21]
ws = aIWG[26]
wd = aIWG[27]
wi = aIWG[28]

print time+" "+lat+" "+lon+" "+alt+" "+temp+" "+dp+" "+ws+" "+wd+" "+wi+"\n"
with open (P3_kml_file, "w") as kml_file:
    kml_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    kml_file.write('<kml xmlns="http://www.opengis.net/kml/2.2"\n')    
    kml_file.write(' xmlns:gx="http://www.google.com/kml/ext/2.2">\n')
    kml_file.write('<Document>\n')
    kml_file.write(' <name>FRAPPE rf05</name>\n')
    kml_file.write(' <Style id="PM1">\n')
    kml_file.write('  <IconStyle>\n')
    kml_file.write('   <scale>0.8</scale>\n')
    kml_file.write('   <Icon>\n')
    kml_file.write('    <href>http://acserver.raf.ucar.edu/flight_data/display/blackplane.png</href>\n')
    kml_file.write('   </Icon>\n')
    kml_file.write('  </IconStyle>\n')
    kml_file.write(' </Style>\n')
    kml_file.write(' <Folder>\n')
    kml_file.write('  <name>Current Position</name>\n')
    kml_file.write('  <Placemark>\n')
    kml_file.write('   <name>NASA426</name>\n')
    kml_file.write('   <description><![CDATA[')
    kml_file.write(time+'<br>')
    kml_file.write(' Lat  : '+lat+' deg_N<br>')
    kml_file.write(' Lon  : '+lon+' deg_E<br>')
    kml_file.write(' Alt  : '+alt+' feet<br>')
    kml_file.write(' Temp : '+temp+' Deg_C<br>')
    kml_file.write(' DP   : '+dp+' Deg_C<br>')
    kml_file.write(' WS   : '+ws+' m/s<br>')
    kml_file.write(' WD   : '+wd+'  degree_T<br>')
    kml_file.write(' WI   : '+wi+'  m/s<br>')
    kml_file.write(']]></description>\n')
    kml_file.write('   <styleUrl>#PM1</styleUrl>\n')
    kml_file.write('   <Point>\n')
    kml_file.write('    <coordinates>'+lon+','+lat+','+alt+'</coordinates>\n')
    kml_file.write('   </Point>\n')
    kml_file.write('  </Placemark>\n')
    kml_file.write(' </Folder>\n')
    kml_file.write('</Document>\n')
    kml_file.write('</kml>\n')
