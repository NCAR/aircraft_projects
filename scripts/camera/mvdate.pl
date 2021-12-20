#!/usr/bin/perl
#Version History:
#Version 1.0:
#
#
use strict;
use Time::Local;

print "\n";
#flags and defults
my $ext = "jpg";
my $force = 0;
my @dir;
my @date;
my $verbose = 0;
my $listfiles = 1;

if (@ARGV <= 0) {
	print<<EOF;
	NO COMMAND LINE ARGUMENTS ENTERED
	This script will search through a directory for files containing a date time string of the format YYYYMMDD?hhmmss or YYMMDD?hhmmss where ? is any non whitespace character, or nothing at all
	Usage:	./mvdate.pl SRC_DIR START_DATE STOP_DATE [Options] DEST_DIR
		START_DATE and STOP_DATE *MUST* be of the form YYYYMMDhhmmss
		SRC_DIR MUST BE THE FIRST COMMAND LINE OPTION
		DEST_DIR MUST BE THE LAST COMMAND LINE OPTION

	Options:
		-ext:jpg	Sets file extention
		-v		Verbose (prints file operations)
		-nolist		Does not display list of files to be moved before confirmation, does display # of files to be moved
		-f		Force (Skips confimation and does not display list of dark images)
		-r		Recusive directory search [NOT IMPLEMENTED]
EOF
	die "";	
}
else {
	if (-d $ARGV[0]) { $dir[0] = $ARGV[0]; }
	else { die "INVALID SRC DIRECTORY\n"; }
	$dir[1] = $ARGV[$#ARGV];
	#Process command line arguments
	for (my $i = 1; $i < $#ARGV; $i++)  {
		if ($ARGV[$i] =~ m/-ext:(\S*)/) {$ext = $1;}
		elsif ($ARGV[$i] eq "-v") {$verbose = 1;}	
		elsif ($ARGV[$i] eq "-nolist") { $listfiles = 0; }
		elsif ($ARGV[$i] eq "-f") {$force = 1;}
		elsif ($ARGV[$i] eq "-r") { } #NOT IMPLEMENTED 
		
		elsif ($ARGV[$i] =~ m/\d{6,8}.\d{6}/) { @{$date[$#date+1]} = DateFromString($ARGV[$i]); }

		else {die "INVALID ARGUMENT: $a";}	
	}
	if ($#dir+1 != 2) {die "Missing or invalid SRC_DIR and or DEST_DIR\n";}
	if ($#date+1 != 2) { die "Invalid Start and Stop Date range\n"; }
}

print "Reading directory: $dir[0]\n";
opendir(DIR, "$dir[0]");
our @files = readdir(DIR);
close(DIR);
print "Moving invalid files\n";
#ignore files that dontt end in .$ext and or dont contain a date time string
@files = grep(/.*\d{6,8}.\d{6}.*\.$ext/, @files);
#make sure there are some files left
if ($#files < 0) {print "$dir[0] does not conatin any .*\\d{6,8}.\\d{6}\\.$ext files!\n"; exit(1); }

#Sort files
@files = sort { lc($a) cmp lc($b) } @files;

#@files = sort { lc($a) cmp lc($b) } @files;
print "Moving Date Range: "; PrintDate(@{$date[0]}); print " To "; PrintDate(@{$date[1]}); print "\n";
#Variable declarations
my @filesToMove;

my @filedate;
foreach my $file (@files) {
	@filedate = DateFromString($file);
	#if filedate is after start date
	#PrintDate(@{$date[0]}); print " | "; PrintDate(@filedate); print "|"; print DateDiff(@filedate, @{$date[0]}) . "\n";
 	#PrintDate(@{$date[1]}); print " | "; PrintDate(@filedate); print "|"; print DateDiff(@{$date[1]}, @filedate) . "\n";
	if (DateDiff(@filedate, @{$date[0]}) >= 0 && DateDiff(@{$date[1]}, @filedate) >= 0) { push (@filesToMove, $file); }
}
BatchMove(@filesToMove);

####
##Functions
####

sub PrintDate
{
	print $_[4]+1 . "/$_[3]/$_[5] $_[2]$_[1]$_[0]";
}

sub DateFromString
{
	if ($_[0] =~ m/(\d\d\d?\d?)(\d\d)(\d\d).(\d\d)(\d\d)(\d\d)/) {
		my @date;
		$date[0] = $6;
		$date[1] = $5;
		$date[2] = $4;
		$date[3] = $3;
		$date[4] = $2-1;
		$date[5] = $1;
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

sub IsOlder
{
	#checks if the first inputted date is older than the second inputted date
	if (DateDiff(@_) > 0) {return 1;}
	else {return 0;}
}

sub BatchMove
{
	my $cont = "\n";
	my @files1 = @_;
	if ($force == 0) {
		#print a list of files to be moved
		if ($listfiles) {
			foreach my $file (@files1) {
				print "Move: $file\n";
			}
		}
		print "Total files to move: " . ($#_+1) . " of " . ($#files+1) . "\n";
		
		print "To continue press enter otherwise enter any value:";
		#get user input (this will capture trailing \n)
		$cont = <STDIN>;
	}

	if ($cont eq "\n") {
		unless (-d $dir[1]) {
			print "\nCreating directory: $dir[1]\n";
			mkdir("$dir[1]") or die "Unable to create directory $dir[1]\n $! \n";
		}	
		print "Moving images to temporary directory..\n";
		#move all files identified as dark
		foreach my $file (@files1) {
			if ($verbose) {print "Moving: $dir[0]/$file To $dir[1]/$file\n";}
			rename("$dir[0]/$file","$dir[1]/$file") or die $!; #rename == move
		}
	}
}

