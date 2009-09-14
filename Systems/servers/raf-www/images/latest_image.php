<?php 
	if (! isset($_GET['name'])) exit("need to specifiy an image: i.e. '?name=vis'");
?>
<html>
	<head>
		<meta http-equiv="refresh" content="900" >
		<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
		<title>Sat Image</title>
		<link type="text/css" href="../camera/css/smoothness/jquery-ui-1.7.1.custom.css" rel="stylesheet" />	
		<link type="text/css" href="../camera/css/style.css" rel="stylesheet" />	

		<script type="text/javascript" src="../camera/js/jquery-1.3.2.min.js"></script>
		<script type="text/javascript" src="../camera/js/jquery-ui-1.7.1.custom.min.js"></script>

		<script type="text/javascript">
var playing=false, loopid=0;
<?php
	/* get array of images in order of last mod date */
	$dir = "/var/www/html/images";
	$satimgname = $_GET['name'];
	$dirg = glob("./*$satimgname"); // put all files in an array
	array_multisort( array_map( 'filemtime', $dirg ), SORT_NUMERIC, SORT_ASC, $dirg);
	$numimgs = count($dirg) ? count($dirg)-1 : 0;

	echo "var imgs = new Array();\n";
	echo "var img_dates = new Array();\n";
	foreach($dirg as $filenum => $filename) {
		echo "imgs[$filenum] = '$filename';\n";
		echo "img_dates[$filenum] = '".date("m/d/Y H:i:s",filemtime($filename))."';\n";
	}	
?>

function slide(dist) {
	var curval = $('#slider').slider('value') + dist;
	if (curval > 0 ) {curval = -<?php echo $numimgs ?> ;}
	else if (curval < -<?php echo $numimgs ?> ) {curval = 0;}
	
	$('#slider').slider('value', curval ); 
	var newimg = imgs[<?php echo $numimgs ?>+curval];
	$('#imgname').text(img_dates[<?php echo $numimgs ?>+ $('#slider').slider('value') ]);
	$('#curimg').attr("src", newimg);

	return curval;
}
function looper() {
	if (playing) { 
		var curval = 0;
		var delay = $('#speedSlider').slider('option', 'value');
		curval = slide(1); 
	}
	setTimeout("looper()", delay * (curval ? 1 : 5));
}
$(function(){

	$('.ui-corner-all').css("cursor", "pointer");
	$('.ui-corner-all').hover(
		function() { $(this).addClass('ui-state-hover'); }, 
		function() { $(this).removeClass('ui-state-hover'); }
	);

	$('#slider').slider({
		min:  <?php echo (-1 * $numimgs) ?>,
		max:  0,
		step: 1,
		slide: function(event, ui) {
			var newimg = imgs[<?php echo $numimgs ?>+ui.value];
			$('#imgname').text(img_dates[<?php echo $numimgs ?>+ui.value]);
			$('#curimg').attr("src", newimg);
		}
	});
	$('#speedSlider').slider({
		min:  50,
		max:  500,
		step: 5,
		slide: function(event, ui) { $('#speed').text(ui.value+" ms"); },
		stop: function(event, ui) { $('#speed').text("Playback Delay"); }
	});

	$('#play').click(function() {
		if (playing) {
			$("#play").text("play");
			playing = false;
		} else {
			$("#play").text("pause");
			playing = true;
		}
	});

	$('#fit').click(function() {
		if ($('#fit').attr('checked')) {
			$('#curimg').height("80%");
		} else {
			$('#curimg').height("");
		}	
	});
	
	$('#imgname').text(img_dates[<?php echo $numimgs ?>+ $('#slider').slider('value') ]);

	$('#speedSlider').slider('option', 'value', 150);
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
				</p>
			</form>
		</div>
		<div style="min-width: 680px; margin-right: auto; margin-left: auto; text-align: center;">
			<img id="curimg" src="<?php echo $dirg[$numimgs] ?>" />
		</div>
		<div class="clear"></div>
		<div id="sliderbox"><div id="slider"></div></div>
		<p style="margin-top:1em; float: right;"><span id="imgname"></span></p>
	</body>
</html>
