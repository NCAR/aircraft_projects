//acMap is sub-class of OpenLayers.Map
acMap.prototype = new OpenLayers.Map();
function acMap() {

	//create vector list
	this.vectorList = new Array();

	//create xMeasure object
	this.xMeasure = new xMeasure_t();

	// create map controls
	this.controls = [
		this.xMeasure.dragger,
		new OpenLayers.Control.LayerSwitcher(),
		new OpenLayers.Control.PanZoomBar(),
		new OpenLayers.Control.Navigation({ zoomWheelEnabled:false })
	];

	// create map
	OpenLayers.Map.call(this, 'map', {
		controls: this.controls,
		projection: smProj, 
		numZoomLevels: 18,
		maxResolution: 156543.0339,
		maxExtent: new OpenLayers.Bounds(-20037508.34, -20037508.34,
					20037508.34, 20037508.34)
	});

	// create/add basemap and plane icon
	this.planeLayer = new acPlaneLayer();
	this.baseMap = new acBaseMap(); 
	this.addLayers([this.baseMap, this.planeLayer, this.xMeasure.xLayer, this.xMeasure.lineLayer]);
	
	//function to initialize all data/settings for the map 
	this.initMap = function() {
		// fill in opacity box
		var opac_cookie = cookieJar.getCookie("mapImgOpacity")
		document.getElementById('opac').value = opac_cookie ? opac_cookie * 100 : 100;
	
		// define event handlers
		map.events.register("mousemove", this, function(e) {
			var m_lonlat = this.getLonLatFromPixel(new OpenLayers.Pixel(e.xy.x,e.xy.y));
			this.xMeasure.cursorLoc.x = m_lonlat.lon;
			this.xMeasure.cursorLoc.y = m_lonlat.lat;

			m_lonlat.transform(smProj, llProj);
			document.getElementById('position').innerHTML = this.dd2dm(m_lonlat);
			document.getElementById('dest2').innerHTML = this.getDegNmi( 
				new OpenLayers.LonLat(
					this.xMeasure.xLoc.x,
					this.xMeasure.xLoc.y).transform(smProj, llProj),
					m_lonlat
			);
			this.xMeasure.lineLayer.redraw();	
		});
		this.events.register("moveend", this, function(e) {
			cookieJar.setCookie("viewBounds", this.getExtent().toBBOX(), 10);
		});
		this.events.register("zoomend", this, function(e) {
			cookieJar.setCookie("viewBounds", this.getExtent().toBBOX(), 10);
		});
		this.events.register("changelayer", this, function(e) {
			var layerList = this.getLayersBy("visibility", true);
			var layerCookie;
			for (var i in layerList){
				layerCookie += layerList[i].name + "^";
			}	
			cookieJar.setCookie("layers", layerCookie,10);
		});
	
		// make errors more pretty
		OpenLayers.IMAGE_RELOAD_ATTEMPTS = 3;
		OpenLayers.Util.onImageLoadErrorColor = "transparent";
	
		// set viewport from cookie
		var boundc=cookieJar.getCookie('viewBounds');
		if (boundc) {
			var bc = boundc.split(','); 
			this.zoomToExtent(new OpenLayers.Bounds(bc[0], bc[1], bc[2], bc[3]), true);
		} else {
			this.zoomToMaxExtent();
		}
	
		// update icon now and every 10 seconds
		this.getIconUpdate();
		setInterval(this.getIconUpdate, 10000);

	}

	// define other useful functions
	this.getIconUpdate = function() {
		//send request to acserver for latest lat/lon
		OpenLayers.Request.GET({ 
			url: 'latlon.php', 
			callback: this.applyIconUpdate,
			scope: this
		});
	}
	this.applyIconUpdate = function(response) {
		//parse response into JSON object
		var j = new OpenLayers.Format.JSON();
		var h = j.read(response.responseText);
		var lonLat = new OpenLayers.LonLat(h.lon, h.lat).transform(llProj, smProj);
	
		//set icon to reflect latest position and heading
		this.planeLayer.icon.style.rotation = h.head;
		this.planeLayer.icon.geometry.x = lonLat.lon;
		this.planeLayer.icon.geometry.y = lonLat.lat;
		this.planeLayer.icon.attributes.description = "altitude: "+h.alt;
		this.planeLayer.setVisibility(true);
		this.planeLayer.redraw();

		//update the markerline position
		this.xMeasure.planeLoc.x = lonLat.lon;
		this.xMeasure.planeLoc.y = lonLat.lat;
		this.xMeasure.lineLayer.redraw();
	}
	this.addImageOverlay = function(g) {
		var graphic = new OpenLayers.Layer.Image(
			g.name,
			g.href + "?" + Math.random(),
			new OpenLayers.Bounds(g.w, g.s, g.e, g.n).transform(llProj, smProj),
			new OpenLayers.Size(g.pxW, g.pxH),
			{
				isBaseLayer: false,
				projection: llProj, 
				numZoomLevels: 18,
				maxResolution: 156543.0339
			}
		);
		graphic.visibility = (cookieJar.getLayerCookie(g.name));
		graphic.opacity = cookieJar.getCookie("mapImgOpacity");

		this.addLayer(graphic);
		this.setLayerIndex(graphic, 0);
		if (g.refresh) {
			setInterval(function(){
				graphic.url = graphic.url.split("?",1) + "?" + Math.random();
				graphic.redraw();
			}, 1000*g.refresh);
		}
	}
	this.addVector = function(g) {
		var vector = new OpenLayers.Layer.GML( g.name, g.href, {
			visibility: (cookieJar.getLayerCookie(g.name)),
			/*styleMap: new OpenLayers.StyleMap({"default": {
				pointRadius: 5,
				strokeWidth: 1,
				fillColor: 'orange',
				strokeColor: "red",
				fillOpacity: 0.4,

				label: "${name}",
				fontColor: "#000000",
				labelAlign: "left"
			}}),*/
			projection: llProj,
			strategies: [new OpenLayers.Strategy.Fixed()],
			protocol: new OpenLayers.Protocol.HTTP({
				url: g.href,
				headers: {
					"If-Modified-Since": "Sat, 26 Jul 1997 05:00:00 GMT"
				},
				format:  new OpenLayers.Format.KML({
					extractStyles: true,
					extractAttributes: true 
				})
			})
		});
		this.addLayer(vector);
		this.setLayerIndex(vector, 0);
		this.vectorList.push(vector) - 1;
		if (g.refresh) {
			setInterval( function() {
				vector.refresh();
			}, 1000*g.refresh);
		}
	}
	this.changeOpacity = function(val) {
		if (val > 1 || val < 0) {
			document.getElementById('opacErr').innerHTML = '0-100 only!';
		} else {
			var layers = map.getLayersByClass("OpenLayers.Layer.Image");
			for (var i in layers){
				layers[i].setOpacity(val);
			}
			cookieJar.setCookie("mapImgOpacity", val, 10);
			document.getElementById('opacErr').innerHTML = '%';
		}
	}
	this.dd2dm = function(ll){
		var dmsString;

		var x = ll.lon, y=ll.lat;
		var xf = x > 0 ? Math.floor(x) : Math.ceil(x);
		var yf = y > 0 ? Math.floor(y) : Math.ceil(y);
		var xd = Math.abs(x-xf), yd = Math.abs(y-yf);
		var xm = Math.round((60 * xd) * 1000)/1000;
		var ym = Math.round((60 * yd) * 1000)/1000;

		dmsString = yf + " " + ym;
		dmsString += ", ";
		dmsString += xf + " " + xm;

		return dmsString;
	}
	this.getDegNmi = function(ll1, ll2) {
		var lon1 = ll1.lon * Math.PI / 180, lat1 = ll1.lat * Math.PI / 180;
		var lon2 = ll2.lon * Math.PI / 180, lat2 = ll2.lat * Math.PI / 180;
	
		//var R = 6371; // km
		//var R = 3957; // mi
		var R = 3483; // nautical mi
		var d = Math.acos(Math.sin(lat1)*Math.sin(lat2) + 
			Math.cos(lat1)*Math.cos(lat2) *
			Math.cos(lon2-lon1)) * R;
	
		var y = Math.sin(lon2-lon1) * Math.cos(lat2);
		var x = Math.cos(lat1)*Math.sin(lat2) -
			Math.sin(lat1)*Math.cos(lat2)*Math.cos(lon2-lon1);
	
		var th = Math.atan2(y, x);
		//TODO dec??
		var dec = 0; 
		th = Math.round(((th * 180 / Math.PI)+360+dec) % 360); 
	
		return th + "&deg;, " + Math.round(d) + " nmi";
	}
	this.parseKML = function() {
		OpenLayers.Request.GET({
			url: 'getKML.php',
			callback: function(data){
				var j = new OpenLayers.Format.JSON();
				var h = j.read(data.responseText);
				for (var i in h.images) {
					map.addImageOverlay(h.images[i]);
				}
				for (var i in h.vectors) {
					map.addVector(h.vectors[i]);
				}
				map.vectorList.push(map.planeLayer);
				map.selector = new acSelector(map.vectorList);

			}
		});
	}
	this.centerOnPlane = function() {
		this.panTo(new OpenLayers.LonLat(this.xMeasure.planeLoc.x, this.xMeasure.planeLoc.y));
	}
	this.togglexMarker = function() {
		if (this.xMeasure.dragger.active){
			this.xMeasure.dragger.deactivate();
			this.selector.activate();
//			this.xMeasure.xLayer.setVisibility(false);
			this.xMeasure.xPoint.style.fillColor = "#FF0000";
			this.xMeasure.xLayer.redraw();
//			this.xMeasure.lineLayer.setVisibility(false);
			document.getElementById('xMarkButton').innerHTML = 'Activate';
		} else {
			this.xMeasure.dragger.activate();
			this.selector.deactivate();
//			this.xMeasure.xLayer.setVisibility(true);
			this.xMeasure.xPoint.style.fillColor = "#00FF00";
			this.xMeasure.xLayer.redraw();
//			//this.xMeasure.lineLayer.setVisibility(document.getElementById('xMarkLines').checked);
			document.getElementById('xMarkButton').innerHTML = 'Deactivate';
		}
	}
	this.togglexMarkerLines = function() {
//		if (this.xMeasure.dragger.active){
			this.xMeasure.lineLayer.setVisibility(document.getElementById('xMarkLines').checked);
//		}	
	}
}

