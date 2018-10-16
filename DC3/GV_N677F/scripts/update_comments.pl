#!/usr/bin/perl

foreach $file (`ls *ICT`) {
    print "Updating comments in $file\n";
    open (FILE, $file) or die "Can't open $file: $!";
    chop $file;
    $outfile = $file.".new";
    print "Output file is $outfile\n";
    open (OUTFILE, ">$outfile") or die "Can't open $outfile: $!";
    while (<FILE>) {
	if (m/^PROJECT_INFO: $/) {print OUTFILE "PROJECT_INFO: DC3, Salina, May-June, 2012\n";}
	elsif (m/^INSTRUMENT_INFO: $/) {print OUTFILE "INSTRUMENT_INFO: UHSAS and CPC\n";}

	# Add new revision numbers to output here. Do NOT remove previous
	# numbers. Comments are cumulative.
	elsif (m/^REVISION:/) {print OUTFILE "REVISION:R2; R1; R0\n";}

	# Add new revision number followed by text comment here.
	elsif (m/^R0: Field Data$/) {print OUTFILE "R2: The NCAR/EOL Research Aviation Facility has recently completed a review and upgrade of its existing algorithms for data processing to incorporate recent improvements that have become available for specific instruments. For details, please see the Appendix to DC3 Project Manager’s Report: Reprocessing\nR1: Reprocess and release data to adjust for modified calibrations in the VCSEL data which are used as the reference hygrometer for all derived humidity variables in this dataset.\nR0: Final Data\n";}

	# If highest revision is R2, then add two to header_lines
	elsif (m/, 1001$/) {
	    $header_lines = $_;
	    $header_lines =~ s/, 1001//;
	    $header_lines = $header_lines+2;
	    print OUTFILE "$header_lines, 1001\n";

	# If highest revision is R2, then add two to special comment count
	} elsif (m/^18$/) {print OUTFILE "20\n";}

	else {print OUTFILE;}
    }
    close (FILE);
    close (OUTFILE);
}
