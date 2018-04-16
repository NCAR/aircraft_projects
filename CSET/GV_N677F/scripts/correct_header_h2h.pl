#!/usr/bin/perl
use File::Basename;

# Hash to relate filename to flight number
$flight{'CSET-HOLODEC-H2H_GV_20150707.csv'} = 'RF02';
$flight{'CSET-HOLODEC-H2H_GV_20150709.csv'} = 'RF03';
$flight{'CSET-HOLODEC-H2H_GV_20150712.csv'} = 'RF04';
$flight{'CSET-HOLODEC-H2H_GV_20150714.csv'} = 'RF05';
$flight{'CSET-HOLODEC-H2H_GV_20150719.csv'} = 'RF07';
$flight{'CSET-HOLODEC-H2H_GV_20150722.csv'} = 'RF08';
$flight{'CSET-HOLODEC-H2H_GV_20150724.csv'} = 'RF09';
$flight{'CSET-HOLODEC-H2H_GV_20150727.csv'} = 'RF10';
$flight{'CSET-HOLODEC-H2H_GV_20150729.csv'} = 'RF11';
$flight{'CSET-HOLODEC-H2H_GV_20150801.csv'} = 'RF12';
$flight{'CSET-HOLODEC-H2H_GV_20150803.csv'} = 'RF13';
$flight{'CSET-HOLODEC-H2H_GV_20150807.csv'} = 'RF14';
$flight{'CSET-HOLODEC-H2H_GV_20150809.csv'} = 'RF15';
$flight{'CSET-HOLODEC-H2H_GV_20150812.csv'} = 'RF16';

# Hash to relate ref number to short name
$ref{',1,'} = 'Time';
$ref{',2,'} = 'QCflag_LWII';
$ref{',3,'} = 'THDCC_LWII';
$ref{',4,'} = 'THDCA_LWII';
$ref{',5,'} = 'CHDC_LWII';
$ref{',6,'} = 'AHDC_LWII';
$ref{',5:30,'} = 'CHDC_LWII';
$ref{',31:56,'} = 'AHDC_LWII';

$first_time = NULL;
$found_flag = "FALSE";
$found_type = "FALSE";
@width = [];

# Now loop through all the PBP csv files and fix the headers
while (</scr/raf/Prod_Data/CSET/HOLODEC/H2H/bad_header/CSET-HOLODEC-H2H_GV_2015????.csv>) {
    open (FILE,$_) or die "Could not open file $_\n";
    $newfile = $_;
    $newfile =~ s/.csv//;
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
	    print basename($_)."\n";
	    $line = "FlightNumber,G,".$flight{basename($_)}."\n";
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

	# Time is given as a float
	if ($line =~ /type,1,int/) {
	    $line = "type,Time,float\n";
	}

	# Change column headers from numbers to short names
	if ($line =~ /1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56/) {
	    @vals = split(",",$line);
	    $line = "";
	    foreach $val (@vals) {
		if ($val >=5 && $val <= 30) {
		    $line .= $ref{',5:30,'}.",";
		} elsif ($val >=31 && $val <= 56) {
		    $line .= $ref{',31:56,'}.",";
		} else {
	            $line .= $ref{','.$val.','}.","
		}
	    }
	    $line .= "\n";
	    $line =~ s/,$//;
	}

	# Remove short_name everywhere
	if ($line =~ /short_name/) { next; }

	# Fix flags
	if ($line =~ /flag_values,2,2/) { next; }
	if ($line =~ /Final \(manual processing\)/) { next; }
	if ($line =~ /Preliminary \(automatic processing\)/) {
		$line = "flag_meanings,".$ref{',2,'}.",Preliminary (automatic processing),Final (manual processing)\n";
	}
	if ($line =~ /fill_value = -99999/) { next; }

	# CHDC long name has an extra comma - fix
	if ($line =~ /long_name,5,,/) {
	    $line =~ s/5,,/$ref{',5,'},/;
	    print NEWFILE $line;
	    
	    # Add SampleVolume to CHDC - needed for completeness and for ncpp
	    $line = "SampleVolume,".$ref{',5,'}.",13\n";
	    print NEWFILE $line;
	    $line = "SampleVolumeUnits,$ref{',5,'},cm3\n";
	}

	# Correct long name of AHCD
	if ($line =~ /long_name,6,Number concentration per bin,1/) {
	    $line =~ s/concentration/of particles/;
	}


	# Dimensionless units should be #, not 1
	if ($line =~ /^long_name.*1$/) {
	    $line =~ s/1$/#/;
	}

	if ($line =~ /flag_values,2,1/ && $found_flag =~ /TRUE/) { next; } #Remove duplicate
	if ($line =~ /type,6,float/ && $found_type =~ /TRUE/) { next; } #Remove duplicate
	if ($line =~ /type,6,float/) { 
	    $found_type = "TRUE"; 
	} 

	# Change all ref numbers to short name
	if ($line =~ /flag_values,2,1/) {
	    $line = "flag_values,".$ref{',2,'}.",1,2\n";
	    $found_flag = "TRUE";
	} elsif ($line =~ /(.*)(,[0-9],)(.*)/ and ($line !~ /(^[0-9.].*),.*/)) {
	    $line = $1.",".$ref{$2}.",".$3."\n";
	}
	if ($line =~ /(.*)(,[0-9][0-9]?:[0-9][0-9]?,)(.*)/) {
	    $line = $1.",".$ref{$2}.",".$3."\n";
	}

	# Add first bin of 6.0 and rename attribute
	if ($line =~ /cell_size,([A-Z_]*),(.*)/) {
	    # First calculate bin widths of existing bins
	    #print "Bins: $2\n";
	    @bins = split(",",$2);
	    #print "Widths: ";
	    for ($i=0;$i<=(scalar @bins)-1;$i++) {
		if ($i > 0) { 
		    $width[$i]= $bins[$i]-$bins[$i-1];
		} else {
		    $width[$i]= $bins[$i]-0;
		}

		#print $width[$i].",";
	    }
	    #print "\n";
	    $line = "CellSizes,$1,6.0,$2\n";
	}

	# Rename cell_size_unts
	if ($line =~ /cell_size_units/) {
	    $line =~ s/cell_size_units/CellSizeUnits/;
	}

	# Remove the word "upper" from CellSizeNote
	if ($line =~ /cell_size_note/) {
	    $line =~ s/upper //;
	    $line =~ s/cell_size_note/CellSizeNote/;
	}

	# Remove HistogramNote
	if ($line =~ /histogram_note/) { next; }

	# Correct time metadata to seconds
	if ($line =~ /microseconds/) {
	    $line =~ s/microseconds/seconds/;
	}
	
	# Fix units
	if ($line =~ /#\/cm3\/um/) {
	    $line =~ s/\/um//;
	}

	# Print times of each file, to be used in renaming files to be more
	# descriptive.
	if ($line =~ /(^[0-9.].*),.*/) {
	   if ($first_time == NULL) {
	       $first_time = $1;
	   }
	   $last_time = $1;
	   # Fix data to match new units
	   @values = split(",",$line);
	   for ($i=4;$i<30;$i++) {
	       $values[$i]=$values[$i]*$width[$i-4];
	   }
	   $line = join(",",@values);
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
    $found_flag = "FALSE";
    $found_type = "FALSE";
}
