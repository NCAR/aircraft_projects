<?php 
	if (isset($_GET['kmz'])) {
		echo ltrim($kml = shell_exec('unzip -pqqa ' . $_GET['kmz']));
	}
?>

