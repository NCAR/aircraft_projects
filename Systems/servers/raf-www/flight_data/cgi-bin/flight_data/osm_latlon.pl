#!/usr/bin/perl -T

use strict;
use DBI;
use Math::Trig;

our $q; our %plat_vars;
require "./getCookie.pl";

#set up db connection and request
my $dbh = DBI->connect("dbi:Pg:database=$plat_vars{dbname};host=$plat_vars{'dbhost'}", "ads")
	or die "Error connecting to db: " . DBI->errstr;

# get column names
my $col_s = $dbh->prepare(" SELECT split_part(value,' ',1) as lon,split_part(value,' ',2) as lat,split_part(value,' ',3) as alt from global_attributes where key='coordinates';")
	or die "Error preparing statement: " . DBI->errstr;
$col_s->execute()
	or die "Error executing statement: " . DBI->errstr;
my $cols = $col_s->fetchrow_hashref;

# verify that column names are only words and/or spaces
if ( $cols->{'lat'} !~ /[\s\w]+/ ||
	 $cols->{'lon'} !~ /[\s\w]+/ ||
	 $cols->{'alt'} !~ /[\s\w]+/ ) 
{
	print "invalid coordinates from global_attribues\n";
	exit;
}

# get column values
my $loc = $dbh->prepare("SELECT ".$cols->{'lat'}.",".$cols->{'lon'}.",".$cols->{'alt'}." FROM raf_lrt ORDER BY datetime DESC LIMIT 2")
	or die "Error preparing statement: " . DBI->errstr;
$loc->execute()
	or die "Error executing statement: " . DBI->errstr;
my $row3 = $loc->fetchall_arrayref;

#sort data into senseable vars
my $alt = $row3->[0]->[2];

my $lat2 = $row3->[0]->[0]; 
my $lon2 = $row3->[0]->[1]; 
my $lat1 = $row3->[1]->[0]; 
my $lon1 = $row3->[1]->[1]; 

#validate data (make sure all vars are only numbers, decimals or -
if ( 
	($alt =~ /^-?[\d\.]+$/) &&
	($lat1 =~ /^-?[\d\.]+$/) &&
	($lat2 =~ /^-?[\d\.]+$/) &&
	($lon1 =~ /^-?[\d\.]+$/) &&
	($lon2 =~ /^-?[\d\.]+$/)
   ) 
{ 
	
	#find bearing based on last two GPS coords
	my $rlat1 = $lat1 * pi/180;
	my $rlon1 = $lon1 * pi/180;
	my $rlat2 = $lat2 * pi/180;
	my $rlon2 = $lon2 * pi/180;
	
	my $y = sin($rlon2 - $rlon1)*cos($rlat2);
	my $x = cos($rlat1)*sin($rlat2) - sin($rlat1)*cos($rlat2)*cos($rlon2-$rlon1);
	
	my $th = int( (atan2($y, $x) * 180/pi + 360) + 0.5);
	
	#return result in JSON format
	print "{\"alt\":\"$alt\",\"lat\":\"$lat1\",\"head\":\"$th\",\"declination\":\"0\",\"lon\":\"$lon1\"}";

}
else {
	print "{\"alt\":\"0\",\"lat\":\"0\",\"head\":\"0\",\"declination\":\"0\",\"lon\":\"0\",\"error\":\"invalid data from db\"}";
}

#disconnect from db
$loc->finish;
$col_s->finish;
$dbh->disconnect;
