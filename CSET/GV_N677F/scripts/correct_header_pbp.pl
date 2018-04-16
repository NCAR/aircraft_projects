#!/usr/bin/perl

# Hash to relate filename to flight number
$flight{'CSET-HOLODEC-PBP_GV_20150707_R0.csv'} = 'RF02';
$flight{'CSET-HOLODEC-PBP_GV_20150709_R0.csv'} = 'RF03';
$flight{'CSET-HOLODEC-PBP_GV_20150712_R0.csv'} = 'RF04';
$flight{'CSET-HOLODEC-PBP_GV_20150714_R0.csv'} = 'RF05';
$flight{'CSET-HOLODEC-PBP_GV_20150719_R0.csv'} = 'RF07';
$flight{'CSET-HOLODEC-PBP_GV_20150722_R0.csv'} = 'RF08';
$flight{'CSET-HOLODEC-PBP_GV_20150724_R0.csv'} = 'RF09';
$flight{'CSET-HOLODEC-PBP_GV_20150727_R0.csv'} = 'RF10';
$flight{'CSET-HOLODEC-PBP_GV_20150729_R0.csv'} = 'RF11';
$flight{'CSET-HOLODEC-PBP_GV_20150801_R0.csv'} = 'RF12';
$flight{'CSET-HOLODEC-PBP_GV_20150803_R0.csv'} = 'RF13';
$flight{'CSET-HOLODEC-PBP_GV_20150807_R0.csv'} = 'RF14';
$flight{'CSET-HOLODEC-PBP_GV_20150809_R0.csv'} = 'RF15';
$flight{'CSET-HOLODEC-PBP_GV_20150812_R0.csv'} = 'RF16';

# Hash to relate ref number to short name
$ref{',1,'} = 'Time';
$ref{',2,'} = 'xpos';
$ref{',3,'} = 'ypos';
$ref{',4,'} = 'zpos';
$ref{',5,'} = 'area';
$ref{',6,'} = 'diameter';
$ref{',7,'} = 'major_axis';
$ref{',8,'} = 'minor_axis';
$ref{',9,'} = 'roundness';

$first_time = NULL;

# Now loop through all the PBP csv files and fix the headers
while (<*csv>) {
    open (FILE,$_) or die "Could not open file $_\n";
    $newfile = $_;
    $newfile =~ s/_R0.csv//;
    open (NEWFILE,">$newfile") or die "Could not open file $newfile\n";
    while (my $line = <FILE>) {
	# Remove reference,G,""
	if ($line =~ /reference,G,""/) {next;}

	# Update source to HoloSuite Version 2016
	if ($line =~ /source,G,Holosuite Version X.xx \(Commit #xxxxxx\)/) {
	    $line = "source,G,Holosuite Version 2016\n";
	}

	# Replace flight_date with FlightNumber
	if ($line =~ /flight_date,G,/) {
	    $line = "FlightNumber,G,".$flight{$_}."\n";
	}

        # Remove double quotes from comment lines and replace comma with 
	# semicolon in quotes. Commas are a reserved character in the BADC-CSV 
	# format.
	if ($line =~ /comments,G,(.*)/) {
	    $value = $1;
	    $value =~ s/"//g;
	    $value =~ s/,/;/g;
	    $line = "comments,G,".$value."\n";
	}
	if ($line =~ /command,G,(.*)/) {
	    $value = $1;
	    $value =~ s/"//g;
	    $value =~ s/,/;/g;
	    $line = "comments,G,".$value."\n";
	}
	
	# Add coordinate_variable line before first variable.
	if ($line =~ /long_name,1/) {
            print NEWFILE "coordinate_variable,Time,Time\n";
	}

	# Variable 2 is erroneously listed as QC flag. It should be xpos
	if ($line =~/long_name,2.QC flag,1/) {
	    $line = "long_name,xpos,X-position in image frame,meters\n";
	}

	# Time is given as a float
	if ($line =~ /type,1,int/) {
	    $line = "type,Time,float\n";
	}

	# Change column headers from numbers to short names
	if ($line =~ /1,2,3,4,5,6,7,8,9/) {
	    $line = "Time,xpos,ypos,zpos,area,diameter,major_axis,minor_axis,roundness\n";
	}

	# Remove short_name everywhere
	if ($line =~ /short_name/) { next; }

	# Change all ref numbers to short name
	if ($line =~ /(.*)(,[0-9],)(.*)/) {
	    $line = $1.",".$ref{$2}.",".$3."\n";
	}

	# Correct time metadata to seconds
	if ($line =~ /microseconds/) {
	    $line =~ s/microseconds/seconds/;
	}

	# Fix diameter  microns typo
	if ($line =~ /diameter  microns/) {
	    $line =~ s/diameter  microns/diameter,microns/;
	}

	# Print times of each file, to be used in renaming files to be more
	# descriptive.
	if ($line =~ /(^[0-9.].*),.*/) {
	   if ($first_time == NULL) {
	       $first_time = $1;
	   }
	   $last_time = $1;
        }
	
        # Write modified lines to new file 
        print NEWFILE $line;
    }
    close FILE;
    close NEWFILE;

    # Calculate time range contained in file
    $first_time = int($first_time);
    $hours = int($first_time/3600);
    $mins = ($first_time / 60) %60;
    $secs = $first_time % 60;
    $first_time = sprintf("%02d%02d%02d",$hours,$mins,$secs);
    $last_time = int($last_time);
    $hours = int($last_time/3600);
    $mins = ($last_time / 60) %60;
    $secs = $last_time % 60;
    $last_time = sprintf("%02d%02d%02d",$hours,$mins,$secs);
    print $_.": ".$first_time."-".$last_time."\n";

    # Rename outout file to include time range
    system("mv $newfile $newfile.$first_time-$last_time.csv");

    $first_time = NULL;
}
