<?php
	//display errors
	ini_set('display_errors','1');

    //make sure that browsers do not cache this page
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

	//get the hostname of the camserver which is updating the database 
	//		This is used by the viewer to send start/stop requests to
	//		camserver instead of the webserver
	$query = "SELECT cam_host FROM camera";
	$result = pg_query($query) or die('Query Failed: '. pg_last_error());
	$chost = pg_fetch_row($result);

	//get the flight number from the database
	$query = "SELECT value FROM global_attributes WHERE key='FlightNumber'";
	$result = pg_query($query) or die('Query Failed: '. pg_last_error());
	$flNum = str_replace(" ","",pg_fetch_array($result));

	//get and format the current date/time
	$UTCdate = gmdate("U", time()) * 1000;

	//put all data in an array, pack into JSON and return it to the viewer
	$a = array('chost'=>$chost[0], 'curFlNum'=>$flNum[0], 'datetime'=>$UTCdate);
	echo json_encode($a);

	//close the database connection
	pg_free_result($result);
	pg_close($dbconn);

?>
