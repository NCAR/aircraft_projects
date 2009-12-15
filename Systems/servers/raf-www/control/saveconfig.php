<?php

	if ( isset($_POST['conf']) ) {
		$bytes = file_put_contents("js/config.json", $_POST['conf']);
		echo $bytes > 0? "0": "1";
	} else {
		echo "2";
	}
	
?>

