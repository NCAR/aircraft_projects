/*
 * COPYRIGHT: University Corporation for Atmospheric Research, 2009-12
 */

var capturePHP="/camera/capture.php"; //path from webroot to capture.php (update this manuall if it changes)
var camServer="http://192.168.84.204"; //camserver (gets updated from db automatically)

//Global Vars
var imgSrc = new Array();
var flightNumber = 0;
var maxVal = -2, offsetTime=0, imgsReady=0;
var grids=false;
var scale = "1024";
var now = new Date();
var d = new Date();

function getNames(offset, pbmode){
//get the name of the the image offset by <offset> seconds,
// pass pbmode to setImgs if offset != 0
	if (offset == 0) {
		$.getJSON("getimgs.php", function(data){
			setImgs(data.jsonImgs[$(".camCheck").size()-1], false);
		});
	} else {
		d.setTime(now.valueOf() + (1000*offset) + offsetTime);
		newImg = d.format("yymmdd-HHMMss", true) + ".jpg";
		setImgs(newImg, pbmode);
	}
}

function setImgs(name, pbmode){
//start loading the images for the next playback frame
	for (i=0; i<=$(".camCheck").size(); i=i+1){
		if ($("#showCam"+i).attr('checked') == 1 ){
                        imgSrc[i] = "http://acserver.raf.ucar.edu/";
			imgSrc[i]  = "camera_images/flight_number_";
		 	imgSrc[i] += flightNumber;
			imgSrc[i] += "/";
			imgSrc[i] += $("#showCam"+i).attr('alt');
			imgSrc[i] += "/";
			imgSrc[i] += name;
	
			if (pbmode) {
				$('<img>')
					.load(function() {
						imgsReady++;
						})
					.error(function() {
						imgsReady++;
						})
					.attr('width', scale)
					.attr('src', imgSrc[i]);
			} else { 
				$("#cam"+i).attr("src", imgSrc[i]).show();
			}
			if(grids){$("img.grid:eq("+(i-1)+")").show();}

		}else{
			$("#cam"+i).attr("src", "").hide();
			$("img.grid:eq("+(i-1)+")").hide();
		}	
	}	
		
	$("#imgNum").html(niceTime(name));
	
}
function niceTime(stdtime) {
	if (stdtime == undefined) { return 0; }
	var imgdate = stdtime.slice(0,6);
	var imgtime = stdtime.slice(7,13);
	return  imgdate.slice(2,4) + "/" + 
		imgdate.slice(4,6) + "/" +
		imgdate.slice(0,2) + " " +
		imgtime.slice(0,2) + ":" +
		imgtime.slice(2,4) + ":" +
		imgtime.slice(4,6);
}

function timedFunc() {
//main loop: updates the images and then calls itself
	if ( $("#autoUpdate").attr('checked') == 1) {
		now = new Date();
		getNames(0, false);
	}

	$(".status").load("status.php");
	if ($("#fdCheck").attr("checked") == true){
		$("span[id='flightData']").load("flightData.php");
	}
	setTimeout("timedFunc()", 1000);
}

function playFunc() {
//'Plays back' the archived images
	var curVal = $("#slider").slider('option', 'value');
	if( curVal <= maxVal ){
		if ($("#playButton").attr("checked") == true){
			imgsReady = 0;
			getNames(curVal, true);
			$("#slider").slider('option', 'value', curVal+5);
			setTimeout("checkReadyImgs()", 10);
		}
	} else {
		$("#playButton").attr("checked", false);
		$("#autoUpdate").attr("checked", true);
	}	
}

function checkReadyImgs() {
//check to see if all images are loaded, 
//if so, set image 'src', and start next frame (playFunc())
	var numChecked = $(".camCheck:checked").size();
	if (imgsReady < numChecked){
		$(".loading").show();
		setTimeout("checkReadyImgs()", 10);
	} else {	
		$(".loading").hide();
		for (i=1; i<=$(".camCheck").size(); i=i+1){
			if ($("#showCam"+i).attr('checked') == 1 ){
				$("#cam"+i).attr('src', imgSrc[i]).show();
			}
		}
		playFunc();
	}
}

