<?php
	//display errors
	ini_set('display_errors', '1');

	//don't let browsers cache this page
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

	//get latest images array from database
	$query = "SELECT latest FROM camera";
	$result = pg_query($query) or die('Query Failed: '. pg_last_error());
	$image = pg_fetch_row($result);

	//use regex to parse individual images from "array" passed back from postgres
	preg_match_all('/\d+\-\d+/', $image[0], $latest);

	//Encode into JSON format and send back to viewer - could use json_encode 
	//			but I need to add '.jpg' to the end of each element anyway
	$i=0;
	echo '{"jsonImgs": [';
	foreach ($latest[0] as $lat) {
		if ($i>0) echo ", ";
		echo "\"$lat.jpg\"";
		$i++;
	}
	echo"]} ";

	//close db connection
	pg_free_result($result);
	pg_close($dbconn);

?>
