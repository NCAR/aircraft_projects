<?php

	//include utils file for xmlrpc functions
	include_once('utils.php');

	//don't let browswer cache this page
	if (isset($_SERVER['HTTP_USER_AGENT']) && (strpos($_SERVER['HTTP_USER_AGENT'], 'MSIE') !== false)) { header('Cache-Control: no-cache'); header('Expires: -1'); }
	else { header('Cache-Control: no-cache, must-revalidate'); header('Expires: Sat, 26 Jul 1997 05:00:00 GMT'); }

	// get vars from HTTP 'GET' args if possible, otherwise use default
	$host = isset($_GET['host']) ? $_GET['host'] : 'localhost' ;
	$port = isset($_GET['port']) ? $_GET['port'] : 30003 ;
	$method = isset($_GET['method']) ? $_GET['method'] : 'GetDsmList' ;
	$args = isset($_GET['args']) ? $_GET['args'] : null ;

	//send request to status-listener
	$rpcArray = xu_rpc_http_concise( array( 'method' => $method,
                                       'args'   => $args,
                                       'host'   => $host,
                                       'uri'    => '/RPC2',
                                       'port'   => $port,
                                       'debug'  =>  '0',
                                       'output' => 'xmlrpc' ));

	//encode as json and return array
	$j = json_encode($rpcArray);
 	echo ($j == '""' || $j == '')? "{\"faultCode\":\"-1\",\"faultString\":\"No return value from xml-rpc call.\"}": $j;

?>

