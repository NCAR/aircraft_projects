<?php
	//don't let browswer cache this page
	if (isset($_SERVER['HTTP_USER_AGENT']) && (strpos($_SERVER['HTTP_USER_AGENT'], 'MSIE') !== false)) { header('Cache-Control: no-cache'); header('Expires: -1'); }
	else { header('Cache-Control: no-cache, must-revalidate'); header('Expires: Sat, 26 Jul 1997 05:00:00 GMT'); }
	
	$host = $_GET['hostname'];
	$retval['tag'] = $_GET['tag'];

	//ping host from shell, parse output
	$result = shell_exec("ping -c 1 $host");
	preg_match_all('/, (\d+)% packet loss/', $result, $out);

	//check for report 
	if (count($out[1])) {
		//check % packet loss
		if ($out[1][0] == "0"){
			$retval['status'] = 0;
			$retval['message'] = "Alive";
		} else {
			$retval['status'] = 2;
			$retval['message'] = "Timed Out";
		}
	} else {
	//if none, then the host was not resolved
		$retval['status'] = 1;
		$retval['message'] = "Unknown Host";
	}
	

	echo json_encode($retval);

?>
