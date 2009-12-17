#!/usr/bin/perl -T

use strict;
use XML::DOM;
use Image::Magick;
use File::Basename;

our $q; our %plat_vars;
require "./getCookie.pl";

# Setup XML parser on $kmlfile
my $kmlFile = $plat_vars{'docs_path'}."/GE/osm.kml";
my $parser = new XML::DOM::Parser;
my $kml = $parser->parsefile($kmlFile);

# Parse KML file and output data needed for OpenLayers in JSON format
print '{"images":[';
&printImageData();

print '],"vectors":[';
&printKMLData();

print "]}\n";

$kml->dispose;

# end

sub printImageData {
# prints out GroundOverlay KML info as JSON object
	my $parent = "GroundOverlay";

	my $nodes = $kml->getElementsByTagName($parent);
	my $n = $nodes->getLength;
	my $img = new Image::Magick;
	my $validCount = 0;

	for (my $i = 0; $i < $n; $i++)
	{

		my %hash = ();
	    my $node = $nodes->item ($i);
		my $href = &getValueOfNode($node, "href");	
		if ($href =~ /^http/) {
			$hash{'href'} = $href;
		} else {
			$hash{'href'} = $plat_vars{'href_path'}."images/".basename($href);
		}

	#	if ( -e $hash{'href'}) { #does not work w/ web ref i.e. http://weather.com/latest.jpg
			if ($validCount > 0) { print "," }
			print "{";
	
			$img->Read($hash{'href'});
			$hash{'pxW'} = $img->Get('width');
			$hash{'pxH'} = $img->Get('height');
			$hash{'name'} = &getValueOfNode($node, 'name');
			$hash{'refresh'} = &getValueOfNode($node, 'refreshInterval');
			$hash{'n'} = &getValueOfNode($node, 'north');
			$hash{'s'} = &getValueOfNode($node, 'south');
			$hash{'e'} = &getValueOfNode($node, 'east');
			$hash{'w'} = &getValueOfNode($node, 'west');
			$hash{'cleanHref'} = basename($hash{"href"});	

			&parse_RAP_filename($hash{'cleanHref'}, \%hash);
		
			my $len = scalar keys( %hash );
			my $j = 0;
	
			while ( my ($key, $value) = each(%hash) ) {
				$value =~ s/\//\\\//g;
				print "\"$key\":\"$value\"";
				$j++;		
				if ($j < $len) { print ", " }
			}
			print "}";
			$validCount++;
	#	}
	}
}

sub printKMLData {
# prints out NetworkLink KML info as JSON object
	my $parent = "NetworkLink";

	my $nodes = $kml->getElementsByTagName($parent);
	my $n = $nodes->getLength;
	my $validCount = 0;

	for (my $i = 0; $i < $n; $i++)
	{
		my %hash = ();
	    my $node = $nodes->item ($i);
		my $href = &getValueOfNode($node, "href");	

		if ($href =~ /^http/) {
			$hash{'cleanHref'} = $href;
		} else {
			$hash{'cleanHref'} = $plat_vars{'href_path'}."GE/".basename($href);
		}

		#if ( -e $hash{'cleanHref'}) { #does not work w/ web ref i.e. http://weather.com/latest.jpg
			if ($validCount > 0) { print "," }
			print "{";
	
			$hash{'name'} = &getValueOfNode($node, 'name');
			$hash{'refresh'} = &getValueOfNode($node, 'refreshInterval');
			$hash{'age'} = int((-M "../../html".$hash{'cleanHref'}) * 24 * 60);
		
			if ($hash{'cleanHref'} =~ /kmz$/i) {
				$hash{'href'} = "/cgi-bin/flight_data/osm_kmz2kml.pl?kmz=" . $hash{'cleanHref'};  
			} else {
				$hash{'href'} = $hash{'cleanHref'};  
			}
	
			my $j = 0;
	
			while ( my ($key, $value) = each(%hash) ) {
				if ($j > 0) { print ", " }
				$value =~ s/\//\\\//g;
				print "\"$key\":\"$value\"";
				$j++;		
			}
			print "}";
			$validCount++;
		#}
	}
}

sub getValueOfNode {
	my ($node, $nameOfNode) = @_;
	return $node->getElementsByTagName($nameOfNode, 1)->item(0)->getFirstChild->getNodeValue
		or return undef;
}

sub parse_RAP_filename {
	use Time::Local;
	use DateTime;

	my ($fn, $hashref) = @_;

	if ( $fn =~ /^([\w-]+)\.([\w-]+)\.(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})\.([\w-]+)\.(jpg|gif|png)$/i )
	{
		$hashref->{'fnparse'} = 1; 

		$hashref->{"category"} = $1;
		$hashref->{"platform"} = $2;
		$hashref->{"type"} = $8;
	
		$hashref->{'year'} = $3;
		$hashref->{'month'} = $4;
		$hashref->{'day'} = $5;
		$hashref->{'hour'} = $6;
		$hashref->{'minute'} = $7;

		#get age in minutes - subtract epochs (seconds), then divide by 60 to get minutes
		$hashref->{'age'} = int((1/60) * (DateTime->now()->epoch() - (
			DateTime->new(
				minute => $hashref->{'minute'},
				hour => $hashref->{'hour'},
				day => $hashref->{'day'},
				month => $hashref->{'month'},
				year => $hashref->{'year'}
			)->epoch()) ));


	} else {
		$hashref->{'fnparse'} = 0; 
		my $age = int((-M $plat_vars{'docs_path'}."images/$fn") * 24 * 60);
		$hashref->{'age'} = (-e $plat_vars{'docs_path'}."images/$fn") ? $age : "?";
	}
	return;
}
