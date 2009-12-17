#!/usr/bin/perl -T

use strict;
use File::Basename;

our $q; our %plat_vars;
require "./getCookie.pl";

# get the name of the file we are looking for
my $href = $q->param('href');
my ($n,$p,$s) = fileparse($href);
my $file = "";

# only get ages for files in the images or GE platform subdirectories
if ( $p =~ /images/ ) {
	$file = $plat_vars{"docs_path"}."/images/$n";
} 
elsif ( $p =~ /GE/ ){
	$file = $plat_vars{"docs_path"}."/GE/$n";
}

# make sure the file exists in its platform directory
if (-e $file) {
	print int((-M $file) * 24 * 60);
} else {
	print "?";
}


