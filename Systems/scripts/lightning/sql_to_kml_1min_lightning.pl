#!/usr/bin/perl

$| = 1;

# This script reads the PsotgreSQL database for 1-min lightning data and pulls out the last hour
# data based on the current time. The last hour is then put into placemarks in 5-10 minute bins

use DBI;

$host = "eol-rt-data.guest.ucar.edu";
#$host = "hyper.guest.ucar.edu";
#$host = "acserver.raf.ucar.edu";

$output = "/var/www/html/GE/last_hour_lightning.kml";
$output1 = "/var/www/html/GE/last_hour_lightning.tmp";

open(OUT,">$output1") || die "Unable to open output file:$output1";
print OUT "<kml xmlns=\"http://earth.google.com/kml/2.1\">\n<Document>\n<name>Lightning Strikes</name>\n" ;
print OUT "<Style id=\"plus\">\n<IconStyle>\n<Icon>\n";
print OUT "<href>http://acserver.raf.ucar.edu/GE/images/plus.png</href>\n";
print OUT "</Icon>\n</IconStyle>\n</Style>\n";
print OUT "<Style id=\"plusFive\">\n<IconStyle>\n<Icon>\n";
print OUT "<href>http://acserver.raf.ucar.edu/GE/images/plus5.png</href>\n";
print OUT "</Icon>\n</IconStyle>\n</Style>\n";
print OUT "<Style id=\"plusTen\">\n<IconStyle>\n<Icon>\n";
print OUT "<href>http://acserver.raf.ucar.edu/GE/images/plus10.png</href>\n";
print OUT "</Icon>\n</IconStyle>\n</Style>\n";
print OUT "<Style id=\"plusFifteen\">\n<IconStyle>\n<Icon>\n";
print OUT "<href>http://acserver.raf.ucar.edu/GE/images/plus15.png</href>\n";
print OUT "</Icon>\n</IconStyle>\n</Style>\n";
print OUT "<Style id=\"plusTwenty\">\n<IconStyle>\n<Icon>\n";
print OUT "<href>http://acserver.raf.ucar.edu/GE/images/plus20.png</href>\n";
print OUT "</Icon>\n</IconStyle>\n</Style>\n";
print OUT "<Style id=\"plusThirty\">\n<IconStyle>\n<Icon>\n";
print OUT "<href>http://acserver.raf.ucar.edu/GE/images/plus30.png</href>\n";
print OUT "</Icon>\n</IconStyle>\n</Style>\n";
print OUT "<Style id=\"minus\">\n<IconStyle>\n<Icon>\n";
print OUT "<href>http://acserver.raf.ucar.edu/GE/images/minus.png</href>\n";
print OUT "</Icon>\n</IconStyle>\n</Style>\n";
print OUT "<Style id=\"minusFive\">\n<IconStyle>\n<Icon>\n";
print OUT "<href>http://acserver.raf.ucar.edu/GE/images/minus5.png</href>\n";
print OUT "</Icon>\n</IconStyle>\n</Style>\n";
print OUT "<Style id=\"minusTen\">\n<IconStyle>\n<Icon>\n";
print OUT "<href>http://acserver.raf.ucar.edu/GE/images/minus10.png</href>\n";
print OUT "</Icon>\n</IconStyle>\n</Style>\n";
print OUT "<Style id=\"minusFifteen\">\n<IconStyle>\n<Icon>\n";
print OUT "<href>http://acserver.raf.ucar.edu/GE/images/minus15.png</href>\n";
print OUT "</Icon>\n</IconStyle>\n</Style>\n";
print OUT "<Style id=\"minusTwenty\">\n<IconStyle>\n<Icon>\n";
print OUT "<href>http://acserver.raf.ucar.edu/GE/images/minus20.png</href>\n";
print OUT "</Icon>\n</IconStyle>\n</Style>\n";
print OUT "<Style id=\"minusThirty\">\n<IconStyle>\n<Icon>\n";
print OUT "<href>http://acserver.raf.ucar.edu/GE/images/minus30.png</href>\n";
print OUT "</Icon>\n</IconStyle>\n</Style>\n";
print OUT "<Style id=\"cloud\">\n<IconStyle>\n<Icon>\n";
print OUT "<href>http://acserver.raf.ucar.edu/GE/images/cloud.png</href>\n";
print OUT "</Icon>\n</IconStyle>\n</Style>\n";
print OUT "<Style id=\"cloudFive\">\n<IconStyle>\n<Icon>\n";
print OUT "<href>http://acserver.raf.ucar.edu/GE/images/cloud5.png</href>\n";
print OUT "</Icon>\n</IconStyle>\n</Style>\n";
print OUT "<Style id=\"cloudTen\">\n<IconStyle>\n<Icon>\n";
print OUT "<href>http://acserver.raf.ucar.edu/GE/images/cloud10.png</href>\n";
print OUT "</Icon>\n</IconStyle>\n</Style>\n";
print OUT "<Style id=\"cloudFifteen\">\n<IconStyle>\n<Icon>\n";
print OUT "<href>http://acserver.raf.ucar.edu/GE/images/cloud15.png</href>\n";
print OUT "</Icon>\n</IconStyle>\n</Style>\n";
print OUT "<Style id=\"cloudTwenty\">\n<IconStyle>\n<Icon>\n";
print OUT "<href>http://acserver.raf.ucar.edu/GE/images/cloud20.png</href>\n";
print OUT "</Icon>\n</IconStyle>\n</Style>\n";
print OUT "<Style id=\"cloudThirty\">\n<IconStyle>\n<Icon>\n";
print OUT "<href>http://acserver.raf.ucar.edu/GE/images/cloud30.png</href>\n";
print OUT "</Icon>\n</IconStyle>\n</Style>\n";
#print OUT "<visibility>1</visibility>\n<open>0</open>\n";

