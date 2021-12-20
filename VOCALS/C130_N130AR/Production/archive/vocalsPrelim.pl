#!/usr/bin/perl -w
# Processes VOCALS camera images.
# Just intended for preliminary movies.
# Scales, adjusts, and annotates with time.

#Uses ...
use Image::Magick;              # Non-standard ImageMagick extensions.

# Initialization and onstants
$outputResolution = "512x384";
mkdir "./AnnotatedImages";

$inputImage = Image::Magick->new();             # Image read in.

# open current working directory and get file list
opendir(IMAGE_DIRECTORY, ".");
@tempList=grep{/.jpg/} readdir IMAGE_DIRECTORY;
@jpegFiles=sort @tempList;
$numFiles = scalar(@jpegFiles);

printf("Processing %d files\n", $numFiles);

$index = 0;
foreach $fileName (@jpegFiles) { 
	($imageTime=$fileName) =~ s/.jpg//;;

	$newName = sprintf("./AnnotatedImages/%05d.jpg", $index);
	printf("Processing %s, file %d of %d\n", $fileName, $index, $numFiles);
	@$inputImage = ();
	$inputImage->ReadImage("./$fileName");
#	Sharpen image. '0.0x1.0' is usual. This is best done before down-sampling.
	$inputImage->Sharpen(geometry=>'0.0x1.0');
#	Reduce resolution.
	$inputImage->Sample(geometry=>$outputResolution);
#	Annotate and save.
	$inputImage->Annotate(gravity=>'SouthWest', font=>"Helvetica-Bold", undercolor=>'grey85', pointsize=>12, text=>$imageTime);
	$inputImage->Write(quality=>90,  filename=>$newName);
	$index++;
}

