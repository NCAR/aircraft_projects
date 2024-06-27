#!/usr/bin/perl -w
use strict;

# Stuart Beaton, NCAR/RAF

# Generates an annotated MPEG-4 video from a directory of images and
# netcdf file. Reads a parameter file specified on the command line to
# get the netcdf file, image directory, variables, etc.

# 2006 Aug 23 - SB
# Added $cameraName and image adjustment keywords.
# Added default scale, outputResolution, and bit rate for axis camera.

# 2010 Jan 26 - JAG
# Added more comments. Streamlined code and moved some code to subroutines.
# Generalized to support many different camera configuration/number of
# cameras.

# 2010 Jun 17 - JAG
# Added ability to increment enddate extracted from .nc global vals if flight
# rolls over midnight.

# 2010 Jun 21 - JAG
# Move outputWidth to keywords (was hardcoded) so that if data is too wide
# and overwrites labels, it can be fixed in config file.
# Change data image height to pull from outputResolution, not scale, so
# data can be taller than image if necessary to accomodate PI var request
# list.
# Bug in enddate extraction added Jun 17. Both end month and end minute were 
# emn - fixed.

# 2010 Sept 23 - JAG
# Movie Date and Time range was only being calculated from netCDF file if netCDF 
# data was included. Add ability to calc date/time from image filenames.

# 2010 Oct 1 - JAG
# Code sometimes dies mid processing. If startNum given on command line
# recover by starting there.

# 2012 Jan 18 - JAA (= JAG)
# If data is missing, continue on without including data.

# 2012 Feb 10 - JAA
# Add new param movieDirectory to specify where to output movies.

# 2012 Feb 22 - JAA
# Handle case where images don't start until after midnight.
# 
# 2012 Apr 26 - JAA
# Upgrade to handle 4 images for TORERO
#
# 2012 May 1 - JAA CBS 
# Added option to overlay imagePointing on each camera image.
#
# 2018 March 13 - TMT
# Added argument to two pass MPEG encoding to enable previewing in ZINC. 
# ------------------------------------------------------------------------------
# Files used:
#	parameters file specified on command line.
#	$netcdfFile - netCDF flight data file read from parameters file.
#
# names hardcoded in Initialization section:
#	$headerDump - netCDF header dump from ncdump.
#	$batchFile - n2asc batch input file.
#	$dataFile - flight values dumped from n2asc.
#	$annotatedImageDirectory - dir to dump annotated images (images
#	containing one or more camera frames and flight level data listing)
# ------------------------------------------------------------------------------

#Uses ...
use Image::Magick;		# Non-standard ImageMagick extensions.
use Sys::Hostname;		# standard module for determining hostname.
use Time::Local;
use POSIX qw(strftime);
use Env;

# -------------------------------------------------------------------
# ------------------------ Hardcoded values -------------------------
# -----------(These may need to be changed in the future.)-----------
# -------------------------------------------------------------------

# Known cameras with default parameters available.
my @knownCameras = ("Axis","Flea","Down_Flea");

# Set defaults for variables
my $annotationFont = "Courier-Bold";
my $fontSize = "13";
my $fontColor = "black";
my $startNum = -1;

# List possible keywords for use in ParamFile
my %possible_keywords = ( # value = description, default
    "includeData" => ("yes or no"),
    "netcdfFile" => ("can use #### to indicate flight, e.g. rf01"),
    "gravityD" => ("NorthEast, East, etc. Default = NorthEast"),
    "cameraName" => ("knownCameras"),
    "imageDir1" => ("can use #### to indicate flight, e.g. rf01"),
    "gravity1" => ("NorthWest, North, etc. Default = NorthWest for 1-2 images, North for more"),
    "movieDirectory" => ("location to write annotated images and final movies"),
    "overlayImageTime" => ("yes or no"),
    "overlayImagePointing" => ("yes or no"),
    "outputResolution" => ("size of entire image in pixels, e.g. num x num"),
    "outputResolutionD" => ("size of entire image with data in pixels, e.g. num x num. For 3-image layout, set this = to outputResolution"),
    "outputWidth" => ("Width of data portion of image; default = 200"),
    "outputFrameRate" => ("frames per second, Playback at 15 fps when recorded at 1 fps."),
    "scale" => (" num x num pixels, size of each camera image"),
    "gamma" => (" eg 1.1"),
    "sharpen" => (" eg 0.0x1.0"),
    "annotationFont" => (" eg Courier-Bold"),
    "fontSize" => (" point, eg 13"),
    "mp4BitRate" => (" eg 1500000"),
    "crop" => ("cropGeometry"),
    "includeProjectName" => (" no or yes"),
    "includeProjectNumber" => (" no or yes"),
    "numCameras" => ("default = 1"),
    "imageDir2" => ("can use #### to indicate flight, e.g. rf01"),
    "gravity2" => ("SouthWest, North, etc"),
    "imageDir3" => ("can use #### to indicate flight, e.g. rf01"),
    "gravity3" => ("SouthWest, North, etc"),
    "imageDir4" => ("can use #### to indicate flight, e.g. rf01"),
    "gravity4" => ("SouthWest, North, etc"),
);