function cookieJar_t() {
	this.setCookie = function(c_name, value, expire_days) {
		//set cookie named <c_name> with value <value>, set to expire in <expire_days>
		var exdate=new Date();
		exdate.setDate(exdate.getDate()+expire_days);
		document.cookie=c_name+ "=" +escape(value)+
		((expire_days==null) ? "" : ";expires="+exdate.toGMTString());
	}
	this.getCookie = function(c_name) {
		//retrieve information from cookie with <c_name>
		if (document.cookie.length>0)
		{
			c_start=document.cookie.indexOf(c_name + "=");
			if (c_start!=-1)
			{
				c_start=c_start + c_name.length+1;
				c_end=document.cookie.indexOf(";",c_start);
				if (c_end==-1) c_end=document.cookie.length;
				return unescape(document.cookie.substring(
							c_start,c_end));
			}
		}
		return false;
	}
	this.cookieOr = function(c_name, ret_value_if_false) {
		var cookie = this.getCookie(c_name);
		return cookie? cookie : ret_value_if_false;
	}
	this.originalLayersCookie = this.getCookie("layers");
	this.getLayerCookie = function(l_name) {
		if (this.originalLayersCookie) {
			if (this.originalLayersCookie.indexOf(l_name+"^") != -1){
				return true;	
			}
		}
		return false;
	}
}

