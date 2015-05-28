#!/usr/bin/perl
###############################################################################
# This scripts will blankout the Gust Pod variables listed below based on the 
# criteria set in the hash below.
# This script is written to be generic, so it can be used to conditionally 
# remove other data from a production netCDF file. Note that it only handles 
# 1-D and 2-D variables but should be straight-forward to expand to other
# cases.
# 
# Written by Janine Aquino May 27, 2015
###############################################################################
use NetCDF;

#Blankout Criteria
%criteria = ( 
    "ROLL" 	=> [5,-5], #deg
    "GGALT" 	=> [0,5000], #m
    "TASF" 	=> [0,130], #m/s
);

# Variables to blankout when above criteria are met
#@vars = ("TAS_GP", "WD_GP", "WI_GP", "UI_GP", "UX_GP", "VI_GP", "VY_GP",
#    "WS_GP");
%vars = (
    "TAS_GP" => ["ROLL", "GGALT", "TASF"],
    "WS_GP" => ["ROLL"],
    "WD_GP" => ["ROLL"], 
    "WI_GP" => ["ROLL"], 
    "UI_GP" => ["ROLL"],
    "UX_GP" => ["ROLL"],
    "VI_GP" => ["ROLL"],
    "VY_GP" => ["ROLL"],
);


# Usage
if (scalar(@ARGV) != 1) {
    print "\nUsage: ./blankout_gp.pl <netCDF file>\n\n";
    exit(1);
}

# Make sure the user entered a netCDF file on the command line
my $filetype  = `file $ARGV[0]`;
if ($filetype !~ /NetCDF Data Format data/) {
    print "\nThis script only works on netCDF files.\n";
    print "Please enter a netCDF file as an argument.\n";
    print "`file $ARGV[0]` returned $filetype\n";
    exit(1);
}

# Get netCDF filename from command line
$infile = $ARGV[0];

# Open the netCDF file for writing
# Get the dims, attributes, and values from the header.
my $ncid = NetCDF::open($infile, NetCDF::WRITE);
my $ndims, my $nvars, my $natts, my $recdim, my $dimname, my $nrec;
NetCDF::inquire($ncid,$ndims,$nvars,$natts,$recdim);

# Get the number of records in the file from the time dimension.
# Time is dimension 0
NetCDF::diminq($ncid,0,$dimname,$nrec);

my %blankout1;
my %blankout2;

# Loop through variables to blank out
foreach $varname (keys %vars) {
    #######################################################
    # Criteria can vary for each variable being blanked out
    # Calculate blankout criteria for current $varname
    #######################################################
    %blankout1 = ();
    %blankout2 = ();
    print "\nPopulate blankouts filter\n";
    foreach $variable (@{$vars{$varname}}) {
        # Determine the index of the blankout var we want to get.
        my @values = ();
        ($dimsize,$ndims_var)=&var_proc($variable,\@values);
	print "\t\t[$criteria{$variable}[0], $criteria{$variable}[1]]\n";

        # set to Missing_Data when var outside criteria
        for (my $i = 0; $i < scalar @values; $i++) {
	  if ($ndims_var == 1) {
	    if (($criteria{$variable}[1] >= $criteria{$variable}[0] &&
	        $values[$i] <= $criteria{$variable}[1] &&
		$values[$i] >= $criteria{$variable}[0]) ||
	        ($criteria{$variable}[1] < $criteria{$variable}[0] &&
	        ($values[$i] < $criteria{$variable}[1] ||
		$values[$i] > $criteria{$variable}[0]))) {
		   $blankout1{$i} = -32767;
	    }
	  } elsif ($ndims_var == 2) {
            for (my $j = 0; $j < scalar @{$values[$i]}; $j++) {
	      if (($criteria{$variable}[1] >= $criteria{$variable}[0] &&
	        $values[$i][$j] <= $criteria{$variable}[1] &&
		$values[$i][$j] >= $criteria{$variable}[0]) ||
	        ($criteria{$variable}[1] < $criteria{$variable}[0] &&
	        ($values[$i][$j] < $criteria{$variable}[1] ||
		$values[$i][$j] > $criteria{$variable}[0]))) {
                    $blankout2{$i}{$j} = -32767;
              }
            }
          } else {
	    &warn_dims();
	  }
        }
    }

    #######################################################
    # Apply blankout to current $varname
    #######################################################
    @values = ();

    # @values empty so read data for varname
    ($dimsize,$ndims_var)=&var_proc($varname,\@values);
    print "Blank out $varname\n";

    if ($ndims_var == 1) {
	    for ($recs=0;$recs<scalar @values;$recs++) {
		if (exists $blankout1{$recs}) {
		    $values[$recs] = $blankout1{$recs};
		}
	    }
    } elsif ($ndims_var == 2) {
        for ($recs=0;$recs<$nrec;$recs++) {
            for ($dim=0;$dim<$dimsize;$dim++) {
	        if (exists $blankout2{$recs}{$dim}) {
		    $values[$recs][$dim] = $blankout2{$recs}{$dim};
	        }
	        if (exists $blankout1{$recs}) {
		    $values[$recs][$dim] = $blankout1{$recs};
	        }
            }
        }
    } else {
	&warn_dims();
    }

    # @values NOT empty so write data for varname
    &var_proc($varname,\@values);
}