my @flightData;
my $theText;
my $outputHeight;
my $outputWidth;
my ($projectNumber,$flightNumber,$time_interval,$headerText,$outputFileTimes);
# -------------------------------------------------------------------
# ----------------------------- Usage -------------------------------
# -------------------------------------------------------------------
#ffmpeg is only installed in mercury or eol-saturn, so must run there
if ( (split /\./, hostname() !~/mercury/) && (split /\./, hostname() !~/eol-saturn/) ) {
        print "Run on mercury for higher performance!\n\n";
        exit(0);
}
#if no arguments or argument is "-h", print help text and exit.
if ( (scalar(@ARGV) < 2) || (scalar(@ARGV) > 3)  || ($ARGV[0] eq "-h") ) {
	print "\n Perl script to generate annotated movies from images\n";
	print " USAGE: $0  parameterFileName <flight eg. rf01> [startnum]\n";
	print " MUST BE RUN ON mercury or eol-saturn!!!\n\n";
	print "\n";
	print " The parameter file is an ascii file containing the following";
	print " lines:\n";
	foreach my $param (keys %possible_keywords) {
	    print "$param = <$possible_keywords{$param}>\n";
	}
	print "endParameters\n\n";
	print " Then list flight level parameters, one per line, using name\n";
	print " given in netCDF file, eg:\n";
	print "GGALT\nGGLAT\nGGLON\n...\n";
	print "endVariablesLT\n";
	exit(0);
}

# Initialize image objects. 
my $Image = Image::Magick->new();		# Image(s) read in.
my $outputImage = Image::Magick->new();		# Final Image to be written out.
my $outputImageD = Image::Magick->new();	# Temp Image for adding data.
my $labelImage = Image::Magick->new();		# Image of variable labels.
my $valueImage = Image::Magick->new();		# Image of variable values.

# -------------------------------------------------------------------
# ------------------------- Initialization --------------------------
# -------------------------------------------------------------------

# Get start time to create unique file names
my $startTime = time();

# Hardcoded file names.
my $headerDump="./headerDump_$startTime"; #Tempfile to dump netcdf header
my $batchFile="./batchFile_$startTime";
my $dataFile="./dataFile_$startTime.asc";

my $annotatedImageDirectory;

# -------------------------------------------------------------------
# Get annotation parameters
# -------------------------------------------------------------------
my $keyref = {%possible_keywords};
my %parameters = (); #empty hash to hold keywords from ParamFile
my $keywords = \%parameters; #reference to keyword hash
if ($ARGV[2]) {
   $startNum = $ARGV[2];
   print "START PROCESSING AT IMAGE NUMBER $startNum\n";
}

&get_keywords($ARGV[0],$ARGV[1],$keyref,$keywords);

# -------------------------------------------------------------------
# Defaults for various cameras if not set in parameters file.
# -------------------------------------------------------------------
!$keywords->{cameraName} 
    and die "Camera must be identified in the parameters file! \n";

# Make sure camera given in ParamFile is known camera type
my $found = 0;
foreach my $camera (@knownCameras) {
   if ($camera =~ $keywords->{cameraName}) { $found = 1; last;}
}
if (!$found) {die "Unknown camera! \n";}

if (!$keywords->{numCameras}) {$keywords->{numCameras} = 1;}
if (!$keywords->{includeProjectName}) {$keywords->{includeProjectName}="no";}
if (!$keywords->{includeProjectNumber}) {$keywords->{includeProjectNumber}="no";}
if (!$keywords->{overlayImageTime}) {$keywords->{overlayImageTime}="no";}
if (!$keywords->{outputWidth}) {$keywords->{outputWidth}=200;}

