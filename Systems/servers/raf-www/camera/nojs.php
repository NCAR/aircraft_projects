<?php
	//write out errors 
	ini_set('display_errors', '1');

	//make sure that browser does not cache this page
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


	//connect to db using host,user,and dbname from env vars (set in php.conf)
	$dbh = getenv('PGHOST');
	$dbU = getenv('PGUSER');
	$dbd = getenv('PGDATABASE');
	$dbconn = pg_connect("host=$dbh dbname=$dbd user=$dbU")
		or die('Could not connect: '.pg_last_error());

	//set refresh rate from GET (or default to every 5 seconds)
	$rate = 5;
	if (isset($_GET['refresh'])) $rate = $_GET['refresh'];
	echo "<meta http-equiv=\"refresh\" content=\"$rate\" >"; 

	//get flight number from global_attributes table
	$query = "SELECT value FROM global_attributes WHERE key='FlightNumber'";
	$result = pg_query($query) or die('Query Failed: '. pg_last_error());
	$flNum = str_replace(' ', '', pg_fetch_result($result, 0, 0));

	//get camera data from camera table
	$query = "SELECT status,message,direction,latest FROM camera";
	$result = pg_query($query) or die('Query Failed: '. pg_last_error());
	$camDB = pg_fetch_row($result, NULL, PGSQL_ASSOC);
	
	//display the message, color coding by status
	if ($camDB['status']) {
		echo "<strong style=\"color: green\">";
	} else {
		echo "<strong style=\"color: red\">";
	}
	echo $camDB['message'] . "</strong><br />\n";

	//use regex to parse out each image name from the "array" returned by posgres
	preg_match_all('/\d+\-\d+/', $camDB['latest'], $latest);
	$latest = $latest[0];

	//use regex to parse out each direction from the "array" returned by posgres
	preg_match('/\{(.+)\}/', $camDB['direction'], $direc);
	$directions = explode(',', $direc[1]);

	//build url to display each image on the page
	$i = 0;
	foreach ($directions as $dir) {
		echo "<img src='http://lenado/camera/flight_number_$flNum/$dir/$latest[$i].jpg' ";
		if (isset($_GET['scale'])) echo "width= ".$_GET['scale'];
		echo " />\n";
		$i++;
	}

	//close up the database connection
	pg_free_result($result);
	pg_close($dbconn);

?>
