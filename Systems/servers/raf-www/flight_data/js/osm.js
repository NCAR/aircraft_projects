//acMap is sub-class of OpenLayers.Map
acMap.prototype = new OpenLayers.Map();
function acMap() {

	// fill in opacity box
	this.opac_cookie = cookieJar.cookieOr("mapImgOpacity","100");

	//create vector list
	this.vectorList = new Array();

	//create xMeasure object
	this.xMeasure = new xMeasure_t();

	// create map controls
	this.controls = [
		this.xMeasure.dragger,
		//new OpenLayers.Control.LayerSwitcher(),
		new OpenLayers.Control.Navigation()
	];

	// create map
	OpenLayers.Map.call(this, 'map', {
		controls: this.controls,
		projection: smProj, 
		numZoomLevels: 17,
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
			$('#curZoomLevel').text(this.zoom);
			cookieJar.setCookie("viewBounds", this.getExtent().toBBOX(), 10);
		});
		this.events.register("changelayer", this, function(e) {
			var layerList = this.getLayersBy("visibility", true);
			var layerCookie;
			for (var i in layerList){
				layerCookie += layerList[i].name.split(": ", 1)[0] + "^";
			}	
			cookieJar.setCookie("layers", layerCookie,10);
		});
	
		// make errors more pretty
		OpenLayers.IMAGE_RELOAD_ATTEMPTS = 3;
		OpenLayers.Util.onImageLoadErrorColor = "transparent";
		OpenLayers.Util.onImageLoadError = function() {
			this.src = "/flight_data/display/loading.png";
			this.style.display = "";
		};
	
		// set viewport from cookie
		var boundc=cookieJar.getCookie('viewBounds');
		if (boundc) {
			var bc = boundc.split(','); 
			this.zoomToExtent(new OpenLayers.Bounds(bc[0], bc[1], bc[2], bc[3]), true);
		} else {
			//this.zoomToMaxExtent();
			this.zoomTo(4);
		}

		//add timestamp
		//this.addTimestampOverlay();

		// update icon now and every 10 seconds
		this.getIconUpdate();
		setInterval(this.getIconUpdate, 10000);

		// update the camera image every 5 minutes
		this.updateCamImage(true);
		setInterval(this.updateCamImage, 5000);
	}

	// define other useful functions
	this.addLayerCheckbox = function(layer) {
		var newChkBoxId = "cbox_" + layer.name + "_id";

		var newChkBoxLbl = $('<label></label>')
		.text(layer.name)
		.attr('for', newChkBoxId);

		var newChkBox = $('<input type="checkbox" />')
		.attr('id', newChkBoxId)
		.attr('checked', layer.visibility)
		.click(function() {
			var newVis = this.checked;
			layer.setVisibility(newVis);
		});

		$('#lListDiv').append(newChkBox).append(newChkBoxLbl).append('<br>');
	}

	this.updateCamImage = function(first) {
		var camdom = document.getElementById("cam");
		if ($("#cameraBox").hasClass("above") || first) {
			camdom.src = "/flight_data/images/latest_forward?" + Math.random();
		}
	}

	this.getIconUpdate = function() {
		//send request to acserver for latest lat/lon
		OpenLayers.Request.GET({ 
			url: '/cgi-bin/flight_data/osm_latlon.pl?'+Math.random(), 
			callback: map.applyIconUpdate,
			scope: map 
		});
	}
	this.applyIconUpdate = function(response) {
		//parse response into JSON object
		var j = new OpenLayers.Format.JSON();
		var h = j.read(response.responseText);
		var lonLat = new OpenLayers.LonLat(h.lon, h.lat).transform(llProj, smProj);
	
		//set icon to reflect latest position and heading
		this.planeLayer.icon.style.rotation = h.head;
		this.planeLayer.icon.attributes.description = "Position:<br>"+h.lat+"&deg;N, "+h.lon+"&deg;E<br><br>Heading: "+(h.head%360)+"&deg;<br>Altitude: "+h.alt+"m";
		this.planeLayer.setVisibility(true);
		this.planeLayer.icon.move(lonLat);

		//update the markerline position
		this.xMeasure.planeLoc.x = lonLat.lon;
		this.xMeasure.planeLoc.y = lonLat.lat;
		this.xMeasure.lineLayer.redraw();

		// get initial xMarker distance
		document.getElementById('dest').innerHTML =
			map.getDegNmi( lonLat.transform(smProj, llProj),
				new OpenLayers.LonLat(
					this.xMeasure.xLoc.x,
					this.xMeasure.xLoc.y).transform(smProj, llProj)
			);

		if (newplatform) { this.centerOnPlane(); newplatform = false; }

	}
	this.addTimestampOverlay = function() {
		if (cookieJar.getCookie("platform") != "C130") {
			return
		}
		var timediv = document.createElement('div');
		timediv.style.opacity = .7;
		timediv.style.filter = "alpha(opacity=70)";

		timediv.style.position = "absolute";
		timediv.style.bottom = "27px";
		timediv.style.left = "50%";
		timediv.style.marginLeft = "-405px";
		timediv.style.zIndex = "750";

		var timestamp1 = document.createElement('img');
		timestamp1.src = "/flight_data/C130/images/sat_label.jpg";
		timestamp1.style.marginLeft = "5px"; 
		var timestamp2 = document.createElement('img');
		timestamp2.src = "/flight_data/C130/images/radar_label.jpg";
		timestamp2.style.marginLeft = "5px"; 

		timediv.appendChild(timestamp1);
		timediv.appendChild(timestamp2);
		
		document.getElementById("debug").appendChild(timediv);

		setInterval(function(){
			timestamp1.src = timestamp1.src.split("?",1) + "?" + Math.random();
			timestamp2.src = timestamp2.src.split("?",1) + "?" + Math.random();
		}, 60000);
	}
	this.addImageOverlay = function(g) {
		var domimg = new Image(); domimg.src = g.href;
		var graphic = new OpenLayers.Layer.Image(
			g.name,
			g.href + "?" + Math.random(),
			new OpenLayers.Bounds(g.w, g.s, g.e, g.n).transform(llProj, smProj),
			new OpenLayers.Size(domimg.width,domimg.height),
			{
				isBaseLayer: false,
				alwaysInRange: true
				/*projection: llProj, 
				numZoomLevels: 17,
				maxResolution: 156543.0339*/
			}
		);
		graphic.visibility = (cookieJar.getLayerCookie(g.name));
		graphic.opacity = cookieJar.getCookie("mapImgOpacity");
		graphic.cleanUrl = g.cleanHref;

		this.addLayer(graphic);
		this.setLayerIndex(graphic, 0);
		this.addLayerCheckbox(graphic);
		if (g.refresh) {
			setInterval(function(){
				graphic.url = graphic.url.split("?",1) + "?" + Math.random();
				graphic.redraw();
			}, 1000*g.refresh);
		}
		$('#oSlider, #oSliderLabel').show();
	}
	this.addVector = function(g) {
		var vis = (g.name.search("Track") != -1)? true:
			(cookieJar.getLayerCookie(g.name));

		var vector = new OpenLayers.Layer.GML( 
			g.name,
			g.href,
			{
				visibility: vis,
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
		vector.cleanUrl = g.cleanHref;
		this.addLayerCheckbox(vector);

		if (g.refresh) {
			setInterval( function() {
				vector.refresh();
			}, 1000*g.refresh);
		}
	}
	this.changeOpacity = function(val) {
		var layers = map.getLayersByClass("OpenLayers.Layer.Image");
		for (var i in layers){
			layers[i].setOpacity(val);
		}
		cookieJar.setCookie("mapImgOpacity", val, 10);
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
		dmsString += "N, ";
		dmsString += xf + " " + xm + "E";

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
			url: '/cgi-bin/flight_data/osm_getKML.pl?'+Math.random(),
			callback: function(data){
				var j = new OpenLayers.Format.JSON();
				var jsonText = data.responseText.split("1\n", 1);
				var h = j.read(jsonText[0]);
				for (var i in h.images) {
					map.addImageOverlay(h.images[i]);
				}
				for (var i in h.vectors) {
					map.addVector(h.vectors[i]);
				}
				map.vectorList.push(map.planeLayer);
				map.hover = new acHover(map.vectorList);
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
			this.hover.activate();
			this.selector.activate();
			this.xMeasure.xPoint.style.fillColor = "#FF0000";
			this.xMeasure.xLayer.redraw();
			$('#xMarkButton').addClass('icon_arrow_r');
			$('#xMarkButton').removeClass('icon_arrow_g');
		} else {
			this.xMeasure.dragger.activate();
			this.selector.deactivate();
			this.hover.deactivate();
			this.xMeasure.xPoint.style.fillColor = "#00FF00";
			this.xMeasure.xLayer.redraw();
			$('#xMarkButton').addClass('icon_arrow_g');
			$('#xMarkButton').removeClass('icon_arrow_r');
		}
	}
	this.togglexMarkerLines = function() {
		var llayer = this.xMeasure.lineLayer;
		var newvis = llayer.visibility? false: true;
		llayer.setVisibility(newvis);
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
	this.getLayerCookie = function(i_name) {
		l_name = i_name.split(": ", 1)[0];
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
		'calculateInRange': function() {return true; },
		numZoomLevels: 18
	});
	this.icon = new OpenLayers.Feature.Vector( 
		new OpenLayers.Geometry.Point(0,0),
		null,
		{externalGraphic: '/flight_data/display/blueplane.png', graphicWidth: 30, graphicHeight: 30, graphicOpacity: 0.8 }
	);
	this.icon.attributes = {name: "Plane", description: "plane description"}
	this.addFeatures([this.icon]);
}

acBaseMap.prototype = new OpenLayers.Layer.OSM();
function acBaseMap() {
        OpenLayers.Layer.OSM.call(this,
                "OpenStreetMap",
                "/osm/tiles2/${z}/${x}/${y}.png",
                {
                        displayOutsideMaxExtent: false,
                        displayInLayerSwitcher: false,
                        sphericalMercator: true
                }
        );
}

acHover.prototype = new OpenLayers.Control.SelectFeature();
function acHover(vecList) {
	OpenLayers.Control.SelectFeature.call(this,
		vecList,
		{
			hover:true, highlightOnly: true, renderIntent: 'temporary',
			eventListeners: {
				featurehighlighted: function(e) {
					var aName=e.feature.attributes.name.substring(0,10);
					if (e.feature.attributes.name.length > 10) aName += "...";

					document.getElementById('curHovItem').innerHTML= 
						aName === undefined? " - ": aName;
				},
				featureunhighlighted: function(e) {
					document.getElementById('curHovItem').innerHTML="";
				}
			}
		}
	);
	map.addControl(this);
	this.activate();
}

acSelector.prototype = new OpenLayers.Control.SelectFeature();
function acSelector(vecList) {
	OpenLayers.Control.SelectFeature.call(this,
		vecList,
		{
			clickout:true, hover:false,
			onSelect: function(e) {
				var aName=e.attributes.name === undefined? " - ": e.attributes.name;
				var aDes=e.attributes.description === undefined? " - ": e.attributes.description;
				e.popup = new OpenLayers.Popup.FramedCloud('chicken',
					e.geometry.getBounds().getCenterLonLat(),
					new OpenLayers.Size(100,100),
					'<b>'+aName+'</b><p>'+aDes+'</p>',
					null, false);
				map.addPopup(e.popup);
			},
			onUnselect: function(e) {
				map.removePopup(e.popup);
				e.popup.destroy();
				delete e.popup;
			}
		}
	);
	map.addControl(this);
	this.activate();
}

function xMeasure_t() {

	//create point for tracking distance, angle
	this.planeLoc = new OpenLayers.Geometry.Point(-81.644, 28.035).transform(llProj,smProj);
	this.xLoc = new OpenLayers.Geometry.Point(cookieJar.cookieOr("xLoc_x",-9984743.889400965),cookieJar.cookieOr("xLoc_y",4962640.215298362));
	this.cursorLoc = new OpenLayers.Geometry.Point(0,0);

	//create structions for for dragging the X
	this.xPoint = new OpenLayers.Feature.Vector(this.xLoc, null, {strokeColor:"#000000", strokeWidth: 1, pointRadius: 7, fillOpacity: 0.5, fillColor: '#FF0000', cursor: 'pointer', graphicName: 'circle'});
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

/*=================Globals=================*/
//cookieJar is global handler for setting and retrieing cookies
var cookieJar = new cookieJar_t();

//define two global projections for transforms
var smProj = new OpenLayers.Projection("EPSG:900913");
var llProj = new OpenLayers.Projection("EPSG:4326");

//make map global
var map;

//create init function
$(function() {

	//create and initialize the map
	map = new acMap();
	map.initMap();

	//Add images and network links from osm.kml 
	map.parseKML();
	
	//set up platform chooser
	$('#pform_label').click(function() { $('#pformDialog').toggle(); });
	$('#pformDialog').load('/cgi-bin/flight_data/osm_platform.pl', function(){
		//make platform table clickable
		$('#pformDialog tr:gt(0)').click(function(){
			$('#pformDialog tr:gt(0)').children()
				.css({"background-color":"#fff","color":"#000"});
			$(this).children()
				.css({"background-color":"#F39814",'color':'#fff'});
			$(this).find('input').attr('checked', true);
			$('form :submit:first').trigger('click');
		});
	});

	//set platform name from cookie
	$('#pform_label, #pform_label_h').html(cookieJar.getCookie("platform"));

	//set layerswitcher to be draggable and resizeable
	addStateDragResize($('#lSwitchBox'), $('#lSwitchToggle'), 
		{id:'ls_', draggable:true});

	//init cambox
	var cambox = $('#cameraBox');
	addStateDragResize(cambox, $('#camToggle'),
		{id:'cam',draggable:true});

	cambox.css('width', cookieJar.cookieOr('camSizeX', "192px"));

	cambox.resizable({'aspectRatio':true, 'stop':function(e, ui){
		cookieJar.setCookie('camSizeX', ui.size.width, 10);
	}});

	cambox.dblclick(function() {
			var rawimg = $("<img>").attr('src', $("#cam").attr('src'));
			var newwidth = rawimg.attr('width');
			var newheight = rawimg.attr('height');
			rawimg.remove();

			$(this).css('width', newwidth);
			$(this).css('height', newheight);
			cookieJar.setCookie('camSizeX', newwidth, 10);
	});


	//init dpad
	$('td.x').click(function(){
		var backDiv = $('#movToggle div:first');
		backDiv.removeClass("icon_move").addClass("icon_move_red");

		setTimeout(function(){
			backDiv.removeClass("icon_move_red").addClass("icon_move");
		}, 500);

	});

	//init transparency slider
	$('#oSlider').slider({
		value: map.opac_cookie*100,
		min: 0, max: 100,
		slide: function(event, ui) {
			map.changeOpacity(ui.value/100);
		}
	});
	
	//display starting zoom
	$('#curZoomLevel').text(map.zoom);

	//display status message to non-firefox users
	window.status = "This site is best viewed using Mozilla Firefox";
});

function toggleHelp() {
	window.open("/flight_data/quickhelp.html", "Quick Reference", "width=600,height=400,menubar=no,status=no,toolbar=no,location=no,scrollbars=yes,resizable=yes");
}

function addStateDragResize(jqd, jqtrig, opt) {

	jqd.css('left', cookieJar.cookieOr(opt.id+'PosX', '40px'))
	.css('top', cookieJar.cookieOr(opt.id+'PosY', '50px'));

	if (cookieJar.getCookie(opt.id+'Shown') == 'true') {
		jqd.removeClass("nodisp");
		jqd.addClass("above");
	}
	if (opt.draggable) {
		jqd.draggable({'containment':'window', 'scroll':'false',
		'stop':function(e, ui){
			cookieJar.setCookie(opt.id+'PosX', ui.offset.left, 10);
			cookieJar.setCookie(opt.id+'PosY', ui.offset.top, 10);
		}});
	}
	jqtrig.click(function() { 
		var cbox = jqd;
		var hidden = cbox.hasClass('nodisp');

		if (!hidden) {
			cbox.effect("transfer", {to: jqtrig}, 500);
			cbox.removeClass("above");
			cbox.addClass("nodisp");
		} else {
			cbox.removeClass("nodisp");
			cbox.addClass("below");
			jqtrig.effect("transfer", {to: cbox}, 300, function(){
				cbox.removeClass("below");
				cbox.addClass("above");
			});
		}

		cookieJar.setCookie(opt.id+'Shown', hidden, 10);
	});
}