acPlaneLayer.prototype = new OpenLayers.Layer.Vector();
function acPlaneLayer() {
	OpenLayers.Layer.Vector.call(this, "Plane", {
		visibility: false,
		displayInLayerSwitcher: false,
		maxResolution: 156543.0339,
		maxExtent: new OpenLayers.Bounds(-20037508.34, -20037508.34,
					20037508.34, 20037508.34)
	});
	this.icon = new OpenLayers.Feature.Vector( 
		new OpenLayers.Geometry.Point(0,0),
		null,
		{externalGraphic: 'blueplane.png', graphicWidth: 30, graphicHeight: 30, graphicOpacity: 0.8 }
	);
	this.icon.attributes = {name: "Plane", description: "could put some flight data here?"};
	this.addFeatures([this.icon]);
}

acBaseMap.prototype = new OpenLayers.Layer.OSM();
function acBaseMap() {
	OpenLayers.Layer.OSM.call(this,
		"OpenStreetMap",
		"tiles2/${z}/${x}/${y}.png",
		{
			displayOutsideMaxExtent: false,
			displayInLayerSwitcher: false,
			sphericalMercator: true
		}
	);
}

acSelector.prototype = new OpenLayers.Control.SelectFeature();
function acSelector(vecList) {
	OpenLayers.Control.SelectFeature.call(this,
		vecList,
		{
			clickout:true, hover:false,
			onSelect: function(e) {
				document.getElementById('kName').innerHTML=e.attributes.name;
				document.getElementById('kDescription').innerHTML=e.attributes.description;
				document.getElementById('detailsBox').className="detail";
			},
			onUnselect: function(e) {
				document.getElementById('detailsBox').className="detail_hidden";
			}
		}
	);
	map.addControl(this);
	this.activate();
}

