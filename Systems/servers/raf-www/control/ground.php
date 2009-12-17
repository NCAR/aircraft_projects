<?php
//ini_set('display_errors','1');

//include utils file for xmlrpc functions
include_once('utils.php');

/* if list is set, then show list, otherwise assume a command is being sent */
if (isset($_GET['list'])) sendList();
else {
	if (! (isset($_GET['method']) && isset($_GET['host']) && isset($_GET['port']))) 
		exit("need method,host and port");     

	$args = null;
	if (isset($_GET['args']) && $_GET['args'] != '') $args = $_GET['args'];

	syslog(LOG_NOTICE, "Xml-Rpc command, sent {$_GET['method']} to {$_GET['host']}"
		. " from {$_SERVER['REMOTE_ADDR']}");

	echo "<pre>";
	print_r( xu_rpc_http_concise( array( 'method' => $_GET['method'],
	'args'   => $_GET['args'], 'host'   => $_GET['host'], 'uri'    => '/RPC2',
	'port'   => $_GET['port'], 'debug'  =>  '0', 'output' => 'xmlrpc' )));
	echo "</pre>";
}

function sendList(){
	syslog(LOG_NOTICE, "Xml-Rpc list request from {$_SERVER['REMOTE_ADDR']}");

	$config_str = file_get_contents("js/config.json");
	$config = json_decode($config_str,true);

	//send request to status-listener
	$dsmList = xu_rpc_http_concise( array( 'method' => 'GetDsmList',
	'args'   => '', 'host'   => 'localhost', 'uri'    => '/RPC2',
	'port'   => '30003', 'debug'  =>  '0', 'output' => 'xmlrpc' ));

	/* this array will hold all of the methods from the static config file, 
	   as well as any that can be obtained via introspection */
	$allMethods = Array(); 

	foreach ($config['dsms'] as $tag => $dsm) {
		$allMethods[$tag]['name'] = $dsm['name'];
		$allMethods[$tag]['host'] = $dsm['host'];
		$allMethods[$tag]['port'] = ($tag == "dsm_server"? '30003': '30004');

		//Get methods from introspection
		$methList = xu_rpc_http_concise(array('method' => 'system.listMethods',
		'args' => null, 'host' => $dsm['host'], 'uri' => '/RPC2',
		'port' => ($tag == "dsm_server"? '30003': '30004'), 
		'debug' => '0', 'output' => 'xmlrpc' ));

		if ($methList != '') {
			foreach ($methList as $methname)
				$allMethods[$tag]['methods'][$methname] = false;
		}

		//Get methods from static config
		foreach ($dsm['controls'] as $title => $control) {
			if (is_string($control)) {
				$allMethods[$tag]['methods'][$title] = $control;
			} else {
				$allMethods[$tag]['methods'][$title] = $control;
			}
		}
	}

	foreach ($dsmList as $tag => $name) {
			
		$methList = xu_rpc_http_concise(array('method' => 'system.listMethods',
		'args' => null, 'host' => $tag, 'uri' => '/RPC2',
		'port' => '30004', 'debug' => '0', 'output' => 'xmlrpc' ));

		if ($methList != '') {
			$allMethods[$tag]['name'] = $name;
			$allMethods[$tag]['host'] = $tag;
			$allMethods[$tag]['port'] = 30004;

			foreach ($methList as $methname)
				$allMethods[$tag]['methods'][$methname] = false;
		}
	}

	/* Add static links here: */
	echo "<h2>Static Commands (Not Implemented Yet):</h2>\n<ul>\n";
	echo "<li>Reboot MTP Laptop</l>\n";
	echo "</ul>\n";

	/* The rest of the links will be generated here: */
	foreach ($allMethods as $tag => $obj) {
		echo "<h2>{$obj['name']} ($tag):</h2>\n<ul>\n";

		foreach ($obj['methods'] as $meth => $details) {
			$link  = "<a target='_blank' href='http://"
			. $_SERVER['SERVER_NAME'] . $_SERVER['PHP_SELF'];
			
			if ($details == false) {
				$link .= "?method=$meth&host={$obj['host']}&port={$obj['port']}'"
				. " onclick=\"this.href += "
				. " prompt('Enter Params:', '&args=');\">$meth</a>";

			} else if (is_string($details)) {
				$link .= "?method=shell_exec&host=localhost&port=30009&"
				. "args[]=stayopen&args[]=$meth&args[]=".urlencode($details)
				. "'>$meth</a>";

			} else {
				foreach ($details as $key => $val) {
					$link .= "args[$key]=$val";
				}
				$link .= "'>$meth</a>";
			}
			echo "<li>$link</li>\n";
		}
		echo "</ul>\n";
	}
}
	
?>
