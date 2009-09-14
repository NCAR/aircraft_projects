<?php
	//don't let browswer cache this page
	if (isset($_SERVER['HTTP_USER_AGENT']) && (strpos($_SERVER['HTTP_USER_AGENT'], 'MSIE') !== false)) { header('Cache-Control: no-cache'); header('Expires: -1'); }
	else { header('Cache-Control: no-cache, must-revalidate'); header('Expires: Sat, 26 Jul 1997 05:00:00 GMT'); }

	//open nagios status file
	$statusdat = file_get_contents('/var/log/nagios/status.dat');
	
	//regex parse out description, state, and output into $out array
	preg_match_all('/service \{[.\S\s][^\}]+service_description=(.*)\n[.\S\s][^\}]+current_state=(.*)\n[.\S\s][^\}]+plugin_output=(.*)\n/', $statusdat, $out);
	
	$size = strpos($_SERVER['HTTP_USER_AGENT'],"iPhone")? '300%' : '80%';

	echo '<h1>'.date("H:i, m.d.y").'</h1>';

	echo '<table cellpadding=10 border=3 style="font-size:'.$size.'">';

	//reformat array to make more sense
	$colors = array(0=>"#00FF00", 1=>"#FFF000", 2=>"#FF0000");
	for ($i=0; $i<count($out[1]); $i++) {
		$status['status']["{$out[1][$i]}"] = $out[2][$i];
		$status['message']["{$out[1][$i]}"] = $out[3][$i];

		echo '<td style="background:' . $colors[$out[2][$i]] . ';" >';
		echo $out[1][$i]."</td><td>".$out[3][$i];
		echo "</td></tr>\n";
	}

	echo '</table>';

?>
