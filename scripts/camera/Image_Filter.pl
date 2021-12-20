#!/usr/bin/perl
#Change Log:
#Version 1.0
# Parse Image magic identify -verbose output to determine darkness of image.
#Version 1.1
# Bug fixes
# Added ground image checking via flt_time script using netCDF files.
# Added a check for continuity
#Version 1.3
# Fixed forgotten month of september in flt_time parsing (flts after august would not have gnd images removed before)
# Date time caparisons are now done using Time::Local (Add support for time compariton over years/months)
# No longer propmts the user for EVERY discontinuity in time, (instead it lists them all at once and asks the user)
#Version 1.4
# If netCDF file does not exist in Prod_Data, look in /scr/raf/local_data. JAA 8/24/2011
#Version 1.5
# Change fixed directories to use RAF env variables.  $DATA_DIR & $RAW_DATA_DIR.

#ToDo:
# Get netCDF info from FULL dirname (easiest to just convert a valid diretory to its full name at start of script)
# Add command line option to set netCDF file
# Fix commandline option for changing avg pixel/std dev thresholds
# Use sqrt(.241R^2 + .691G^2 + .068B^2) to calculate brightness of image
# threshold brightness of images and avg std dev
use strict;
use Time::Local;
use File::Path qw(mkpath);
use Cwd 'abs_path';

print "\n";
#flags and defults
our $ext = "jpg";
our $pattern = '(\d\d)(\d\d)(\d\d)[\_|-](\d\d)(\d\d)(\d\d)\.'.$ext;
our $speedhack = 0;
our $verbose = 0;
our $force = 0;
our $dir = "";
our $checkCont = 1;
our $checkDark = 1;
our $checkGnd = 1;
our $move;
#Ajusting these values will change what images the script removes (higher values = more bright)
our @threshold;
our $listfiles = 1;
$threshold[0][0] = 50; #R if Mean is low image is dark #dusk colors..
$threshold[1][0] = 50; #G if Mean is low image is dark #green is bright!
$threshold[2][0] = 50; #B if Mean is low image is dark #night is blue.. grr
$threshold[0][1] = 18; #R if Standard Deviation is low image is mostly one color
$threshold[1][1] = 15; #G if Standard Deviation is low image is mostly one color
$threshold[2][1] = 18; #B if Standard Deviation is low image is mostly one color
our $project = -1;
our $flight = -1;
our $expectedDiff = 10; #Actually 1, but any gap less than 10 seconds I dont care about
our $speedstart = 25;
our $speedstop = 80;