if ($keywords->{cameraName} =~ m/Axis/) {	
        # rescale to square pixels (width / 1.1) in approximate widescreen (16:9)
	# format and allowing room for annotation.
	if (!$keywords->{scale}) {$keywords->{scale}= "640x480!";}	
        	# The '!' forces resize to exact dimensions, accounting for pixel
		# aspect ratio.
	if (!$keywords->{outputResolution}) {
	        $keywords->{outputResolution} = "800x480";}
		# The default output resolution assumes a single image movie
	if (!$keywords->{outputFrameRate}) { $keywords->{outputFrameRate} = 15; }	
		# 15 fps playback when recorded at 1 fps.
	if (!$keywords->{mp4BitRate}) { $keywords->{mp4BitRate} = 1500000; }
}

if ($keywords->{cameraName} =~ m/Flea/) { 	
	# Reduce resolution from 1024x768, adjust gamma, and sharpen.
	if (!$keywords->{scale}) { $keywords->{scale} = "640x480"; }
	if (!$keywords->{outputResolution}) { $keywords->{outputResolution} = "800x480"; }
	if (!$keywords->{sharpen}) { $keywords->{sharpen} = "0.0x1.0"; }
	if (!$keywords->{gamma}) { $keywords->{gamma} = 1.1; }
	if (!$keywords->{outputFrameRate}) { $keywords->{outputFrameRate} = 15; }	
		# Playback at 15 fps when recorded at 1 fps.
	if (!$keywords->{mp4BitRate}) { $keywords->{mp4BitRate} = 1500000; }
}
if ($keywords->{cameraName} =~ m/Down_Flea/) { 	
	# Reduce resolution from 1024x768, adjust gamma, and sharpen.
	if (!$keywords->{scale}) { $keywords->{scale} = "640x480"; }
	if (!$keywords->{outputResolution}) { $keywords->{outputResolution} = "800x480"; }
	if (!$keywords->{sharpen}) { $keywords->{sharpen} = "0.0x1.0"; }
	if (!$keywords->{gamma}) { $keywords->{gamma} = 1.1; }
	if (!$keywords->{outputFrameRate}) { $keywords->{outputFrameRate} = 30; }	
		# Playback at 30 fps when recorded at 2 fps.
	if (!$keywords->{mp4BitRate}) { $keywords->{mp4BitRate} = 1500000; }
}

print "Camera defaults set for $keywords->{cameraName}\n";

if ($keywords->{includeData} eq "yes") {
    # -------------------------------------------------------------------
    # Get flight info from header file
    # -------------------------------------------------------------------
    ($projectNumber,$flightNumber,$time_interval,$headerText,$outputFileTimes) = 
        &dump_netcdfFile_header($keywords->{netcdfFile},$headerDump);

    # -------------------------------------------------------------------
    # Create n2asc input batch file, clobbering old one if it exists.
    # -------------------------------------------------------------------
    &create_n2asc_batchfile($batchFile,$keywords,$dataFile,$time_interval);

    # Create data file from netCDF file using batchFile & load data file
    # into this script.
    &create_ascii_dataFile($dataFile,$batchFile);
    ($theText, @flightData) = &load_ascii_data($dataFile);

    #Write flight level data variables given in ParamFile to the label image.
    (undef,$outputHeight) = split(/x/,$keywords->{outputResolution});
    $outputWidth = $keywords->{outputWidth};
    if ($keywords->{numCameras} > 1) {$outputHeight = $outputHeight/2;}
    &write_vars2labelImage($labelImage,$headerText,$theText,$outputHeight,$outputWidth);
}

# -------------------------------------------------------------------
# ----------------------- Load image list ---------------------------
# -------------------------------------------------------------------

# Open the directory and read the list of JPEG files into @jpegFiles array.
opendir(IMAGE_DIRECTORY, "$keywords->{imageDir1}") 
	|| die "Image directory $keywords->{imageDir1} not found";
my @tempList = grep{/.jpg/} readdir IMAGE_DIRECTORY;
closedir IMAGE_DIRECTORY;

# sort by filename which is the image time. 
# Alternative would be to search the entire list for each second of data.
# (Should see how much additional time that would add.)
my @jpegFiles=sort @tempList;
my $numFiles = scalar(@jpegFiles);
print "Number of images to process = $numFiles\n";

# If not including netCDF data then read flight number from image dir path.
if ($keywords->{includeData} ne "yes") {
    $flightNumber = $keywords->{imageDir1};
    $flightNumber =~ s/^.*flight_number_(....).*/$1/;
}

# Set the output dir for annotated images and final movies
!$keywords->{movieDirectory} 
    and die "movieDirectory must be identified in the parameters file! \n";

$annotatedImageDirectory = 
    $keywords->{movieDirectory}."/AnnotatedImages_$flightNumber";
