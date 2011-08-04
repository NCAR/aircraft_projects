#!/usr/bin/perl

$outfile = $ARGV[0];
$outfile =~ s/.txt/.data/;
open (OFILE, ">$outfile") or die "Can't open $outfile:$!\n";
$line = <>;
($numlines) = split(' ',$line);
$linenum = 0;
while ($line = <>) {
    $linenum++;
    if ($linenum < $numlines) {next;}
    if ($line !~ /^TIME/) {
	($time, $rest) = split(' ',$line,2);
	$time = $time - 3.5;
	$line = join(' ',$time,$rest);
    }
    print OFILE $line;
}
