#!/usr/bin/perl -T
#
# COPYRIGHT: University Corporation for Atmospheric Research, 2009-12
#

use strict;
use CGI;
use CGI::Cookie;
our $q = CGI->new;

our %plat_vars; our $header;
my $p_in = $q->param("platform");
$plat_vars{'base_path'}="/flight_data/";

# can we guess your platform?
if ( $q->url(-base=>1) =~ /(localhost)|(acserver)|(hyper)|(hercules)/i 
	or ($p_in =~ /acserver/i) ) {

	#you appear to be on a plane
	$plat_vars{'platform'}="acserver";
	$plat_vars{'openlayers'}="/OpenLayers/OpenLayers.js";
	$plat_vars{'jquery'}="/jQuery/js/jquery-1.5.1.min.js";
	$plat_vars{'jqueryui'}="/jQuery/js/jquery-ui-1.8.13.custom.min.js";
	$plat_vars{'jquerycss'}="/jQuery/css/smoothness/jquery-ui-1.8.13.custom.css";
	$plat_vars{'docs_path'}="../../html/flight_data/";
	$plat_vars{'href_path'}=$plat_vars{'base_path'};
	$plat_vars{'dbname'}="real-time";
	$plat_vars{'dbhost'}="acserver.raf.ucar.edu";
}
else {
	#you appear to not be on a plane

	#check for platform:
	if ($p_in ne '') {
	        #strip whitespace
        	$p_in =~ s/^\s+//;
	        $p_in =~ s/\s+&//;

        	# validate this platfrom exists
	        if (&getCookie($p_in)) {
			$plat_vars{'platform'}= $p_in;
	        } else {
                	#invalid platform - choose another (unless called from platform.pl)
			if ( $q->url() !~ /platform\.pl/i ){
				print $q->redirect('platform.pl');
				exit;
			}
	        }
	} else {
		my $platform_cookie=&getCookie();
		if (! $platform_cookie) {
			#no platform - choose one (unless we were called from platform.pl)
			if ( $q->url() !~ /platform\.pl/i ){
				print $q->redirect('platform.pl');
				exit;
			}
			$plat_vars{'platform'} = "none";
		} else {
			$plat_vars{'platform'} = $platform_cookie;
		}
	}
	$plat_vars{'openlayers'}="http://openlayers.org/api/2.12/OpenLayers.js";
	$plat_vars{'jquery'}="http://ajax.googleapis.com/ajax/libs/jquery/1.5.1/jquery.min.js";
	$plat_vars{'jqueryui'}="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.13/jquery-ui.min.js";
	$plat_vars{'jquerycss'}="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.13/themes/black-tie/jquery-ui.css";
	$plat_vars{'href_path'}=$plat_vars{'base_path'}.$plat_vars{'platform'}."/";
	$plat_vars{'docs_path'}="../../docs/flight_data/".$plat_vars{'platform'}."/";
	$plat_vars{'dbname'}="real-time-".$plat_vars{'platform'};
	$plat_vars{'dbhost'}="eol-rt-data.fl-ext.ucar.edu";
}

if ($header ne "") {
	print $q->header($header)
} else {
	my $c = new CGI::Cookie(-name=>'platform', -value=>$plat_vars{'platform'}, -expires=>"+24h");
    print $q->header(-cookie=>$c);
}

sub getCookie
{
	use DBI;
	use CGI::Cookie;

	my $pltfrm;
	my ($input) = @_;

	if ( $input ) {
		$pltfrm=$input;
	} else {
		my %cookies = fetch CGI::Cookie;
		if (! exists $cookies{"platform"} ) {
			return 0;
		}
		$pltfrm=$cookies{"platform"}->value;
	}
	
	#set up db connection and request
	my $dbh = DBI->connect("dbi:Pg:database=platforms;host=eol-rt-data.fl-ext.ucar.edu", "ads")
		or die "Error connecting to db: " . DBI->errstr;
	my $sth = $dbh->prepare("SELECT status FROM platform_list WHERE platformid = ?")
		or die "Error preparing statement: " . DBI->errstr;
	
	#execute request
	$sth->execute($pltfrm)
		or die "Error executing statement: " . DBI->errstr;
	
	my @ary = $sth->fetchrow_array;
		
	if ((scalar @ary) < 1) {
		# invalid cookie, does not exist in database
		return 0;
	} else {
		$pltfrm =~ /^([-\w\s]+)$/;
		return $1;
	}
}
1;