if (@ARGV <= 0) {
	print<<EOF;
	NO COMMAND LINE ARGUMENTS ENTERED
	This script will search through an image directory and removes very dark images using imagemagick also removes images taken on the ground using flt_time script (Installed on Merlot).
	Usage:	./Image_Filter.pl [OPTIONS] TARGET_DIR

	Options:
		-pattern:"regex"Sets the regex to pull date/time from filename for continuity checking and ground
				image checking.  Default is for aircraft camera images, i.e. yymmdd[-_]hhmmss.jpg
					'(\d\d)(\d\d)(\d\d)[\_|-](\d\d)(\d\d)(\d\d)\.'.$ext
				If don't need continuity/gnd check, set -skipcont -skipgnd -pattern:"none"
		-ext:jpg	Sets file extention (Default: jpg)
		-maxmean:R|G|B	Sets maximum average pixel value (per color)
				(Default:35|35|55) {Range: 0-255}
		-maxdev:R|G|B	Sets maximum pixel value standard deviation (per color)
				(Default:15|15|15) {Range: 0-255}
		-t:##		Time in seconds between image files
				(Default:1) {Used to check consistency}
		-proj:PLOWS	Sets project (Not needed if TARGET_DIR if of form
				*/Raw_Data/<Project>/*/flight_number_<flightno>/* )
		-fltno:ff01	Sets flight number (Not needed if TARGET_DIR if of form
				*/Raw_Data/<Project>/*/flight_number_<flightno>/* )
		-skipcont	Skips continuity check
		-skipdark	Skips dark image check/removal and removed only ground images
				(based on flt_time script)
		-skipgnd	Skips ground image check/removal
		-v		Verbose (prints file operations)
		-nolist		Does not display list of files to be removed before confirmation,
				does display # of files to be removed
		-f		Force (Skips confimation and does not display list of dark images)
		-r		PERMANATLY REMOVE (normally dark images are moded to
				target_DIR/removed/) [NOT YET IMPLEMENTED]
		-Y		Don't prompt before moving the images
		-tdir:removed	Sets name of subdir that dark images are moved to
				(Default: removed) [NOT YET IMPLEMENTED]
		-s:##		File skipping, Checks every ## files and assumes the images
				inbetween based on the images checked (Default: 0) {Range: 0-inf}
		-s%:##		Sets file skipping to a percentage of total files
				{Range: 0-100} [NOT YET IMPLEMENTED]
		-sstart:##	Sets threshold speed for flt_time to be checked first (Default: 25)
		-sstop:##	Sets threshold speed for flt_time to be checked last (Default: 80)
EOF
	die "";	
}
else {
	#Process command line arguments
	foreach my $a (@ARGV) {
	        #print $a . "\n";
	    	if ($a =~ m/-ext:(\S*)/) {$ext = $1;}
		#elsif ($a =~ m/-maxmean:(\d+)\|(\d+)\|(\d+)/) { $threshold[0][0] = $1; $threshold[0][1] = $2 ; $threshold[0][2] = $3 }
		#elsif ($a =~ m/-maxdev:(\d+)\|(\d+)\|(\d+)/) { $threshold[1][0] = $1; $threshold[1][1] = $2 ; $threshold[0][3] = $3 }
		elsif ($a =~ m/-maxmean:(\d+)\|(\d+)\|(\d+)/) { $threshold[0][0] = $1; $threshold[1][0] = $2 ; $threshold[2][0] = $3 }
		elsif ($a =~ m/-maxdev:(\d+)\|(\d+)\|(\d+)/) { $threshold[0][1] = $1; $threshold[1][1] = $2 ; $threshold[2][1] = $3 }
		elsif ($a =~ m/-pattern:(.*)/) {$pattern = $1; }
		elsif ($a =~ m/-t:(\d+)/) { $expectedDiff = $1; }
		elsif ($a =~ m/-proj:(.*)/) { $project = $1; }
		elsif ($a =~ m/-fltno:(.*)/) { $flight = $1; }
		elsif ($a eq "-skipcont") { $checkCont = 0;}
		elsif ($a eq "-skipdark") { $checkDark = 0;} 
		elsif ($a eq "-skipgnd") { $checkGnd = 0;}
		elsif ($a eq "-v") {$verbose = 1;}	
		elsif ($a eq "-nolist") { $listfiles = 0; }
		elsif ($a eq "-f") {$force = 1;}
		elsif ($a eq "-r") { } #NOT IMPLEMENTED 
		elsif ($a eq "-Y") {$move = "\n";}
		elsif ($a =~ m/-tdir:(.*)/) {} #NOT IMPLEMENTED
		elsif ($a =~ m/-s:(\d+)/) {$speedhack = $1; print "SpeedHack set\n";}
		elsif ($a =~ m/-s%:(\d+)/) {} #NOT IMPLEMENTED
		elsif ($a =~ m/-sstart:(\d+)/) { $speedstart = $1; }
		elsif ($a =~ m/-sstop:(\d+)/) { $speedstop = $1; }
		
		#elsif (-d $a) {$dir = abs_path($a); } #target dir
		elsif (-d $a) {$dir = $a; } #target dir
		elsif ($a eq "" || $a eq "\n") {} #For capturing stangeness
		else {die "INVALID ARGUMENT: $a";}	
	}
	if ($dir eq "") {die "NO DIRECTORY ENTERED: $dir";}
	# If there is no time info, then must skip continuity and ground check. Just do dark check.
	if ($pattern =~ m/none/) {
	    $checkGnd = 0;
	    $checkCont = 0;
	}
}

print "Reading directory: $dir\n";
opendir(DIR, "$dir");
our @files = readdir(DIR);
close(DIR);
print "Removing invalid files\n";
#ignore files that don end in .$ext
@files = grep(/.*\.$ext/, @files);
#make sure there are some files left
if ($#files < 0) {print "$dir does not conatin any *.$ext files!\n"; exit(1); }
#Sort files, this allows the script to skip files and accuratly assume what the files skipped contain
if ($speedhack || $checkGnd || $checkCont) { print "Sorting Files\n"; @files = sort { lc($a) cmp lc($b) } @files; }

#Variable declarations
my @filesToRemove;

if ($checkCont) {
	my $diff = 0;
	my @gap;
	for (my $i = 1; $i <= $#files; $i++) {
		my $p = -1;
		if (int($i/($#files+1)*100) - $p > 0) { print "Scanning for discontinuity: " . int($i/($#files+1)*100) . "% Done\r"; $p++; }
		if ($files[$i] ne "" && $files[$i-1] ne "") {
			$diff = DateDiff(DateFromFile($files[$i]), DateFromFile($files[$i-1]));
			if (($diff > $expectedDiff && $diff > 0) || $diff < 0) {
				#print "\nDate discontinuity between $files[$i] and $files[$i-1] | $diff seconds\n";
				#print "To ignore press enter, otherwise input anyvalue:";
				#my $cont = <STDIN>;
				#if ($cont ne "\n") { die "Inconsistent data!\n"; }
				$gap[$#gap+1][0] = $files[$i-1];
				$gap[$#gap][1] = $files[$i]; #after the previous line a new element is created so the +1 is not needed
				$gap[$#gap][2] = $diff;
			}
			elsif ($diff == 0) {
				print "\nUnable to detect time difference between:\n     $files[$i-1]\n     $files[$i]\n";
				print "To ignore press enter, otherwise input anyvalue:";
				my $cont = <STDIN>;
				if ($cont ne "\n") { die "Inconsistent data!\n"; }
			}
		}
	}
	print "Scanning for discontinuity: 100% Done\n"; 
	if ($#gap > 0) {
		for ($a = 0; $a <= $#gap; $a++) {
			print "Time Gap: $gap[$a][0] -> $gap[$a][1] | $gap[$a][2]\n";
		}
		print "To ignore press enter, otherwise input any value:";
		my $cont = <STDIN>;
		if ($cont ne "\n") { print "Canceled by user\n"; exit(1); }
	}
}
else
{
	print "Scanning for discontinuity: SKIPPED\n"; 
}
print "\n";
our @date;
#date store in @date as MM,DD,YYYY,hh,mm,ss
if ($checkGnd) {
	#variable declaration for Gnd checking
	#my @date;
	my $speed = $speedstart;
	my $count = 0;
	#if project was not given try to get it out of the directory path
	if ($project == -1) {
		$dir =~ m/\/Raw_Data\/(.*?)\//;
		$project = $1;
		if ($project eq "") { print "Unable to find project name, Gnd check may be skipped\n";}
	}
	#if flight number was not given try to get it out of the directory path
	if ($flight == -1) {
		$dir =~ m/(?:f|F)light_number_(\S\S\d\d)/;
		$flight = $1;
		if ($flight eq "") { print "Unable to find flight number, Gnd check may be skipped\n"; }
	}
	#location of netCDF file
	my $netCDF = "/scr/raf/Prod_Data/$project/$project$flight.nc";
	# Final production data will be in Prod_Data. However, if the production files have not
	# yet been generated, use the field-phase files. We are only accessing the aircraft
	# speed to determine if the camera is operating on the ground and strip ground images.
	# This should not change enough from field- to production- files to make a difference.
	# This if statement allows us to create preliminary movies before the final .nc files
	# exist. - JAA 8/24/2011
	unless (-e $netCDF) {
	    open(DATA, 'echo $DATA_DIR |');
	    while (<DATA>) {
		chomp;
	        $netCDF = "$_/$project$flight.nc";
	    }
	    close(DATA);
	    if (-e $netCDF) {
	        print "Use data file ".$netCDF."\n";
	    }
	}

	# We are inconsistent. Sometimes field files are in $DATA_DIR. Sometimes they are in
	# $DATA_DIR/$project.
	unless (-e $netCDF) {
	    open(DATA, 'echo $DATA_DIR |');
	    while (<DATA>) {
		chomp;
	        $netCDF = "$_/$project/$project$flight.nc";
	    }
	    close(DATA);
	    print "Use data file ".$netCDF."\n";
	}
	
	if (-e $netCDF) { #if the netCDF file is found
		#the flt_time script is kinda basic.. it will not specify whether it found
		#an increase or decrase in speed that breached its threshold.  Also it will
		#report only 1 time if it only finds one crossing so we need to ajust the
		#speed it uses as a threshold untill it gives us some data that makes some sense
		while ($#date+1 != 2 && $speed <= $speedstop ) { 
			@date = ();
			#run flt_time scrpt and pipe the output into perl
			open(DATA, "flt_time -t $speed $netCDF|");	
			#get takeoff and landing time from flt_time output
			$count = 0;
			while(<DATA>) {
				#while flt_time is outputting
				if ($_ =~ m/\s*\w\w\w (\w\w\w\w?)\s*(\d?\d) (\d\d)\:(\d\d)\:(\d\d) (\d\d\d\d)\s*/) {
					$date[$count][4] = MonthToNum($1); #month
					$date[$count][3] = $2;#day
					$date[$count][2] = $3;#hour
					$date[$count][1] = $4;#min
					$date[$count][0] = $5;#sec
					$date[$count][5] = $6;#year
					if ($date[$count][5] < 100) { $date[$count][5] += 2000; }
					
					$count++;
				}
			}
			close(DATA);
			
			#Sometimes the flt_time script returns dates that are mere seconds
			#apart probably to so skipping on takeoff/landing If the takeoff
			#and landing times are less than 10 min apart they are not useful,
			#empty @date so the while loop continues
			if ($#date+1 == 2 && DateDiff(@{$date[1]}, @{$date[0]}) < (10*60)) { @date = (); }
			
			$speed++;
			
		}
		
		if ($#date+1 == 2) { 
			#unfortunately flt_time only outputs one date/time and does not specify
			#if it is a start or end time so we have to check it if only put out 2,
			#a start and stop also this will filter out multiple flights in one netcdf file
			
			#print out takeoff | first file date and landing | last file date
			print PrintDate(@{$date[0]}); print " | "; PrintDate(DateFromFile($files[0])); print "\n";
			print PrintDate(@{$date[1]}); print " | "; PrintDate(DateFromFile($files[$#files])); print "\n";
			
			#Quick sanity check
			if (IsOlder(DateFromFile($files[$#files]), DateFromFile($files[0]))) {
				#earliest file should be earler than landing time
				if (IsOlder(DateFromFile($files[0]),@{$date[1]})) { 
					print "Earlist file is older than landing time! (";
					PrintDate(DateFromFile($files[0])); print " | ";
					PrintDate(@{$date[1]}); print ")\n";
					print "Scanning for ground images: SKIPPED (Bad Takeoff/LandingTime)\n"; 
					$checkGnd = 0;
				}
				#oldest file should be older than takeoff time
				if (IsOlder(@{$date[0]}, DateFromFile($files[$#files]))) {
					print "Oldest file is earlier than takeoff time! (";
					PrintDate(@{$date[0]}); print " | ";
					PrintDate(DateFromFile($files[$#files])); print ")\n";
					print "Scanning for ground images: SKIPPED (Bad Takeoff/LandingTime)\n"; 
					$checkGnd = 0;
				}
			}
			else
			{
				print "Files sorted into reverse order?!\n";
			}
			if ($checkGnd) {
				#now check each file to see if it is newer than takeoff or older than landing
				for (my $i = 0; $i <= $#files; $i++) {
					my $p = -1;
					if (int($i/$#files*100) - $p) { print "Scanning for ground images: " . int($i/$#files*100) . "% Done\r"; $p++ }
					#if file time is older than landing time remove it
					if (IsOlder(DateFromFile($files[$i]),@{$date[1]})) { push(@filesToRemove, $i);} 
					#if file time is earlier than takeoff time remove it
					if (IsOlder(@{$date[0]},DateFromFile($files[$i]))) { push(@filesToRemove, $i);}
				}
				print "Scanning for ground images: 100% Done";
				
				if ($#filesToRemove+1 > 0) {print " (Ground Images Found)\n"; Remove("removed/ground",@filesToRemove); @filesToRemove = ();}
				else { print " (No ground Images found)\n"; }
			}
		}
		else
		{
			print "Scanning for ground images: SKIPPED (Missing takeoff or landing time)\n"; 
		}
	}	
	else {
		print "Could not find netCDF file, skipping ground image removal.\n";
		print "Scanning for ground images: SKIPPED\n"; 	
	}
}
else { print "Scanning for ground images: SKIPPED\n"; } 
print "\n";
#print $#files+1 . "\n";
#print $speedhack . "\n";
if ($checkDark) {
	#dark checking variable declarations
	my $speeddark = 0; #this will be set to 1 if a dark file is encountered
	my @speedHist; #list of files skipped in the last iteration
	my @filesToRemove; #list of files idetified as dark

	for (my $i = 0; $i <= $#files; $i++) {
		my $p = -1;
		if (int($i/$#files*100) - $p) { print "Scanning for dark images: " . int($i/($#files+1)*100) . "% Done\r"; $p++ }
		#skip files with the wrong ext Shoulden't be nessesary but just in case
		if ($files[$i] =~ m/.*\.$ext/) {
			#always true if $speedhack is 0, other wise skips $speedhack # of files and checks the very last file
			if ($speedhack == 0 || $i % $speedhack == 0 || $i == $#files) {
				#if image is dark store its name and deal with it later
				if (IsDark($files[$i])) {
					#$file is dark
					push (@filesToRemove, $i);
					$speeddark = 1;
					if ($speeddark && $speedhack) {
						#if image was dark and last image was dark all images inbetween should be dark
						foreach my $f (@speedHist) { push(@filesToRemove, $f); }
					}
					elsif ($speedhack) {
						#if speed hack is enabled skipped files need to be checked
						foreach my $f (@speedHist) {
							if (IsDark($files[$f])) { push(@filesToRemove, $f); }
						}
					}
				}
				elsif ($speeddark && $speedhack) {
					#if image was bright and last image was dark
					#check skipped images
					foreach my $f (@speedHist) {
						if (IsDark($files[$f])) { push(@filesToRemove, $f); }
					}
					$speeddark = 0; #this image was light
				}
				#clear file history
				@speedHist = ();
			}
			else {
				#add file to list of files skipped during this iteration
				push(@speedHist, $i);
			}
		}
	}
	print "Scanning for dark images: 100% done";
	if ($#filesToRemove+1 > 0) {
		print " (Dark images found)\n";
		Remove("removed", @filesToRemove);
		@filesToRemove = ();
	}
	else {print " (No Dark images found)\n";}
}
else { print "Scanning for dark images: SKIPPED\n"; }



####
##Functions
####

sub PrintDate
{
	print $_[4]+1 . "/$_[3]/$_[5] $_[2]$_[1]$_[0]";
}

sub DateFromFile
{
	# nono must always be accompanied by -skipgnd and -skipcont
	if ($_[0] =~ m/none/) {
	    	return;
	}
	if ($_[0] =~ m/$pattern/) {
		my @date;
		$date[0] = $6; #sec
		$date[1] = $5; #min
		$date[2] = $4; #hr
		$date[3] = $3; #day
		$date[4] = $2-1; #mon
		$date[5] = $1; #yr
		if ($date[5] < 100) { $date[5] += 2000; }
			
		return @date;
	}
}

sub DateDiff
{
	my @date1 = @_[0..5];
	my @date2 = @_[6..11];
	my $diff = 0; #in seconds
	if ($date1[5] < 100) {$date1[5] += 2000; }
	if ($date2[5] < 100) {$date2[5] += 2000; }
	
	my $time1 = timelocal(@date1);
	my $time2 = timelocal(@date2);

	return ($time1-$time2);
}

sub MonthToNum
{
	my @months = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec");
	for (my $i = 0; $i < 12; $i++)
	{
		if ($_[0] eq $months[$i]) { return $i; }
	}
	die "Invalid month: $_[0]\n";
}

sub IsOlder
{
	#checks if the first inputted date is older than the second inputted date
	my @date1 = @_[0..5];
	my @date2 = @_[6..11];
	#expand year if need be
	if ($date1[5] < 100) { $date1[5] += 2000; }
	if ($date2[5] < 100) { $date2[5] += 2000; }
	
	if (DateDiff(@_) > 0) {return 1;}
	else {return 0;}
}
sub Remove
{
	my $cont = "\n";
	my $subdir = shift;
	my @indexes = @_;
	if ($force == 0) {
		#print a list of files to be removed
		#if ($listfiles) {
		#	foreach my $i (@indexes) {
		#		print "Remove: $files[$i]\n";
		#	}
		#}
		print "Total files to remove: " . ($#_+1) . " of " . ($#files+1) . "\n";
		
		#print "Takeoff: "; PrintDate(@{$date[0]}); print " | "; PrintDate(DateFromFile($files[0])); print "\n";
		#print "Landing: "; PrintDate(@{$date[1]}); print " | "; PrintDate(DateFromFile($files[$#files])); print "\n";
		
		if (!($move)) {

			print "To continue press enter otherwise enter any value:";
			#get user input (this will capture trailing \n)
			$cont = <STDIN>;
		}
	}

	if ($cont eq "\n") {
		print "\r\r";
		unless (-d "$dir/$subdir") {print "\nMaking dir $dir/$subdir\n"; mkpath("$dir/$subdir") || die "Failed: mkdir -p $dir/$subdir";}	
		print "Moving images to $dir/$subdir\n";
		#remove all files identified as dark
		foreach my $i (@indexes) {
			if ($verbose) {print "Moving: $dir/$files[$i] To $dir/$subdir/$files[$i]\n";}
			rename("$dir/$files[$i]","$dir/$subdir/$files[$i]") or die "Failed: mv $dir/$files[$i] $dir/$subdir/$files[$i]\n     $!"; #rename == move
			$files[$i] = "REMOVE ME";
		}
		@files = grep(/.*\.$ext/, @files);
	}
}
sub IsDark
{
	my @colordata;
	$colordata[0][0] = -1;
	$colordata[0][1] = -1;
	my $colorindex = -1;
	my $file = @_[0];
	#use imagemagick to get picture information, piped into DATA
	open(DATA, "identify -verbose  \"$dir/$file\"|");
	#Extract mean and skewness from output 
	while (<DATA>) {
		#use regexpressions to get data. In newer versions of imagemagick there is no capitalization..
		#(?: ) is a non capturing group vs. ( ) which captures and is stored in $1 $2 etc.
		#\s* is any amount of whitespace, used lberally to prevent updates from breaking the script
		if ($_ =~ m/\s*(?:R|r)ed:\s*/) {
			$colorindex = 0;
		}
		elsif ($_ =~ m/\s*(?:G|g)reen:\s*/) {
			$colorindex = 1;
		}
		elsif ($_ =~ m/\s*(?:B|b)lue:\s*/) {
			$colorindex = 2
		}
		elsif ($_ =~ m/\s*(?:G|g)ray:\s*/) { #Apparently if an image is black enough it is converted to gray scale...
			$colorindex = 3
		}
		elsif ($_ =~ m/\s*(?:M|m)ean:\s*(\d*\.?\d*)\s*(\s*\(\d*\.\d*\))?\s*/) {
			if ($colorindex == 3){
				$colordata[0][0] = $1;
				$colordata[1][0] = $1;
				$colordata[2][0] = $1;
			}
			else{ $colordata[$colorindex][0] = $1; }
		}
		elsif ($_ =~ m/\s*(?:S|s)tandard (?:D|d)eviation:\s*(\d*\.?\d*)\s*(\s*\(\d*\.\d*\))?\s*/) {
			if ($colorindex == 3){
				$colordata[0][1] = $1;
				$colordata[1][1] = $1;
				$colordata[2][1] = $1;
			}
			else{ $colordata[$colorindex][1] = $1; }
		}
		#elsif ($_ =~ m/Resolution/) { last; }
	}	
	close DATA;
	
	if ($colordata[0][0] == -1 || $colordata[0][1] == -1 || $colorindex == -1) {
		die "\nImageMagick Parsing Failure: $file\n$colordata[0][0]|$colordata[0][1]|$colorindex";
	}

	my $dark = 1; #dark unless otherwise proven by jury trial
	for (my $i = 0; $i < 3; $i++) {
	        #print "$colordata[$i][0] | $colordata[$i][1]\n";
		#if mean or standard deviation is above threshold image is not dark
		#if ($i == 2) { 
		#    print "$i:0 $colordata[$i][0] | $threshold[$i][0]\n";
		#    print "$i:1 $colordata[$i][1] | $threshold[$i][1]\n";
		#}
		#my $stop = <STDIN>;
		if ($colordata[$i][0] > $threshold[$i][0]) {
			$dark = 0;
			#print "$i: $dark\n";
			last;
		}
		elsif ($colordata[$i][1] > $threshold[$i][1]) {
			$dark = 0;
			#print "$i: $dark\n";
			last;
		}  
	}
	#if ($dark) { print "DARK \n"; }
	#print "---\n";
	return $dark;

}
