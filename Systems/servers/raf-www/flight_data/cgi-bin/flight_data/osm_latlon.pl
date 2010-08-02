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
my $lon_s = $dbh->prepare(" SELECT value FROM global_attributes WHERE key='longitude_coordinate';")
	or die "Error preparing statement: " . DBI->errstr;
my $lat_s = $dbh->prepare(" SELECT value FROM global_attributes WHERE key='latitude_coordinate';")
	or die "Error preparing statement: " . DBI->errstr;
my $alt_s = $dbh->prepare(" SELECT value FROM global_attributes WHERE key='zaxis_coordinate';")
	or die "Error preparing statement: " . DBI->errstr;

$lat_s->execute()
	or die "Error executing statement: " . DBI->errstr;
$lon_s->execute()
	or die "Error executing statement: " . DBI->errstr;
$alt_s->execute()
	or die "Error executing statement: " . DBI->errstr;

my $lat_n = $lat_s->fetchrow_hashref;
my $lon_n = $lon_s->fetchrow_hashref;
my $alt_n = $alt_s->fetchrow_hashref;

# verify that column names are only words and/or spaces
if ( $lat_n->{'value'} !~ /[\s\w]+/ ||
	 $lon_n->{'value'} !~ /[\s\w]+/ ||
	 $alt_n->{'value'} !~ /[\s\w]+/ ) 
{
	print "invalid coordinates from global_attribues\n";
	exit;
}

# get column values
#my $loc = $dbh->prepare("SELECT ".$cols->{'lat'}.",".$cols->{'lon'}.",".$cols->{'alt'}." FROM raf_lrt ORDER BY datetime DESC LIMIT 2")
my $loc = $dbh->prepare("SELECT ".$lat_n->{value}.",".$lon_n->{value}.",".$alt_n->{value}." FROM raf_lrt ORDER BY datetime DESC LIMIT 2")
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
$lat_s->finish;
$lon_s->finish;
$alt_s->finish;
$dbh->disconnect;
