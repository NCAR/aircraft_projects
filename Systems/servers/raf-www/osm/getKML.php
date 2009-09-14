<?php
	/* Turn off all error reporting */
	error_reporting(0);

	$file = "include.kml";
	$imgarray = array();
	$vecarray = array();

	/* parse xml into php-native datastream */
	$xml = simplexml_load_file($file);

	/* add all image overlays to imgarray */
	findTag("groundoverlay", $xml, $imgarray);

	/* add all external kml/kmz to vecarray */
	findTag("networklink", $xml, $vecarray);
		
	/* wrap data into JSON form and send to browser */
	echo json_encode(array("images"=>$imgarray, "vectors"=>$vecarray));
	/* end */


	function findTag($tag, $node, &$oArray) {
	/* searches $node's decendants for $tag recursively. 
	 * once a node with the desired tag is found, the node is passed to 
	 *	fillimg() for processing.
	 * $oArray is passed throuh this function by reference to allow
	 *	the output array to be specified by the calling function
	 */
		foreach ($node->children() as $child){
			if (strtolower($child->getName()) == $tag) {
					fillimg($child, $oArray);
			} else {	
				findTag($tag, $child, $oArray);
			}

		}
		return false;

	}

	function fillimg($targetNode, &$outArray) {
	/* searches $targetNode for all the data needed to create 
	 *	a proper OpenLayers vector or image layer and encodes 
	 *	into $outArray.
	 */

		$valid = 1;	
		$curObj = Array();
		foreach ($targetNode->children() as $child){
			switch (strtolower($child->getName())){

				case "open": 
					$curObj['vis'] = "{$child}";
					break;
				case "name":
					$curObj['name'] = "{$child}";
					break;
				case "description":
					$curObj['description'] = "{$child}";
					break;
				case "refreshinterval":
					$curObj['refresh'] = "{$child}";
					break;
				case "link":
					foreach ($child->children() as $grandchild){
						switch (strtolower($grandchild->getName())){
	
						case "name":
							$curObj['name'] = "{$grandchild}";
							break;
						case "refreshinterval":
							$curObj['refresh'] = "{$grandchild}";
							break;
						case "href":
							if ( substr($grandchild, -3, 3) == "kmz") {
								$curObj['href'] = "kmz2kml.php?kmz=$grandchild";
							} else {	
								$curObj['href'] = "{$grandchild}";
							}
							break;
						}
					}
					break;
				case "icon":
					foreach ($child->children() as $grandchild){
						switch (strtolower($grandchild->getName())){
	
						case "name":
							$curObj['name'] = "{$grandchild}";
							break;
						case "refreshinterval":
							$curObj['refresh'] = "{$grandchild}";
							break;
						case "href":
							$curObj['href'] = "{$grandchild}";
							$size = getimagesize($grandchild);
							$valid = $size ? true : false;
							$curObj['pxW'] = $size[0]; 
							$curObj['pxH'] = $size[1]; 
							break;
						}
					}
					break;
				case "latlonbox":
					foreach ($child->children() as $grandchild){
						switch (strtolower($grandchild->getName())){
	
						case "north":
							$curObj['n'] = "{$grandchild}";
							break;
						case "east":
							$curObj['e'] = "{$grandchild}";
							break;
						case "south":
							$curObj['s'] = "{$grandchild}";
							break;
						case "west":
							$curObj['w'] = "{$grandchild}";
							break;
						}
					}
					break;
			}
		}
		if ($valid) 
			$outArray[] = $curObj;
	
	}

?>
