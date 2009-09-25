
<html>
<head>
</head>
<?php
	if (isset($_GET['vertical'])) {
		echo "<frameset border=\"1\" cols=\"30%,*\">";
		echo "<frame src=\"../camera/nojs.php?width=90%\">";
	} else {
		echo "<frameset border=\"1\" rows=\"30%,*\">";
		echo "<frame src=\"../camera/nojs.php?height=90%\">";
	}
?>
<frame src="../osm/index.html">
</frameset>
</html>