function xMeasure_t() {

	//create point for tracking distance, angle
	this.planeLoc = new OpenLayers.Geometry.Point(-81.644, 28.035).transform(llProj,smProj);
	this.xLoc = new OpenLayers.Geometry.Point(cookieJar.cookieOr("xLoc_x",0),cookieJar.cookieOr("xLoc_y",0));
	this.cursorLoc = new OpenLayers.Geometry.Point(0,0);

	//create structions for for dragging the X
	this.xPoint = new OpenLayers.Feature.Vector(this.xLoc, null, {strokeColor:"#000000", strokeWidth: 1, pointRadius: 8, fillOpacity: 0.8, fillColor: '#FF0000', cursor: 'pointer', graphicName: 'x'});
	this.xLayer = new OpenLayers.Layer.Vector("Measure Marker", {visibility: true, displayInLayerSwitcher: false});
	this.xLayer.addFeatures([this.xPoint]);
	this.plane2x = new OpenLayers.Feature.Vector( new OpenLayers.Geometry.LineString([this.planeLoc, this.xLoc]), null, {strokeColor:"#00FF00", strokeOpacity: 0.7, strokeWidth: 4, strokeDashstyle: 'longdash'});
	this.x2mouse = new OpenLayers.Feature.Vector( new OpenLayers.Geometry.LineString([this.xLoc, this.cursorLoc]), null, {strokeColor:"#0000FF", strokeOpacity: 0.7, strokeWidth: 4, strokeDashstyle: 'longdash'});
	this.lineLayer = new OpenLayers.Layer.Vector("Measure Lines", {visibility: false, displayInLayerSwitcher: false});
	this.lineLayer.addFeatures([this.plane2x, this.x2mouse]);

	//create dragger control
	this.dragger = new OpenLayers.Control.DragFeature(this.xLayer, {onDrag: function(newX) {
		var x_lonlat = new OpenLayers.LonLat(newX.geometry.x, newX.geometry.y).transform(smProj, llProj);
		var plane_lonlat = new OpenLayers.LonLat(map.xMeasure.planeLoc.x, map.xMeasure.planeLoc.y).transform(smProj, llProj)
		document.getElementById('dest').innerHTML = map.getDegNmi(plane_lonlat, x_lonlat);
	}, onComplete: function(newX) {
		cookieJar.setCookie('xLoc_x', newX.geometry.x, 10);
		cookieJar.setCookie('xLoc_y', newX.geometry.y, 10);
	}});

}