NetCDF::close($ncid);

###############################################################################
# Do the work on each variable to blank out - read it in, or if we already
# did that, write it back out to the file.
###############################################################################
sub var_proc () {
    my $varname = shift;
    my $val_ref = shift;
    @values = @$val_ref;

    my $varcount = NetCDF::varid($ncid,$varname);

    # Determine the type and number of dimensions of the variable.
    my $varname,my $type,my $dims, my @dimids, my $atts;
    NetCDF::varinq($ncid,$varcount,$varname,$type,$dims,\@dimids,$atts);

    if ($dims == 1) {
	$dimsize = 1;
    } elsif ($dims == 2) {
        NetCDF::diminq($ncid,2,$dimname,$dimsize);
    } else {
        &warn_dims();
    }

    # If there are values in the array...
    if (@values == 0) {
	print "\tRead $dims-D var $varname\n";
	if ($dims == 1) {
	    # Read a 1-D integer array
	    my @start = (0);
	    my @count = ($nrec);
	    NetCDF::varget($ncid,$varcount,\@start,\@count,\@values);
        } elsif ($dims == 2) {
            # Read a 2-D integer array
	    for ($recs=0;$recs<$nrec;$recs++) {
                my @start = ($recs,0);
                my @count = (1,$dimsize);
	        @vals=();
                NetCDF::varget($ncid,$varcount,\@start,\@count,\@vals);
	        $values[$recs] = [ @vals ];
    	    }
	} else {
	    &warn_dims();
        }
    } else { # else...
	print "\tWrite $dims-D var $varname\n";
	if ($dims == 1) {
            # Write a 1-D integer array
            my @start = (0);
            my @count = ($nrec);
            NetCDF::varput($ncid,$varcount,\@start,\@count,\@values);
	    @values = ();
            NetCDF::varget($ncid,$varcount,\@start,\@count,\@values);
        } elsif ($dims == 2) {
            # Write a 2-D integer array
	    for ($recs=0;$recs<$nrec;$recs++) {
	        my @start = ($recs,0);
	        my @count = (1,$dimsize);
	        NetCDF::varput($ncid,$varcount,\@start,\@count,\@{$values[$recs]});
	    }
	    @values = ();
	} else {
	    &warn_dims();
	}
    }

    @$val_ref = @values;
    return($dimsize,$dims);
}
###############################################################################
sub warn_dims() {
    print "Code only handles vars with one or two dims\n";
    print "Var $varname has $ndims_var dimensions\n";
    exit(1);
}
