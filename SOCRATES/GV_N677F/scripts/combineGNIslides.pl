#!/usr/bin/perl -w
use strict;

# Stuart Beaton, NCAR/RAF

# Generates an annotated MPEG-4 video from a directory of images 
# Reads a parameter file specified on the command line to
# get the netcdf file, image directory, variables, etc.

# 2018 Oct 19 - JAA
# Derived from combineCamera.pl
# ------------------------------------------------------------------------------
# Files used:
#	parameters file specified on command line.
#
# names hardcoded in Initialization section:
#	$annotatedImageDirectory - dir to dump annotated images (images
#	containing image count overlay)
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

# Set defaults for variables
my $annotationFont = "Courier-Bold";
my $fontSize = "13";
my $fontColor = "black";
my $startNum = -1;

# List possible keywords for use in ParamFile
my %possible_keywords = ( # value = description, default
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
    "numCameras" => ("default = 1"),
);

my @flightData;
my $theText;
my $outputHeight;
my $outputWidth;
my ($projectNumber,$flightNumber,$time_interval,$headerText);
# -------------------------------------------------------------------
# ----------------------------- Usage -------------------------------
# -------------------------------------------------------------------
#if no arguments or argument is "-h", print help text and exit.
if ( (scalar(@ARGV) < 1) || (scalar(@ARGV) > 2)  || ($ARGV[0] eq "-h") ) {
	print "\n Perl script to generate annotated movies from images\n";
	print " USAGE: $0  parameterFileName  [startnum]\n";
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

&get_keywords($ARGV[0],$keyref,$keywords);

# -------------------------------------------------------------------
# Defaults for various cameras if not set in parameters file.
# -------------------------------------------------------------------
if (!$keywords->{numCameras}) {$keywords->{numCameras} = 1;}
if (!$keywords->{overlayImageTime}) {$keywords->{overlayImageTime}="no";}
if (!$keywords->{outputWidth}) {$keywords->{outputWidth}=200;}

# -------------------------------------------------------------------
# ----------------------- Load image list ---------------------------
# -------------------------------------------------------------------

# Open the directory and read the list of JPEG files into @jpegFiles array.
opendir(IMAGE_DIRECTORY, "$keywords->{imageDir1}") 
	|| die "Image directory $keywords->{imageDir1} not found";
my @tempList = grep{/.png/} readdir IMAGE_DIRECTORY;
closedir IMAGE_DIRECTORY;

# sort by filename which is the image time. 
# Alternative would be to search the entire list for each second of data.
# (Should see how much additional time that would add.)
my @jpegFiles=sort @tempList;
my $numFiles = scalar(@jpegFiles);
print "Number of images to process = $numFiles\n";

# Set the output dir for annotated images and final movies
!$keywords->{movieDirectory} 
    and die "movieDirectory must be identified in the parameters file! \n";

$annotatedImageDirectory = 
    $keywords->{movieDirectory}."/AnnotatedImages";
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

#unlink $batchFile;
#unlink $headerDump;
#unlink $dataFile;

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
	@$valueImage = ();
	
	# Size output image with white background (canvas).
	$outputImage->Set(size=>$keywords->{outputResolution}, quality=>100);
	$outputImage->ReadImage('xc:white');	# White canvas

	my $gravity;
	if ($keywords->{numCameras} > 4) {
	    print "Code only handles up to four cameras. Update code!\n";
	    exit(1);
	}
        if ($keywords->{gravity1}) {
	    $gravity = $keywords->{gravity1}
	} else {
	    if ($keywords->{numCameras} == 1) {$gravity = 'NorthWest'};
	}
	
	# Get image time so can later pull flight data for this time from data
	# file.
	# - The last 6 characters of the filename before the .png is the time of
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

	print "image $fileNum/$numFiles: $fileName $imageTime\n";

	# Now process the cameras.
	my $addtl_cameras = 1;
	while ($addtl_cameras <= $keywords->{numCameras}) {
            my $Directory = $keywords->{"imageDir$addtl_cameras"};
	    $Image = &get_camera_image($Directory, $fileName);
	    #&adjust_camera_image($keywords->{crop},$keywords->{scale},
	    #    $keywords->{gamma},$keywords->{sharpen},$Image);
	    $gravity = $keywords->{"gravity$addtl_cameras"}; 
	        
	    if ($keywords->{overlayImageTime} eq "yes") {
	        my $imageDateTime = $fileName;
	        $imageDateTime =~ s/.png//;
	        $Image->Annotate(gravity=>'SouthWest', font=>"Helvetica-Bold",
	            undercolor=>'grey85', pointsize=>24, text=>$imageDateTime);
	    }

	    $outputImage->Composite( image=>$Image, gravity=>$gravity);
	    @$Image = ();

	    $addtl_cameras += 1;
	}


	# Determine the output image filename.
	my $outputImageName=
	    sprintf('%s/%05d.png',$annotatedImageDirectory,$fileNum);

	# write out the image.
	$outputImage->write($outputImageName);
}


# --------------------------------------------------------------------
#----------------------- Two pass MPEG encoding ----------------------
# --------------------------------------------------------------------
my $outputFrameRate = $keywords->{outputFrameRate};;
my $mp4BitRate = $keywords->{mp4BitRate};;

my $outputFilename = "gni_movie.mp4";
my $command = "/usr/bin/ffmpeg -i $annotatedImageDirectory/%05d.png -pix_fmt yuv420p -b:v $mp4BitRate -y  ".$keywords->{movieDirectory}."/$outputFilename";
print "$command\n";
if (system "$command") { die "Unable to create MPEG file $outputFilename, using command $command"}; 


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

    if ($fileName !~ /[0-9][0-9][0-9][0-9][0-9].png/) {
	print "Filename $Directory/$fileName doesn't match ".
	    "expected pattern: *HHMMSS.png\n";
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
	    $fileName =~ s/.png/_?.png/;
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
    my ($param_file, $possible_keywords, $key_hash) = @_;

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

    print "$keyword = $key_hash->{$keyword}\n";
	if (!defined $possible_keywords->{$keyword}) {
	    die "Quitting because of unrecognized keyword $keyword in file.\n";
	}

    }

    print "\n\nDone reading parameters file $param_file\n";
    
}