# Delete old annotated images directory and create a new (empty) one.
# Little error checking here right now, and could use FILE::PATH functions.
if ($startNum == -1) {
    -d $annotatedImageDirectory and system "rm -r $annotatedImageDirectory";
    mkdir "$annotatedImageDirectory" or die "Couldn't create $annotatedImageDirectory directory!";
}
print "Annotated images will be stored in $annotatedImageDirectory\n";

# --------------------------------------------------------------------
#---------------------- Delete temporary files -----------------------
# --------------------------------------------------------------------

unlink $batchFile;
unlink $headerDump;
unlink $dataFile;

# --------------------------------------------------------------------
#---------------------- End of Initialization ------------------------
# --------------------------------------------------------------------


# --------------------------------------------------------------------
#---------------------- Image annotation loop ------------------------
# --------------------------------------------------------------------
# An alternative would be to get the time from the data file and load
# the appropriate image. If that image is missing, just keep going.
# --------------------------------------------------------------------

# Find a matching time in the data file
my $fileNum=0;
my $haveData = 1;
my $imageTime = 0;
my $prevImageTime = 0;
foreach my $fileName (@jpegFiles) {
        # Code sometimes dies mid processing. If startNum given on command line
        # recover by starting there.
	$fileNum++;		#track the number of image files processed

        if ($fileNum <= $startNum) {
            print "Skipping image $fileNum\n";
            next;
        }


	# clear the images, set output attributes, then read and scale an image
	@$Image = ();
	@$outputImage = ();
	@$outputImageD = ();
	@$valueImage = ();
	
	# Size output image with white background (canvas).
	$outputImage->Set(size=>$keywords->{outputResolution}, quality=>90);
	$outputImage->ReadImage('xc:white');	# White canvas
	$outputImageD->Set(size=>$keywords->{outputResolutionD}, quality=>90);
	$outputImageD->ReadImage('xc:white');	# White canvas

	my $gravity;
	if ($keywords->{numCameras} > 4) {
	    print "Code only handles up to four cameras. Update code!\n";
	    exit(1);
	}
        if ($keywords->{gravity1}) {
	    $gravity = $keywords->{gravity1}
	} else {
	    if ($keywords->{numCameras} == 1) {$gravity = 'NorthWest'};
	    if ($keywords->{numCameras} == 2) {$gravity = 'NorthWest'};
	    if ($keywords->{numCameras} == 3) {$gravity = 'North'};
	    if ($keywords->{numCameras} == 4) {$gravity = 'North'};
	}
	
	# Get image time so can later pull flight data for this time from data
	# file.
	# - The last 6 characters of the filename before the .jpg is the time of
	# the camera or filesaving-computer (HHMMSS)
	# - Ignore the date which preceeds the time since the ascii file 
	# doesn't include it.
	# - Since the date is in the filename, flights that roll over to 
	# UTC 000000 are still sorted properly.
        #Save previous image time to check for gaps in imagery
	$prevImageTime = $imageTime; 
	$imageTime=substr($fileName,-10,6);
	my $imageTime_withColons=substr($imageTime,0,2).':'.
		substr($imageTime,2,2).':'.substr($imageTime,4,2);

	# If not including netCDF data then determine image time from image 
	# names.
	# Determine start time here and end time at end of loop.
	my $imageDate = substr($fileName,-17,6);
	if ($keywords->{includeData} ne "yes" && $fileNum == 1) {
	    $outputFileTimes = $imageDate.'.'.$imageTime;
	}

	print "image $fileNum/$numFiles: $fileName $imageTime\n";

	# Now process the cameras.
	my $addtl_cameras = 1;
	while ($addtl_cameras <= $keywords->{numCameras}) {
            my $Directory = $keywords->{"imageDir$addtl_cameras"};
	    $Image = &get_camera_image($Directory, $fileName);
            &adjust_camera_image($keywords->{crop},$keywords->{scale},
	        $keywords->{gamma},$keywords->{sharpen},$Image);
	    $gravity = $keywords->{"gravity$addtl_cameras"}; 
	        
	    if ($keywords->{overlayImageTime} eq "yes") {
	        my $imageDateTime = $fileName;
	        $imageDateTime =~ s/.jpg//;
	        $Image->Annotate(gravity=>'SouthWest', font=>"Helvetica-Bold",
	            undercolor=>'grey85', pointsize=>12, text=>$imageDateTime);
	    }

	    if ($keywords->{overlayImagePointing} eq "yes") {
	        my $dir = $keywords->{"imageDir$addtl_cameras"};
	        my @parts = split('/',$dir);
	        my $pointing = pop(@parts);
	        chomp $pointing;
	        $Image->Annotate(gravity=>'NorthEast', font=>"Helvetica-Bold",
	          undercolor=>'grey85', pointsize=>12, text=>" ".$pointing." ");
	    }
	    $outputImage->Composite( image=>$Image, gravity=>$gravity);
	    @$Image = ();

	    $addtl_cameras += 1;
	}

	# Determine the output image filename.
	my $outputImageName=
	    sprintf('%s/%05d.jpg',$annotatedImageDirectory,$fileNum);
            system("rm /tmp/magick-*");
	###############
	# flight data #
	###############
	# Get the data from the data file and put into an array. If the the 
	# datafile time does not match the image filename time, get the next 
	# line of the data file until it does.
	# This assumes there are no time gaps in the ascii file generated from 
	# the netCDF file. This is a safe assumption, especially with production
	# data. BUT the first image must be equal to or later than the first 
	# data point. (Modified to handle first image before first data
	# Jan 2012).
	$haveData=1;
	if ($keywords->{includeData} eq "yes") {
	    $theText = '';
	    if (scalar(@flightData) == 0) {
	       print "End of data file reached searching for ".
	             "$imageTime_withColons\n";

	       # If data is missing, continue on without including data.
	       $haveData=0;
	    } else {
	        my $dataDate = substr($flightData[0],0,10);
	        $dataDate =~ s/-//g;
	        my $dataTime = substr($flightData[0],11,8);
	        $dataTime =~ s/://g;
	        print "data start $dataDate $dataTime\n";
	        if (
	        # Special Case: Midnight rollover with data gap
	        # Both dataTime and imageTime rollover to 00:00:00.
	        # If there is not an image gap, then data has already
	        # incremented to 00:00:00, image = data and we are good.
	        # If there IS a data gap over midnight, then data increments to
	        # pre-midnight time, but image is after midnight (i.e. data has
	        # hour 23, image has hour 00, and dataTime < imageTime test fails
	        # incorrectly. So test for this added Feb 2012.
		((($imageTime - $prevImageTime) != 1) && ($prevImageTime > $imageTime)) 
	        # If the first image in the file is after midnight, but the data
	        # is before, we need to increment the data until it catches the 
		# image.
	        || (($prevImageTime == 0) && ("20".$imageDate > $dataDate))
	        ) {
		    # Increment until data reaches midnight rollover. Next while
		    # loop will finish incrementing data until it reaches image
                    while ($dataTime != 000000) {
                        shift(@flightData);
	                $dataTime = substr($flightData[0],11,8);
	                $dataTime =~ s/://g;
	                if (scalar(@flightData) == 0) {
	                print "End of data file reached searching for ".
	                      "$imageTime_withColons\n";

	                # If data is missing, continue on without including data.
	                $haveData=0;
	                exit(1);
	                last;
	                }
		    }
	        }
                if ($dataTime > $imageTime) { $haveData = 0; }
	        while ($dataTime < $imageTime)  {
	            # print "M";# Can count 'M's to find out how many images were 
	            # missing.
                    shift(@flightData);
	            $dataTime = substr($flightData[0],11,8);
	            $dataTime =~ s/://g;
	        }
	        print "data final $dataTime\n";
	        # Create the data string.
	        if ($haveData == 1) {
	            my @dataItems = split(',',shift(@flightData));
	            foreach my $value (@dataItems) { 
		        $theText=$theText.sprintf("%s\n", $value);
	            }
	        # chomp $theText;		# Remove final newline.
	        }
	    }
	
	    # Initialize image used for variable values.
	    $valueImage->Set( size=>"${outputWidth}x$outputHeight");
	    $valueImage->ReadImage('xc:none');		# Transparent canvas

	    # Add an image consisting of the variable values to the bottom,
	    # right so can overlay with the existing labelImage
	    $valueImage->Annotate( font=>$annotationFont, pointsize=>$fontSize, x=>15,
	        weight=>500, gravity=>'SouthEast', fill=>"$fontColor",text=>"$theText");

	    #################	
	    # Composite all three images (variable values, labels, and camera 
	    # image). Put the values along the lower right side of the image
	    #################	

            if (!$keywords->{gravityD}) {$gravity = 'NorthEast';}
	    $gravity = $keywords->{"gravityD"}; 
	    $outputImageD->Composite( image=>$outputImage, gravity=>'West');
	    $outputImageD->Composite( image=>$valueImage, gravity=>$gravity);
	    $outputImageD->Composite( image=>$labelImage, gravity=>$gravity);
	    # write out the image.
	    $outputImageD->write($outputImageName);
        } else {
	    # write out the image.
	    $outputImage->write($outputImageName);
	}
}

