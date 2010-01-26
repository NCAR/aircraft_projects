#!/usr/bin/perl 

# This script listens for NOTIFY reports that are sent when a specific action has 
# occurred to the database. The NOTIFY channel is shown here as "light_strike". 
# To send a NOTIFY, use "NOTIFY light_strike" when logged into the database. If this 
# script is running it will print the process ID that sent the NOTIFY and the 
# time the notification was sent.

# Borrowed from http://www.mail-archive.com/pgsql-general@postgresql.org/msg54945.html
# with minor modification by Greg Stossmeister 7/30/2009.

use DBI;
use IO::Select;

$SIG{'ALRM'} = 'handler';

($PROG = $0) =~ s%.*/%%;
#  print "PROG=$PROG\n";

  $num = grep /$PROG/,`/bin/ps -f -u ads`;
#  print "num=$num\n";
  if($num >= 2) {
#   print "convert_trans.pl: Instance already running. exiting\n";
   exit;
  }

$| = 1;

$host = "eol-rt-data.guest.ucar.edu";

$dbattr = {RaiseError => 1, AutoCommit => 1};

$dbh = DBI->connect("dbi:Pg:dbname=real-time-C130;host=$host",'ads','',{AutoCommit => 1, RaiseError => 1, PrintError => 0}) or die "Couldn't connect to database: " . DBI->errstr;

print "Connected to ground database.";

$dbh->do("LISTEN sat_vis");
$dbh->do("LISTEN sat_ir");
$dbh->do("LISTEN radar");

my $fd = $dbh->func("getfd");
my $sel = IO::Select->new($fd);

while (1) {
  print "waiting...";

  eval {
    $sel->can_read;
    $dbh->{RaiseError} = 1;

    my $notify = $dbh->func("pg_notifies");
    if ($notify) {
        my ($relname, $pid) = @$notify;
        my $row = $dbh->selectrow_hashref("SELECT now()");
        print "$relname from PID $pid at $row->{now}\n";
	if ($relname eq "radar") {
          system("/home/local/Systems/scripts/get_radar_image");
	}
	else {
          my $product = substr $relname, 4;
          system("/home/local/Systems/scripts/get_sat_image $product");
	}
    }
  };
  if($@) {
     print "Error $@ with the database\n";
     exit;
  }
}
