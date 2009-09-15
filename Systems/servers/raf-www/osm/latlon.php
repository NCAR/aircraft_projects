<?php
	ini_set('display_errors','1');
	
	//connect to db, using env vars
	$dbh = getenv('PGHOST');
	$dbU = getenv('PGUSER');
	$dbd = getenv('PGDATABASE');
	$dbconn = pg_connect("host=$dbh dbname=$dbd user=$dbU")
		or die('Could not connect: '.pg_last_error());
  
  /* get the EndTime value from DB */
	$query = "SELECT value FROM global_attributes WHERE key='EndTime'";
	$result = pg_query($query) or die('Query Failed: '. pg_last_error());
	$line = pg_fetch_row($result);
	$datetime = substr_replace(str_replace(" ","",$line[0]), "", -4, 4);
  
  /* get latest alt/lat/lon/heading using EndTime from above */
	$query = "SELECT ggalt,gglat,gglon,thdg FROM raf_lrt WHERE datetime='$datetime'";
	$result = pg_query($query) or die('Query Failed: '. pg_last_error());

  /* get heading to nearst 5 degrees */
	$line = pg_fetch_array($result);
	$iHeading = abs((round($line['thdg'] + 2.5)) % 360); 
	$heading =  $iHeading - ($iHeading  % 5);
  
  /* calculate magnetic declination using International Geomagnetic 
  	Reference Field Model program */
	$decDM = explode("\n", shell_exec("./getDec.bin IGRF10.unx ".date("Y,m,d")." D F{$line['ggalt']} {$line['gglat']} {$line['gglon']} | egrep -o \".[0-9]+[dm]\" | head -n 2 | egrep -o \"\-?[0-9]+\""));
	$decDD = $decDM[0] < 0 ? $decDM[0] - ($decDM[1] / 60) : $decDM[0] + ($decDM[1] / 60);

	echo json_encode(array("lon"=>$line['gglon'], "lat"=>$line['gglat'], "head"=>$heading, "declination"=>$decDD, "alt"=>$line['ggalt'] ));

  /* close the database connection */
	pg_free_result($result);
	pg_close($dbconn);
?>
