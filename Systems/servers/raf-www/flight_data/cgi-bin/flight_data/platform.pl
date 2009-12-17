#!/usr/bin/perl -T

use strict;
use DBI;
use CGI qw(:all);

our $q; our %plat_vars;
require "./getCookie.pl";

if ($plat_vars{'platform'} eq "acserver") {
	print "<meta http-equiv=\"REFRESH\" content=\"2;url=/cgi-bin/flight_data/osm_index.pl\">";
	print "<strong>platform list only available on ground</strong><br>(you will be sent back to the display page in 2 seconds)";
	exit;
}

#set up db connection and request
my $dbh = DBI->connect("dbi:Pg:database=platforms;host=eol-rt-data.guest.ucar.edu", "ads")
	or die "Error connecting to db: " . DBI->errstr;
my $sth = $dbh->prepare("SELECT platformid,tailnumber,flightnumber,projectname,status FROM platform_list ORDER BY platformid")
	or die "Error preparing statement: " . DBI->errstr;

#execute request
$sth->execute()
	or die "Error executing statement: " . DBI->errstr;
my $parray = $sth->fetchall_arrayref()
	or die "Error fetching row : " . DBI->errstr;

#Include jquery libs
&printjs();

#print out stylesheet
&printcss();

#print out platform chooser box
print "<div class='mainbox'>\n";
print h2("Platform Chooser<hr>\n");

print b(p("Current Platform: ".em( (("" ne $plat_vars{'platform'})?"$plat_vars{'platform'}":"none") )."\n"));
print p("Please choose a new one below");

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
	Tr(th(["Platform ID", "Tail #", "Flight #", "Projectname", "Status"])),
	Tr([@platforms])
);
print "<div class='right'>\n";
print submit("submit", "Set Platform");
print "</div>\n";
print endform;

print "</div>";

sub printcss {

print <<endCSS;
<style type="text/css">
	body {
		padding: 0px;
	}
	h2 {
		margin: 0px;
		padding: 0px;
		text-align:center;
	}
	div.mainbox {
		width:800px;
		padding:15px; 
		margin:15px; 
		background-color:#F0F0F0; 
		border: 1px dotted #808080; 
		font-size:1.1em; 
		margin:0 auto 0 auto;
	}
	div.right{
		float: right;
	}
	table {
		margin-bottom: 15px;
		width: 100%;
		border-collapse: collapse;
	}
	table th {
		text-align: left;
		background: #E5F9FF;
		font-size: 14px;
		border-bottom: 2px solid #AAA;
	}
	table td {
		background: #FFF;
		border-bottom: 1px solid #AAA;
		border-left: 1px dotted #AAA;
	}
</style>
</head>
endCSS
}

sub printjs {

print <<endJS;
<head>
<script type="text/javascript" src="$plat_vars{jquery}"></script>
<script type="text/javascript">
	\$(function(){
		\$("tr:gt(0)").click(function(){
			\$("tr:gt(0)").children().css("background-color", "#FFF")
				.css("color", "#000");
			\$(this).children().css("background-color", "#F39814")
				.css("color", "#FFF");
			\$(this).find("input").attr("checked", true);
		});
		\$("tr:gt(0)").dblclick(function(){
			\$(":submit:first").trigger("click");
		});
	});
</script>
endJS
}
