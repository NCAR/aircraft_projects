<?php
	//don't let browswer cache this page
	if (isset($_SERVER['HTTP_USER_AGENT']) && (strpos($_SERVER['HTTP_USER_AGENT'], 'MSIE') !== false)) { header('Cache-Control: no-cache'); header('Expires: -1'); }
	else { header('Cache-Control: no-cache, must-revalidate'); header('Expires: Sat, 26 Jul 1997 05:00:00 GMT'); }
	
	//call the correct function based on command passed by GET method
	switch ($_GET['command']) {
		case 'reboot':
			rebooter($_GET['hostname']);
			break;
		case 'ping':
			pinger($_GET['hostname']);
			break;
		case 'Cameras':
			capture($_GET['action']);
			break;
		case 'Nimbus':
			nimbus($_GET['action']);
			break;
		case 'SATCOM-MPDS':
			satcom_mpds($_GET['action']);
			break;
		case 'DSM-Server':
			dsmserver($_GET['action']);
			break;
		default:
			exit('unrecoginzed or null command');
	}

function launch($name, $comm) {
	//Fire up a gnome-terminal on server's local display with
	//	title=$name and profile=$_GET['profile'], and 
	//	launch $comm as the shell command

	$display = ":0.0";	
	$profile = isset($_GET['profile'])? "--window-with-profile=".$_GET['profile']: "";
	$launch = "gnome-terminal --display=$display $profile -t \"$name\" -x $comm &> /dev/null &";

	return shell_exec($launch);
}

function capture($action) {
	//call php script on camserver and pass it the command as an argument
	$captureURL = 'http://accam/camera/capture.php';
	echo file_get_contents("$captureURL?$action=1");
}

function nimbus($action) {
	switch ($action) {
		case 'start':
			launch('Nimbus', '/home/local/Systems/scripts/launch_nimbus_rt');
			break;
		case 'stop':
			launch("Quit Nimbus", "killall -v nimbus");
			break;
		default:
			exit("unrecognized nimbus command");
	}
}

function dsmserver($action) {
	switch ($action) {
		case 'start':
			launch('DSM-Server', '/home/ads/bin/start_data_acq');
			break;
		case 'stop':
			launch('Quit DSM-Server', '/home/ads/bin/stop_data_acq');
			break;
		default:
			exit("unrecognized DSM-Server command");
	}
}

function satcom_mpds($action) {
	switch ($action) {
		case 'start':
			launch("Start MPDS", "/sbin/ifup mpds");
			break;
		case 'stop':
			launch("Stop MPDS", "/sbin/ifdown mpds");
			break;
		default:
			exit("unrecognized satcom command");
	}
}

function rebooter($host) {
	//ssh into the $host and issue the reboot command
	launch("SSH Reboot $host", "ssh -f ads@$host reboot");
}

function pinger($host) {

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
}

?>