# If not including netCDF data then determine image time from image names.
# Determine end time here.
if ($keywords->{includeData} ne "yes") {
    $outputFileTimes = $outputFileTimes.'_'.$imageTime;
}


# --------------------------------------------------------------------
#----------------------- Two pass MPEG encoding ----------------------
# --------------------------------------------------------------------
my $outputFrameRate = $keywords->{outputFrameRate};;
my $mp4BitRate = $keywords->{mp4BitRate};;

my $outputFilename = "$flightNumber.$outputFileTimes.mp4";

#attempt by TMT to make movies playable in field catalog
#my $command = "usr/bin/ffmpeg -pattern_type glob -i $annotatedImageDirectory/%05d.jpg  -c:v libx264 -r $outputFrameRate -pix_fmt yuv420p -y $outputFilename";

# First ffmpeg pass
my $command = "/usr/bin/ffmpeg -i $annotatedImageDirectory/%05d.jpg -r $outputFrameRate -pix_fmt yuv420p -b:v $mp4BitRate -y -passlogfile ./ffmpeg_$flightNumber -pass 1 ".$keywords->{movieDirectory}."/$outputFilename";
print "$command\n";
if (system "$command") { die "Unable to create MPEG file $outputFilename, pass 1 using command $command"}; 
$command = "/usr/bin/ffmpeg  -i $annotatedImageDirectory/%05d.jpg -r $outputFrameRate -pix_fmt yuv420p -b:v $mp4BitRate -y -passlogfile ./ffmpeg_$flightNumber -pass 2 ".$keywords->{movieDirectory}."/$outputFilename";
print "$command\n";
if (system "$command") {die "Unable to create MPEG file $outputFilename, pass 2 using command $command"};

