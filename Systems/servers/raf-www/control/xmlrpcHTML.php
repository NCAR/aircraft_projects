<?php

	//include utils file for xmlrpc functions
	include_once('../adads/utils/utils.php');
	
	//don't let browswer cache this page
	if (isset($_SERVER['HTTP_USER_AGENT']) && (strpos($_SERVER['HTTP_USER_AGENT'], 'MSIE') !== false)) { header('Cache-Control: no-cache'); header('Expires: -1'); }
	else { header('Cache-Control: no-cache, must-revalidate'); header('Expires: Sat, 26 Jul 1997 05:00:00 GMT'); }

	// get vars from HTTP 'GET' args if possible, otherwise use default
	$port = isset($_GET['port']) ? $_GET['port'] : 30006 ;
	$method = isset($_GET['method']) ? $_GET['method'] : 'GetClocks' ;
	$args = isset($_GET['args']) ? $_GET['args'] : '' ;

	//send request to status-listener
	$response = xu_rpc_http_concise(
	   array( 'method'   => $method,
	          'args'     => $args,
	          'host'     => 'localhost',
	          'uri'      => '/RPC2',
	          'port'     => $port,
	          'debug'    => '0',
	          'output'   => 'xmlrpc',
	          'nodecode' => 'true',
	          'timeout'  => '0'  // seconds (0 = never)
	          )
	   );
	
	//$response is returned as sanitized html - need to change back to real html (for proper browser display): 
	echo str_replace('&amp;', '&', str_replace('&lt;', '<', str_replace('&gt;', '>', $response)));
?>
