<?php
	/* Set the time (in seconds) that must elapse before
	   this script will allow a new image to be sent to 
	   the ground :                                     */
	$MIN_TIME = 30;

	$timefile = "last_sent.timestamp";

	if (isset($_GET['override'])) {
		send();
		
		echo "<b style='color:green'>Image sent </b>" . 
		"-<i> override</i>^^" .
		'<p><span class="ui-icon ui-icon-check" ' . 
		'style="float:left; margin:0 7px 10px 0;"></span>' .
		'OK</p>';

		exit ();
	}
		
	$last_send = fileatime($timefile);
	$current = time();
	$age = $current - $last_send;

	$tooFast = file_exists($timefile) && $age < $MIN_TIME;

	if (!$tooFast) send(); 

	echo $tooFast? "0^^<b style='color:red' >Image not sent</b>^^" . 
		'<p><span class="ui-icon ui-icon-alert" ' .
		'style="float:left; margin:0 7px 10px 0;"></span>' .
		"You should wait at least <b>$MIN_TIME</b>" . 
		 " seconds between sending images.</p>" :

		"1^^<b style='color:green'>Image sent</b>^^" .
		'<p><span class="ui-icon ui-icon-circle-check" ' . 
		'style="float:left; margin:0 7px 10px 0;"></span>' .
		'OK</p>';


	echo "<p>(previous image was sent <b>$age</b> seconds ago.)</p>";

	function send() {
		global $timefile;

		touch($timefile);
		shell_exec("/home/local/Systems/scrips/send_camera.cron");
	
		return;
	}
?>
