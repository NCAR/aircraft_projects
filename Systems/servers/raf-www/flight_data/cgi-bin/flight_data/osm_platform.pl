#!/usr/bin/perl -T
#
# COPYRIGHT: University Corporation for Atmospheric Research, 2009-12
#

use strict;
use DBI;
use CGI qw(:all);

our $q; our %plat_vars;
require "./getCookie.pl";

if ($plat_vars{'platform'} eq "acserver") {
	print "<strong>platform list only available on ground</strong>";
	exit;
}

#set up db connection and request
my $dbh = DBI->connect("dbi:Pg:database=platforms;host=eol-rt-data.guest.ucar.edu", "ads")
	or die "Error connecting to db: " . DBI->errstr;
my $sth = $dbh->prepare("SELECT platformid,tailnumber,projectname FROM platform_list ORDER BY platformid")
	or die "Error preparing statement: " . DBI->errstr;

#execute request
$sth->execute()
	or die "Error executing statement: " . DBI->errstr;
my $parray = $sth->fetchall_arrayref()
	or die "Error fetching row : " . DBI->errstr;

#build array of <td>'s with all the platform info, include radio buttons
my @platforms;
for my $p ( @$parray ) {

	#validate input from db TODO: is there a cleaner/quicker way?
	for my $dirty ( @$p ) {
		if ( $dirty !~ /^[-\s\w]*$/ ) {
			print "unclean data from database";
			exit;
		}
	}

	my $r = radio_group(-name=>"platform", -values=>" ".@$p[0], -default=>"n");
	push(@platforms, td([$r,@$p[1 .. $#$p]]));
}

#print form w/ embedded table of available platforms
print start_form(-action=>"osm_index.pl");	
print table(
	Tr(th(["Platform ID", "Tail #", "Projectname"])),
	Tr([@platforms])
);
print "<div class='fr'>\n";
print submit("submit", "Set Platform");
print "</div>\n";
print endform;

