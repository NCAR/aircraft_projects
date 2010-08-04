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

$| = 1;

# Check to see if another version of this script is already running
$SIG{'ALRM'} = 'handler';

($PROG = $0) =~ s%.*/%%;
  print "PROG=$PROG\n";

  $num = grep /$PROG/,`/bin/ps -f -u ads`;
  print "num=$num\n";
  if($num >= 2) {
     print "listen_notify.pl: Instance already running. exiting\n";
     exit;
  }


#$host = "hercules.guest.ucar.edu";
$host = "acserver";

$dbattr = {RaiseError => 1, AutoCommit => 1};

$dbh = DBI->connect("dbi:Pg:dbname=real-time;host=$host",'ads','',{AutoCommit => 1, RaiseError => 1, PrintError => 0});

$dbh->do("LISTEN light_strike");

my $fd = $dbh->func("getfd");
my $sel = IO::Select->new($fd);

while (1) {
    print "waiting...";
    $sel->can_read;
    my $notify = $dbh->func("pg_notifies");
    if ($notify) {
        my ($relname, $pid) = @$notify;
        my $row = $dbh->selectrow_hashref("SELECT now()");
        print "$relname from PID $pid at $row->{now}\n";
	system("/home/local/Systems/scripts/lightning/sql_to_kml_1min_lightning.pl");
    }
}
