#!/usr/bin/perl -T
#
# COPYRIGHT: University Corporation for Atmospheric Research, 2009-12
#

use strict;

our $q; our %plat_vars;
require "./getCookie.pl";
my $plat_param = $q->param("platform");
my $newplat = ($plat_param ne "")? 'true': 'false'; 

print <<endHEAD;
<html>

  <head>
	<title>Flight Data</title>
	<link rel="icon" type="image/png" href="/flight_data/display/favicon.png" />
	<link rel="stylesheet" href="$plat_vars{base_path}css/osm.css" type="text/css" />
	<link type="text/css" href="$plat_vars{jquerycss}" rel="stylesheet" />	
	<script type="text/javascript" src="$plat_vars{jquery}"></script>
	<script type="text/javascript" src="$plat_vars{jqueryui}"></script>
	<script type="text/javascript" src="$plat_vars{openlayers}"></script>
	<script type="text/javascript" src="$plat_vars{base_path}js/osm.js" > </script>
	<script type="text/javascript">
		var newplatform=$newplat;
	</script>
  </head>

endHEAD

open FILE, "<", $plat_vars{'docs_path'}."/osm_index.html" or die "could not read osm_index.html";
my @indx=<FILE>;
close FILE or die "could not close file";
print @indx;


