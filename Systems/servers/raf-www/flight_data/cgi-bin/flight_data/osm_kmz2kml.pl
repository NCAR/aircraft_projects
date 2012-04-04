#!/usr/bin/perl -T
#
# COPYRIGHT: University Corporation for Atmospheric Research, 2009-12
#

use strict;
use File::Basename;

our $q; our %plat_vars; our $header="application/vnd.google-earth.kml+xml";
require "./getCookie.pl";

# $in holds the name of the kmz we want to decompress
my $in = $q->param('kmz');

# use fileparse to ignore any directory structure and 
#  just get the filename, this also prevents users from
#  displaying the contents of other files
my ($n,$p,$s) = fileparse($in);

# create the final path that will be passed to unzip
$n =~ /([-\w\.]+\.kmz)$/i;		 #untaint
my $kmz = "GE/$1";

# check to make sure the file exists, if so - unzip it
if ( -e $plat_vars{'docs_path'}."$kmz" ) {
	local $ENV{"PATH"}="";

	open(KML, "/usr/bin/unzip -p ".$plat_vars{'docs_path'}."$kmz|")
		or die "no pipe\n";

	while(<KML>) {
		#untaint kml => '$' not allowed
		# This is rather weak untainting, however the MIME
		# type is not HTML, so it should not be parsed by
		# the browser. Also, only files in the GE directory
		# can be accessed.
		$_ =~ /^([^\$]+)$/;
		print $1;
	}	

	close(KML);
} else {
	print "could not find file $kmz";
}
