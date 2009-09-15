<?php
	//display errors
	ini_set('display_errors','1');

	//don't let browswer cache this page
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

	//connect to db, using env vars
	$dbh = getenv('PGHOST');
	$dbU = getenv('PGUSER');
	$dbd = getenv('PGDATABASE');
	$dbconn = pg_connect("host=$dbh dbname=$dbd user=$dbU")
		or die('Could not connect: '.pg_last_error());

	//get status(numeric status) and message(human readable status) from camera table
	$query = "SELECT status,message FROM camera";
	$result = pg_query($query) or die('Query Failed: '. pg_last_error());
	$status = pg_fetch_row($result);	

	//display message, color coding by value of status
	if ($status[0] == "1") {
		echo "<strong style=\"color: green\">";
	} else {
		echo "<strong style=\"color: red\">";
	}
	echo "$status[1]</strong><div id='camPGstatus' style=\"display:none\">{$status[0]}</div>";

	//close db connection
	pg_free_result($result);
	pg_close($dbconn);

?>