# keep proj dir clean by moving log files created during MPEG encoding to /tmp
system "mv *ffmpeg* /tmp";

# --------------------------------------------------------------------
#-------------------------------- END --------------------------------
# --------------------------------------------------------------------
print "Normal program Completion.\n";


# ------------------------------------------------------------------------------
#--------------------------------- SUBROUTINES ---------------------------------
# ------------------------------------------------------------------------------

# -------------------------------------------------------------------
# ---------------- Get Camera Image from jpg file -------------------
# -------------------------------------------------------------------
sub get_camera_image() {
    my ($Directory, $fileName) = @_;
    #
    # This subroutine reads in a single image from a jpg file.
    # assumes filenames with endings like *HHMMSS.jpg
    #


    # Initialize a new image to work with
    my $Image = Image::Magick->new();	
    @$Image = (); # clear the image

    if ($fileName !~ /[0-9][0-9][0-9][0-9][0-9][0-9].jpg/) {
	print "Filename $Directory/$fileName doesn't match ".
	    "expected pattern: *HHMMSS.jpg\n";
 	exit(1);
    } else {

	# If file doesn't exist:

	# Try pulling off YYMMDD_HHMMSS.jpg from the end of the
	# filename and matching that.
	if (! -e "$Directory/$fileName") {
	    $fileName=substr($fileName,-17,17);
	}

	# Try changing _ to - in filename and matching that.
	if (! -e "$Directory/$fileName") {
	    $fileName =~ s/_/-/;
	}
	
	# Try adding _d to filename before .jpg and matching that.
	if (! -e "$Directory/$fileName") {
	    $fileName =~ s/.jpg/_?.jpg/;
	}

	#  If still doesn't exist, warn user and continue.
	#if (! -e "$Directory/$fileName")
	my @files = glob("$Directory/$fileName");
	if (scalar(@files) == 0) {
	    printf "$Directory/$fileName";
	    print " not found!\n";
	} else {
	    $fileName  = $files[0];
	    printf "$fileName";
	    print "\n";
	}

	#Read in current image, or if none, set to white.
        $Image->ReadImage("$fileName") 
	    or $Image->ReadImage('xc:white');

    	return ($Image);
    }
}

# -------------------------------------------------------------------
# ---------------------- Adjust Camera Image ------------------------
# -------------------------------------------------------------------
sub adjust_camera_image() {
    my ($cropGeometry,$scale,$gamma,$sharpen,$Image) = @_;

    # Apply image adjustments. Should sharpening be before or 
    # after scaling? (After is quicker, is before better?)
    if ($cropGeometry) {$Image->Crop( geometry=>$cropGeometry )};
    if ($scale) {$Image->Scale( geometry=>$scale )};
    if ($gamma) {$Image->Gamma( gamma=>$gamma );}
    if ($sharpen) {$Image->Sharpen( geometry=>$sharpen )};	
    # radius = 0, sigma = 1 is good.
}