function autoscaler() {
//Determines and sets the new image scaling
	var auto = $("#autoScale").attr('checked');
	var sideways = $("#sideways").attr('checked');
	var ccams = $(".camCheck:checked").size();
	var menuWidth = 250;

	if (auto) {
		if(sideways) {
			if (ccams > 2) {	// added for 2x2 layout
				ccams = 2;
			}
			if ((document.documentElement.clientWidth - menuWidth) < (document.documentElement.clientHeight * ccams)) {
				scale = (document.documentElement.clientWidth - menuWidth) / ccams;
			} else {
				scale = (document.documentElement.clientHeight);
			}
		} else {
			if (((document.documentElement.clientWidth - menuWidth) * ccams) < (document.documentElement.clientHeight)) {
				scale = (document.documentElement.clientWidth ) - menuWidth;
			} else {
				scale = (document.documentElement.clientHeight / ccams);
			}
		}

		$("img.cam").attr("width", scale);
		$("img.grid").attr("width", scale);
	} else {
		$("img.cam").removeAttr("width");
		for (i=1; i<=$(".camCheck").size(); i=i+1){
			$("img.grid:eq("+(i-1)+")").attr("width", ($("#cam"+i).attr('width') ));	
		}
	}

	if ($("#autoUpdate").attr('checked') == false) {
		getNames($("#slider").slider('value'),false);
	}
	setCookie("autoScale", auto ? "C" : "X", 10);
	var cams_selected = "";
	$(".camCheck:checked").each(function(i){
		cams_selected += this.alt + "&";
	});
	setCookie("cams_selected", cams_selected, 10);

}

function buildImageTable(sideways) {
//sets up the HTML table that holds the images
	var table_contents="";
	if(sideways){
		table_contents = "<tr>";
		for (i = 1; i <= $(".camCheck").size(); i = i + 1){
			table_contents = table_contents 
				+ '<td><img class="grid" src="grid.png" style="display:none;" /><img id="cam' + i
				+ '" class="cam" src="nothere.jpg" /></td> \n';
			if ((i % 2) == 0) {
				table_contents = table_contents + '</tr><tr>';	// for 2x2 grid
			}
		}
		table_contents = table_contents + '</tr>';

	} else {
		for (i=1; i<=$(".camCheck").size(); i=i+1){
			table_contents = table_contents
				+ '<tr><td><img class="grid" src="grid.png" style="display:none;" /><img id="cam' + i
				+ '" class="cam" src="nothere.jpg" width="200" /></td></tr> \n';
		} 
	}
	$("#imageTable").html(table_contents);
	autoscaler(); //scale images
}

function setupGlobals(){
	//get data from server needed for setting up the page
	$.getJSON("getData.php", function(data){
	        //check for offset between local and server clock
        	var servDate = new Date;
	        servDate.setTime(data.datetime);
        	var locDate = new Date();
	        offsetTime = servDate.valueOf() - locDate.valueOf();

		//update flight number from DB
		flightNumber = data.curFlNum;
		$(".flightNum").text(flightNumber);

		//get hostname of the camserver that last updated the database	
		camServer = 'http://' + data.chost;

		//get global setting cookies
		grids = getCookie("grids") != "X";
		$("#grids").attr('checked', grids); 
		var slcookie = getCookie("sliderMin");
		$("#sliderMin").val(slcookie == "X"?5:slcookie);
	});
}

