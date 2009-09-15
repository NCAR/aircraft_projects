<?php
	//display errors
	ini_set('display_errors','1');

	//sort function - 'left' is low, 'right' is high, everything else goes in the middle
	function std_order($a, $b) { return ($a=="left"?-1: ($a=="right"?1: ($b=="left"?1:-1))); }

	//make sure browser does not cache this page
	if (isset($_SERVER['HTTP_USER_AGENT']) && (strpos($_SERVER['HTTP_USER_AGENT'], 'MSIE') !== false)) {
	  # This is for Internet Explorer, the browser that doesn't listen to HTTP standards.
	  header('Cache-Control: no-cache');
	  header('Expires: -1');
	}
	else {
	  # This is for everyone else that listens to HTTP standards; like FireFox, Opera, and Chrome.
	  header('Cache-Control: no-cache, must-revalidate'); // HTTP/1.1
	  header('Expires: Sat, 26 Jul 1997 05:00:00 GMT'); // Date in the past
	}

	//connect to database, using env vars
	$dbh = getenv('PGHOST');
	$dbU = getenv('PGUSER');
	$dbd = getenv('PGDATABASE');
	$dbconn = pg_connect("host=$dbh dbname=$dbd user=$dbU")
		or die('Could not connect: '.pg_last_error());

	//get directions from camera
	$query = "SELECT direction FROM camera";
	$result = pg_fetch_row(pg_query($query)) or die('Query Failed: '. pg_last_error());

	//parse array using regex, to get each individual direction
	preg_match('/\{(.+)\}/', $result[0], $direc);
	$directions = explode(',', $direc[1]);

	//output a checkbox for each camera, with label and alt tag. Default the first
	//checkbox to checked, others unchecked
	$count = 1;
	usort($directions, "std_order");
	foreach ($directions as $dir) {
		echo '<input type="checkbox" id="showCam'.$count.'" class="camCheck" alt="'.$dir.'"' ;
		if (isset($_GET[$dir])) echo " checked";
		echo ' onClick="autoscaler();" /><label for="showCam' . $count . '">' . $dir . "</label><br />\n";
		$count++;
	}

	//close db connection
	pg_close($dbconn);

?>

