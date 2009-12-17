#!/usr/bin/perl -T

use strict;
use File::stat;
use File::Basename;
use DirHandle;
use CGI;

our $q; our %plat_vars;
require "./getCookie.pl";

# get the name paramter from GET
my $name = $q->param('name');

# check to make sure the name parameter was defined
if ($name != defined) {
	print "need to specifiy an image: i.e. '?name=vis'";
	exit;
}

# Do not allow dangerous chars
if ( $name =~ /\.\./ || $name !~ /^[-\w\s\.]+$/) {
	print "Invalid image specifier, use expression i.e. ?name=vis";
	exit;
}

# get array of images that match the name provided by GET
my $dir = $plat_vars{'docs_path'}."images/";
my %files = get_Files($dir, $name);

# Set up basic html text, including jQuery js lib and our style.css file
print <<endHTML;
<html>
	<head>
		<meta http-equiv="refresh" content="900" >
		<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
		<title>Sat Image</title>
		<script type="text/javascript" src="$plat_vars{jquery}"></script>
		<script type="text/javascript" src="$plat_vars{jqueryui}"></script>
		<link type="text/css" href="$plat_vars{jquerycss}" rel="stylesheet" />	
		<link type="text/css" href="$plat_vars{base_path}css/images.css" rel="stylesheet" />

		<script type="text/javascript">
var playing=false, loopid=0;
endHTML

# create js arrays to hold image src and their last modified date in string form
print "var imgs = new Array();\n";
print "var img_dates = new Array();\n";

# sort images by modified date, fill in js array with data.
my $i = 0;
foreach my $keys (sort{$files{$a} <=> $files{$b}} keys %files) {
	print "imgs[$i] = '". basename($keys) . "';\n";
	print "img_dates[$i] = '" . scalar localtime($files{$keys}) . "';\n";
	$i++;
}	

my $message="";
if ($i == 0) { $message = "<br/>No Images Found matching: $name";}

my $numimgs;
if ($i <= 1) { $numimgs = 0; }
else { $numimgs = $i - 1 }

# finish printing html for webpage
print <<endHTML;
function slide(dist) {
	var curval = \$('#slider').slider('value') + dist;
	if (curval > 0 ) {curval = -$numimgs;}
	else if (curval < -$numimgs) {curval = 0;}
	
	\$('#slider').slider('value', curval ); 
	var newimg = "$plat_vars{href_path}images/" + imgs[$numimgs+curval];
	\$('#imgname').text(img_dates[$numimgs+ \$('#slider').slider('value') ]);
	\$('#curimg').attr("src", newimg);

	return curval;
}
function looper() {
	if (playing) { 
		var curval = 0;
		var delay = \$('#speedSlider').slider('option', 'value');
		curval = slide(1); 
	}
	setTimeout("looper()", delay * (curval ? 1 : 5));
}
\$(function(){

	\$('.ui-corner-all').css("cursor", "pointer");
	\$('.ui-corner-all').hover(
		function() { \$(this).addClass('ui-state-hover'); }, 
		function() { \$(this).removeClass('ui-state-hover'); }
	);

	\$('#slider').slider({
		min:  (-1 * $numimgs),
		max:  0,
		step: 1,
		slide: function(event, ui) {
			var newimg = "$plat_vars{href_path}images/" + imgs[$numimgs+ui.value];
			\$('#imgname').text(img_dates[$numimgs+ui.value]);
			\$('#curimg').attr("src", newimg);
		}
	});
	\$('#speedSlider').slider({
		min:  50,
		max:  500,
		step: 5,
		slide: function(event, ui) { \$('#speed').text(ui.value+" ms"); },
		stop: function(event, ui) { \$('#speed').text("Playback Delay"); }
	});

	\$('#play').click(function() {
		if (playing) {
			\$("#play").text("play");
			playing = false;
		} else {
			\$("#play").text("pause");
			playing = true;
		}
	});

	\$('#fitImg').click(function() {
		if (\$('#fitImg').is(':checked')) {
			\$('#curimg').addClass("autofit");
		} else {
			\$('#curimg').removeClass("autofit");
		}	
	});
	
	\$('#imgname').text(img_dates[$numimgs+ \$('#slider').slider('value') ]);

	\$('#speedSlider').slider('option', 'value', 500);
	\$('#curimg').attr("src", "$plat_vars{href_path}images/"+imgs[0]);
	looper();
});
		</script>

	</head>

	<body>

		<div style="z: 1; position:absolute; right: 1.5em; top: .5em; width: 150px;">
			<form action="" class="greyBox">
<!--				<input  type="checkbox" id="fit" checked /><label for="fit">Fit to browser</label>-->
				<p>
				<button type="button" class="ui-state-default ui-corner-all" onclick="slide(-1)">&laquo</button>
				<button type="button" class="ui-state-default ui-corner-all" id="play">play</button>
				<button type="button" class="ui-state-default ui-corner-all" onclick="slide(1)">&raquo</button>
				</p> <p style="margin-top:15px;">
				<div id="speedSlider"></div>
				<!--<input type="text" id="upspeed" size='7' value="150"/> ms-->
				<span id="speed">Playback Delay</span>
				</p> <p>
				<label><input type="checkbox" id="fitImg" />Auto-Fit</label>
				</p>
			</form>
		</div>
		<div style="min-width: 680px; margin-right: auto; margin-left: auto; text-align: center;">
			<img id="curimg" src="" style="min-height:300px;"/>
			<strong>$message</strong>
		</div>
		<div style="z: 1; " id="sliderbox"><div id="slider"></div></div>
		<p style="margin-top:1em; float: right;">Upload Date: <span id="imgname"></span></p>
	</body>
</html>
endHTML

# function that gets all the files in a directory that match the $name input
sub get_Files {
	my ($dir,$name) = @_; 

	if ( ! -e $dir) {
		print "can't access $plat_vars{'platform'}/images directory";
		exit;
	}
	my $dh = DirHandle->new($dir); #die "can't opendir $dir: $!";
	return  map {$_ => (stat($_)->mtime)} map  { "$dir$_" } grep { m/$name/i } $dh->read();
}