# -------------------------------------------------------------------
# ------------------- Get annotation parameters ---------------------
# -------------------------------------------------------------------
sub get_keywords() {
    my ($param_file, $flightNum, $possible_keywords, $key_hash) = @_;

    # Read parameter file.
    # Lines are in the form of 'parameter_name=value'.
    # End parameters section with "endParameters".

    # The name of the parameters file is the first command line argument.
    -e $param_file or die "Parameters file doesn't exist\n";
    open PARAMETERS_FILE, "<$param_file";

    # Loop through the parameters section of the file.
    while (<PARAMETERS_FILE>)  {	# Read a line from the file
        s/\s//g;			# Remove all white space.
        chomp;			# Remove trailing newline.
        next if /^$/;		# Next line if this one is blank.
        next if /^#/;		# Next line if this one is commented out with #
        last if /^endParameters/ ;	# Exit loop if it contains this string.
        (my $keyword, my $value) = split /=/;	# Split at equal sign.

	# Put keyword into parameter/keys hash
	$key_hash->{$keyword}=$value;

	# Convert #### to flight number
	$key_hash->{$keyword} =~ s/####/$flightNum/; 

    print "$keyword = $key_hash->{$keyword}\n";
	if (!defined $possible_keywords->{$keyword}) {
	    die "Quitting because of unrecognized keyword $keyword in file.\n";
	}

    }

    print "\n\nDone reading parameters file $param_file\n";
    
}

# -------------------------------------------------------------------
# ---------------- Get flight info from header file -----------------
# -------------------------------------------------------------------
sub dump_netcdfFile_header() {
    my $netcdfFile = shift;
    my $headerDump = shift;
    my @tempVar=();

    # Create a new header dump.
    -e $netcdfFile or die "Netcdf file $netcdfFile not found.\n";
    if (system "ncdump -h $netcdfFile > $headerDump") 
	{die "Couldn't create netcdf header dump file $headerDump"};

    # Open the netCDF header dump file and get the project name, flight, and date
    open(HEADER_DUMP_FILE, "$headerDump") 
	|| die "Couldn't open header file $headerDump\n";

    # Read project name from netcdf file if requested
    # match on yes, ignoring case.
    my $projectName;		# Empty string.
    if ($keywords->{includeProjectName} =~ m/yes/i) { 
        seek(HEADER_DUMP_FILE,0,0);
        @tempVar=grep(/:ProjectName =/, <HEADER_DUMP_FILE>);
        ($projectName)=($tempVar[0] =~ /^\s+:ProjectName = "(.*)"/);
    }

    my $projectNumber;	# Empty string.
    if ($keywords->{includeProjectNumber} =~ m/yes/i) { 
        seek(HEADER_DUMP_FILE,0,0);
        @tempVar=grep(/:ProjectNumber =/, <HEADER_DUMP_FILE>);
        ($projectNumber)=($tempVar[0] =~ /^\s+:ProjectNumber = "(.*)"/);
    }


    seek(HEADER_DUMP_FILE,0,0);
    @tempVar=grep(/:FlightNumber =/, <HEADER_DUMP_FILE>);
    (my $flightNumber)=($tempVar[0] =~ /^\s+:FlightNumber = "(.*)"/);

    seek(HEADER_DUMP_FILE,0,0);
    @tempVar=grep(/:TimeInterval =/, <HEADER_DUMP_FILE>);
    (my $timeInterval)=($tempVar[0] =~ /^\s+:TimeInterval = "(.*)"/);
    (my $beginTime,my $endTime) = split('-',$timeInterval);

    seek(HEADER_DUMP_FILE,0,0);
    @tempVar=grep(/:FlightDate =/, <HEADER_DUMP_FILE>);
    (my $flightDate)=($tempVar[0] =~ /^\s+:FlightDate = "(.*)"/);

    my ($mn,$dy,$yr) = split('/',$flightDate);
    my ($emon,$edy,$eyr) = split('/',$flightDate);
    # If endTime < beginTime, then rolled over midnight, so increment end
    # date by one day.
    my ($bhr,$bmn,$bsec) = split(':',$beginTime);
    my ($ehr,$emn,$esec) = split(':',$endTime);
    my $endDate = timegm($esec,$emn,$ehr,$dy,$mn-1,$yr);
    my $beginDate = timegm($bsec,$bmn,$bhr,$dy,$mn-1,$yr);
    if ($endDate < $beginDate) {
	($eyr,$emon,$edy) = 
	    split '-',strftime('%Y-%m-%d',gmtime($endDate+86400));
    }

    my $time_interval = "$yr-$mn-$dy,$beginTime~$eyr-$emon-$edy,$endTime";
    print $time_interval."\n";
    $beginTime =~ s/://g;
    $endTime =~ s/://g;
    my $outputFileTimes = "$yr$mn$dy.${beginTime}_$endTime";

    my $prelim = "\n\n";
    seek(HEADER_DUMP_FILE,0,0);
    if (grep(/PRELIMINARY/, <HEADER_DUMP_FILE>)) {
	$prelim = "\nPRELIMINARY DATA \n";
    }

    # Close header dump file.
    close (HEADER_DUMP_FILE);

    $headerText="$projectName$projectNumber $flightNumber \n$flightDate \n $prelim ";

    print "Flight info retrieved from header of netCDF file  $netcdfFile\n";
    return ($projectNumber,$flightNumber,$time_interval,$headerText,$outputFileTimes);
}