$dbh = DBI->connect("dbi:Pg:dbname=real-time;host=$host",'ads','',{AutoCommit => 1, RaiseError => 1, PrintError => 0});

# Set up loop to move through the last 60 minutes
for($i = 0; $i < 6; $i++) {

#   $i = 1;
# Compute time parameters for query
   ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = gmtime(time-(60*$i));
   $mon++;
   $year+=1900;

   $time = sprintf("%4d-%02d-%02d %02d:%02d",$year,$mon,$mday,$hour,$min);
# Test settings
#   $year = "2009";
#   $mon = "07";
#   $mday = "28";
#   $hour = "16";
#   $min = "58";

#   print "Getting data for $year-$mon-$mday $hour:$min\n";
   print "Getting data for $time\n";

   $query = "SELECT * from lightning where datetime ~ '$time'";
   $sth = $dbh->prepare($query);
   $result = $sth->execute();

   while ( @row = $sth->fetchrow_array ) {
#      print "@row\n";
#      print "0:$row[0], 1:$row[1], 2:$row[2], 3:$row[3]\n";

# Choose placemark for KML based on flash amplitude
          if($row[3] > 0 ) {
             if ($i < 5 ) {
                 $placemark_graphic = "#plus";
             } elsif($i >=5 && $i < 10) {
                 $placemark_graphic = "#plusFive";
             } elsif($i >=10 && $i < 15) {
                 $placemark_graphic = "#plusTen";
             } elsif($i >=15 && $i < 20) {
                 $placemark_graphic = "#plusFifteen";
             } elsif($i >=20 && $i < 30) {
                 $placemark_graphic = "#plusTwenty";
             } elsif($i >=30 && $i < 40) {
                 $placemark_graphic = "#plusThirty";
             } elsif($i >=40 && $i < 50) {
                 $placemark_graphic = "#plusForty";
             } elsif($i >=50 && $i < 60) {
                 $placemark_graphic = "#plusFifty";
             } elsif($i >=60) {
                 $placemark_graphic = "#plusSixty";
             }
          } elsif($row[3] < 0 ) {
             if ($i < 5 ) {
                 $placemark_graphic = "#minus";
             } elsif($i >=5 && $i < 10) {
                 $placemark_graphic = "#minusFive";
             } elsif($i >=10 && $i < 15) {
                 $placemark_graphic = "#minusTen";
             } elsif($i >=15 && $i < 20) {
                 $placemark_graphic = "#minusFifteen";
             } elsif($i >=20 && $i < 30) {
                 $placemark_graphic = "#minusTwenty";
             } elsif($i >=30 && $i < 40) {
                 $placemark_graphic = "#minusThirty";
             } elsif($i >=40 && $i < 50) {
                 $placemark_graphic = "#minusForty";
             } elsif($i >=50 && $i < 60) {
                 $placemark_graphic = "#minusFifty";
             } elsif($i >=60) {
                 $placemark_graphic = "#minusSixty";
             }
          } elsif($row[3] == 0 ) {
             if ($i < 5 ) {
                 $placemark_graphic = "#cloud";
             } elsif($i >=5 && $i < 10) {
                 $placemark_graphic = "#cloudFive";
             } elsif($i >=10 && $i < 15) {
                 $placemark_graphic = "#cloudTen";
             } elsif($i >=15 && $i < 20) {
                 $placemark_graphic = "#cloudFifteen";
             } elsif($i >=20 && $i < 30) {
                 $placemark_graphic = "#cloudTwenty";
             } elsif($i >=30 && $i < 40) {
                 $placemark_graphic = "#cloudThirty";
             } elsif($i >=40 && $i < 50) {
                 $placemark_graphic = "#cloudForty";
             } elsif($i >=50 && $i < 60) {
                 $placemark_graphic = "#cloudFifty";
             } elsif($i >=60) {
                 $placemark_graphic = "#cloudSixty";
             }
          } 

#          print OUT "<Placemark>\n<name>$i minutes ago</name>\n<visibility>1</visibility>\n";
          print OUT "<Placemark>\n";
          #print OUT "<description><b>Date/Time:$row[0]</b><p><b>Amplitude: $row[3]</b></p></description>\n";
          print OUT "<description>Date/Time:$row[0]\nAmplitude: $row[3]</description>\n";
#          print OUT "<description><b>Date/Time:$row[0]</b><p><b>Latitude: $row[1]</b></p>";
#          print OUT "<p><b>Longitude: $row[2]</b></p><p><b>Amplitude: $row[3]</b></p></description>\n";
#          print OUT "<TimeStamp><when>$row[0]</when></TimeStamp>\n";
          print OUT "<styleUrl>$placemark_graphic</styleUrl><Region />\n";
#          print OUT "<Point><extrude>0</extrude><tessellate>0</tessellate>\n";
          print OUT "<Point>\n";
          print OUT "<altitudeMode>clampToGround</altitudeMode>\n";
          print OUT "<coordinates>$row[2],$row[1],0</coordinates>\n</Point>\n</Placemark>\n";

   }

}
          print OUT "</Document>\n</kml>\n";
	  close OUT;
	  unlink($output);
	  rename($output1, $output);
