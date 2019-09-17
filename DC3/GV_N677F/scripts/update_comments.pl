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
	elsif (m/^REVISION:/) {print OUTFILE "REVISION:R3; R2; R1; R0\n";}

	# Add new revision number followed by text comment here.
	elsif (m/^R0: Field Data$/) {print OUTFILE "R3: This update contains corrected 2DC data (CONC2DC[AR]_LWOI, DBAR2DC[AR]_LWOI, and PLWC2DC[AR]_LWOI). It was discovered that all particles in a single buffer got time-stamped with the data-system time tag of the end off the buffer. So for concentrations above 5-10/L, or when in heavy cloud, the system writes multiple buffers per second so the time-stamp will be very close to accurate. But when a buffer spans multiple seconds, all the particles were being binned to the second of the end time-stamp for the buffer. This has now been corrected so data is spread across the time-period of the buffer correctly. This version also uses exact circle fitting for measuring particle size and limits accepted particles to center-in images.\nR2: The NCAR/EOL Research Aviation Facility has recently completed a review and upgrade of its existing algorithms for data processing to incorporate recent improvements that have become available for specific instruments. For details, please see the Appendix to DC3 Project Manager’s Report: Reprocessing\nR1: Reprocess and release data to adjust for modified calibrations in the VCSEL data which are used as the reference hygrometer for all derived humidity variables in this dataset.\nR0: Final Data\n";}

	# If highest revision is R2, then add two to header_lines
	elsif (m/, 1001$/) {
	    $header_lines = $_;
	    $header_lines =~ s/, 1001//;
	    $header_lines = $header_lines+3;
	    print OUTFILE "$header_lines, 1001\n";

	# If highest revision is R2, then add two to special comment count
	} elsif (m/^18$/) {print OUTFILE "21\n";}

	else {print OUTFILE;}
    }
    close (FILE);
    close (OUTFILE);
}