# -------------------------------------------------------------------
# Create n2asc input batch file, clobbering old one if it exists.
# This section copies the variable list from the parameters file
# into the n2asc batch file.
# -------------------------------------------------------------------
sub create_n2asc_batchfile() {
    my ($batchFile,$keywords,$dataFile,$time_interval) = @_;
  open BATCH_FILE, "> $batchFile"  
      or die "Can't open ascii batch file $batchFile\n";
  print BATCH_FILE "if=$keywords->{netcdfFile}\nof=$dataFile\n";
  #print BATCH_FILE "ti=2000-01-01,00:00:00~2008-12-31,23:59:59\n";
  #print BATCH_FILE "ti=$time_interval\n";


  while (<PARAMETERS_FILE>) {
	s/\s//g;				# Remove all white space.
	chomp;					# Remove trailing newline.
	next if /^$/;				# Next line if it's blank.
	last if /endVariables/;		# Exit loop if it contains this string.
	print BATCH_FILE "var=$_\n";
  }
  close BATCH_FILE;
  close PARAMETERS_FILE;	# Done with this file, but don't delete it.

  print "n2asc batch file $batchFile created\n";
}
# -------------------------------------------------------------------
# ---------------------- Create data file ---------------------------
# -------------------------------------------------------------------
sub create_ascii_dataFile() {
    my ($dataFile,$batchFile) = @_;

# Remove old flight data file if it exists, create new one with N2ASC.
-e $dataFile and unlink $dataFile;
print "\n****\nBegin running n2asc -b $batchFile\n";
if (system "nc2asc -b $batchFile") 
	{die "Couldn't create flight data file $dataFile"};
print "\nn2asc completed\n****\n\n";
}

# -------------------------------------------------------------------
# --------------------- Load ascii data file ------------------------
# -------------------------------------------------------------------
# Return a string containing the variable names to write with the data
# to the final images.
sub load_ascii_data() {
  my ($dataFile) = shift;

  # Open the data file created by the n2asc and read the heading.
  open (FLIGHT_DATA_FILE, $dataFile) 
	|| die "\nCouldn't open the data file $dataFile\n";

  # Put the data file into an array variable.
  my @flightData=<FLIGHT_DATA_FILE>;

  # Get the header string from the first line of the data,
  # then split this into variables to write to the image
  my @columnLabels=split(',',shift(@flightData));
  my $theText = '';
  foreach my $label (@columnLabels) { 
	$theText=$theText.sprintf("%s\n",$label);
  }
  #chomp $theText;		# Remove final newline.
  return($theText,@flightData);
}
# -------------------------------------------------------------------
# Create a small (unchanging) image consisting of the variable labels.
# -------------------------------------------------------------------
sub write_vars2labelImage() {
    my ($labelImage,$headerText,$theText,$outputHeight,$outputWidth) = @_;

  @$labelImage = ();
  $labelImage->SetAttribute(size=>"${outputWidth}x$outputHeight");
  $labelImage->ReadImage('xc:none');		# Transparent canvas

  # Header text floats to the top, left of the label image.
  $labelImage->Annotate( font=>$annotationFont, pointsize=>$fontSize,
      weight=>500, gravity=>'NorthWest', fill=>"$fontColor",text=>"$headerText");

  # Parameter names float to the bottom, left of the label image.
  # Parameter values will be added directly across, i.e. bottom, right.
  $labelImage->Annotate( font=>$annotationFont, pointsize=>$fontSize,
      weight=>500, gravity=>'SouthWest', fill=>"$fontColor",text=>"$theText");

  close (FLIGHT_DATA_FILE);		# Don't need the file any longer.

  print "data file $dataFile and base image created\n";
}
