<?php
	// COPYRIGHT: University Corporation for Atmospheric Research, 2009-12

	//don't let browswer cache this page
	if (isset($_SERVER['HTTP_USER_AGENT']) && (strpos($_SERVER['HTTP_USER_AGENT'], 'MSIE') !== false)) { header('Cache-Control: no-cache'); header('Expires: -1'); }
	else { header('Cache-Control: no-cache, must-revalidate'); header('Expires: Sat, 26 Jul 1997 05:00:00 GMT'); }

	//open nagios status file
	$statusdat = file_get_contents('/var/log/nagios/status.dat');

	//regex parse out description, state, and output into $out array
	preg_match_all('/service \{[.\S\s][^\}]+service_description=(.*)\n[.\S\s][^\}]+current_state=(.*)\n[.\S\s][^\}]+plugin_output=(.*)\n/', $statusdat, $out);

	//reformat array to make more sense
	for ($i=0; $i<count($out[1]); $i++) {
		//only send items with Warning or critical status
		if ($out[2][$i] > 0) {
			$status['status']["{$out[1][$i]}"] = $out[2][$i];
			$status['message']["{$out[1][$i]}"] = $out[3][$i];
		}
	}

	//encode as json and return array
	echo json_encode($status);
?>
