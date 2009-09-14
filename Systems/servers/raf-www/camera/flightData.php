<?php
	//display errors
	ini_set('display_errors','1');

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

	//connect to db, using env vars	
	$dbh = getenv('PGHOST');
	$dbU = getenv('PGUSER');
	$dbd = getenv('PGDATABASE');
	$dbconn = pg_connect("host=$dbh dbname=$dbd user=$dbU")
		or die('Could not connect: '.pg_last_error());

	//get units from db, build units[] array
//	$query = "SELECT units FROM variable_list WHERE name IN ('PITCH', 'THDG', 'TASX', 'ATX', 'PALTF') ORDER BY name";
	$query = "SELECT units FROM variable_list WHERE name IN ('PITCH', 'THDG') ORDER BY name";
	$result = pg_query($query) or die('Query Failed: '. pg_last_error());
	$line = pg_fetch_all($result);
	foreach ($line as $nuPair) {
		foreach ($nuPair as $unit) {
			$units[] = $unit;
		}
	}	

	//get endTime (latest update) from db
	$query = "SELECT value FROM global_attributes WHERE key='EndTime'";
	$result = pg_query($query) or die('Query Failed: '. pg_last_error());
	$line = pg_fetch_row($result);
	$datetime = substr_replace(str_replace(" ","",$line[0]), "", -4, 4);	

	//get latest values of selected variables
//	$query = "SELECT ATX,PALTF,PITCH,TASX,THDG FROM raf_lrt WHERE datetime='$datetime'";
	$query = "SELECT PITCH,THDG FROM raf_lrt WHERE datetime='$datetime'";
	$result = pg_query($query) or die('Query Failed: '. pg_last_error());

	//Echo nicely formatted values, with labels and units
	$count = 0;
	while ($line = pg_fetch_array($result, NULL, PGSQL_ASSOC)) {
		foreach ($line as $name => $col_val) {
//			echo "<p><span class='fdName' >$name:</span><br />\n<span class='fdValue'>" . $col_val . "</span> <span class='units' >" . str_replace(" ","",$units[$count]) . " </span></p>\n";
			echo "<span class='fdName' >$name:</span><span class='fdValue'>" . $col_val . "</span> <span class='units' >" . str_replace(" ","",$units[$count]) . " </span> &nbsp &nbsp &nbsp &nbsp ";
			$count++;
		}
	}

	//close db connection
	pg_free_result($result);
	pg_close($dbconn);

?>
