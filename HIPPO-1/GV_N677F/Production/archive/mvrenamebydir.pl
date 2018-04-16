#! /usr/bin/perl
use strict;

#print "Scanning: $ARGV[0]\n";
my @files = <$ARGV[2]/*.jpg>;
my $start = 0;
my $stop = 0;
my $tmp = "";

if ($files[0] =~ /(\d{6}).(\d{6})/) {
	$tmp = $1 . $2;

	$start = $tmp;
	$stop = $tmp;
}

foreach my $file (@files) {
    	if ($file =~ /(\d{6}).(\d{6}).jpg$/) {
		$tmp = $1 . $2;
	    	if ($tmp > $stop) { $stop = $tmp; }
		if ($tmp < $start) { $start = $tmp; }

	}
}

#my $startDate = "20" . substr($start,0, 2) . "-" . substr($start,2,2) . "-" . substr($start,4,2) . " " . substr($start,6,2) . ":" . substr($start, 8, 2) . ":" . substr($start, 10, 2);
#my $stopDate = "20" . substr($stop,0, 2) . "-" . substr($stop,2,2) . "-" . substr($stop,4,2) . " " . substr($stop,6,2) . ":" . substr($stop, 8, 2) . ":" . substr($stop, 10, 2);
my $datestring = "20" . substr($start, 0, 6) . "." . substr($start, 6, 6) . "_" . substr($stop, 6, 6);

my $srcfile = $ARGV[0];
my $destfile = "";
if (lc($srcfile) =~ /(\wf\d\d)/) {
	$destfile = $ARGV[1] . "/" . uc($1) . ".FWD." . $datestring . "Prelim.mov";
}

print "mv $srcfile $destfile\n";

system("mv $srcfile $destfile\n");

#print "Start: $startDate\nStop: $stopDate\n";