$(function(){
/* ************************************************
 * JQuery page load function,  This function runs 
 * when the page is loaded.
 * Need to put all JQuery setup and event handlers
 * inside this function
 **************************************************/

	/*=========    SET UP HTML   ============*/

	//get status info
	$(".status").load("status.php");

	//capture status, get flight nubmer
	setupGlobals();

	//load camera selector checkboxes (get names from DB)
	$('#camSelectors').load('camSelect.php?'+getCookie("cams_selected"), function(){

		//load data from cookies before building tables, etc
		$("#autoScale").attr('checked', getCookie("autoScale") != "X");

		var sideways_checked = getCookie("sideways") != "X";
		$("#sideways").attr('checked', sideways_checked);
		buildImageTable( sideways_checked ); //set up image table

		timedFunc();  //start showing/refreshing images	
	});

	//set time scale for slider
	$("#sliderMin").change(function() {
		var newval = $("#sliderMin").attr('value')
		var newTime = (-60 * newval);
		$("#slider").slider('option', 'min', newTime);
		setCookie("sliderMin", newval, 10);
	});

	//set up tabs
//	$("#tabs").tabs();		

	//set up Slider
	var minSliderValue = -60 * $("#sliderMin").val();
	$('#slider').slider({
		min: minSliderValue, 
		max: maxVal,
		step: 1,
		slide: function(event, ui) {
			$("#autoUpdate").attr("checked", false);
			var curtimedate = new Date();
			var infostring = "&laquo ";
			var mins=Math.floor(-ui.value/60);
			if (mins) { infostring +=  mins + " Minutes " + (-ui.value%60) + " Seconds Ago"; }
			else { infostring += (-ui.value%60) + " Seconds Ago"; }
			curtimedate.setTime(now.valueOf() + (1000*ui.value) + offsetTime);
			infostring += ("&raquo " + niceTime(curtimedate.format("yymmdd-HHMMss", true)));
			$("#imgNum").html(infostring);
		},
		stop: function(event, ui) {
			getNames(ui.value, false)
		}
	});
	setInterval(function(){$('#camSelectors').load('camSelect.php?'+getCookie("cams_selected"));}, 15000);

	/*=========    SET UP EVENT HANDLERS    ============*/

	//autoscale events
	$("#autoScale").click(function() { autoscaler(); });
	$(window).resize(function() { autoscaler(); });

	//live flight data
	$("#fdCheck").click(function() {
		var livedata = $("#fdCheck").attr('checked');
		if (livedata) {
			$("#fdDiv").show();
		} else {
			$("#fdDiv").hide();
		}
		setCookie("fdCheck", livedata ? "C" : "X", 10);
	});

	//grid event
	$("#grids").click(function() {
		grids = $("#grids").attr('checked');
		if (!grids) {
			for (i=1; i<=$(".camCheck").size(); i=i+1){
				$("img.grid:eq("+(i-1)+")").hide();
			}
		} else { autoscaler(); }
		setCookie("grids", grids ? "C" : "X", 10);
	});					

	//request horizonal image layout
	$("#sideways").click(function() {
		var sideways_checked = $("#sideways").attr('checked');
		buildImageTable(sideways_checked);	
		setCookie("sideways", sideways_checked ? "C" : "X", 10);
	});
	
	//start,stop, refresh buttons
	$("#startRec").click(function(){
		$.ajax({type: "GET", url: camServer+capturePHP+"?start=1", dataType: "jsonp"});
		setupGlobals();
	});
	$("#stopRec").click(function(){
		$.ajax({type: "GET", url: camServer+capturePHP+"?stop=1", dataType: "jsonp"});
	});

	//live or playback control
	$("#autoUpdate").click(function() {
		if ($("#autoUpdate").attr("checked")) {
			$("#playButton").attr("checked", false);
			$("#slider").slider('value', maxVal);
		}
	});

	$("#playButton").click(function(){
		if ($("#playButton").attr("checked")){
			$("#autoUpdate").attr("checked", false);
			if ( $("#slider").slider('option', 'value') >= maxVal){
				$("#slider").slider('option', 'value', (-60 * $("#sliderMin").attr('value')));
			}
			playFunc();		
		}
	});

	$("#sendLatest").click(function(){
		loadingBox();
		$.get("sendLastImage.php", function(data){
			[dSent, dTitle, dMesg] = data.split("^^", 3);
			$("#messageboxdiv")
				.html(dMesg)
				.dialog('option', 'title', dTitle)
				.dialog('option', 'buttons', 
					dSent == "1" ? 
					{'Ok' : function() {$(this).dialog('close');} } :
					{'Send Anway': sendImageOverride,
					 'I\'ll Wait' : function() {$(this).dialog('close');} }
				);
		});
	});
	$("#messageboxdiv").dialog({autoOpen: false});
	
	//show flight data if cooke is there	
	$("#fdCheck").attr('checked', getCookie("fdCheck") != "X");
	$("#fdCheck").triggerHandler('click');
});

function loadingBox() {
	$("#messageboxdiv")
		.dialog('option', 'title', "Please Wait...")
		.html("<img src='/display/load.gif' />")
		.dialog('open')
		.dialog('option', 'buttons', {});
}

function sendImageOverride() {
	loadingBox();
	$.get("sendLastImage.php?override=true", function(data){
		[dTitle, dMesg] = data.split("^^", 2);
		$("#messageboxdiv")
			.html(dMesg)
			.dialog('option', 'title', dTitle)
			.dialog('option', 'buttons', {'Ok' : function() {$(this).dialog('close');} })
			.dialog('open');
	});
}


/*==============Cookie handlers===================*/
function setCookie(c_name, value, expire_days) {
	var exdate=new Date();
	exdate.setDate(exdate.getDate()+expire_days);
	document.cookie=c_name+ "=" +escape(value)+
	((expire_days==null) ? "" : ";expires="+exdate.toGMTString());
}
function getCookie(c_name)
{
    if (document.cookie.length>0)
    {
	c_start=document.cookie.indexOf(c_name + "=");
	if (c_start!=-1)
	{
	    c_start=c_start + c_name.length+1;
	    c_end=document.cookie.indexOf(";",c_start);
	    if (c_end==-1) c_end=document.cookie.length;
	    return unescape(document.cookie.substring(c_start,c_end));
	}
    }
    return "X";
}
	
