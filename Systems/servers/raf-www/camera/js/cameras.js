var capturePHP="/camera/capture.php"; //path from webroot to capture.php (update this manuall if it changes)
var camServer="http://sloop2.eol.ucar.edu"; //camserver (gets updated from db automatically)

//Global Vars
var imgSrc = new Array();
var flightNumber = 0;
var maxVal = -2, imgsReady=0;
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
		d.setTime(now.valueOf() + (1000*offset) );
		newImg = d.format("yymmdd-HHMMss") + ".jpg";
		setImgs(newImg, pbmode);
	}
}

function setImgs(name, pbmode){
//start loading the images for the next playback frame
	for (i=1; i<=$(".camCheck").size(); i=i+1){
		if ($("#showCam"+i).attr('checked') == 1 ){
/*TODO: put this back*/
			/*imgSrc[i]  = "camera_images/flight_number_";
		 	imgSrc[i] += flightNumber;
			imgSrc[i] += "/";
			imgSrc[i] += $("#showCam"+i).attr('alt');
			imgSrc[i] += "/";
			imgSrc[i] += name;*/

			imgSrc[i]  = "camera_images/";
			imgSrc[i] += $("#showCam"+i).attr('alt');
			imgSrc[i] += "/test.jpg";
	
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
	var menuWidth = 275;

	if (auto) {

		if(sideways){
			if ((document.documentElement.clientWidth - menuWidth) < (document.documentElement.clientHeight * ccams )) {
				scale = (document.documentElement.clientWidth / ccams ) - (menuWidth/ccams);
			} else {
				scale = (document.documentElement.clientHeight );
			}
		} else {
			if (((document.documentElement.clientWidth - menuWidth) * ccams) < (document.documentElement.clientHeight)) {
				scale = (document.documentElement.clientWidth ) - menuWidth;
			} else {
				scale = (document.documentElement.clientHeight / ccams );
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
}

function buildImageTable(sideways) {
//sets up the HTML table that holds the images
	var table_contents="";
	if(sideways){
		table_contents = "<tr>";
		for (i=1; i<=$(".camCheck").size(); i=i+1){
			table_contents = table_contents 
				+ '<td><img class="grid" src="grid.png" style="display:none;" /><img id="cam' + i
				+ '" class="cam" src="nothere.jpg" /></td> \n';
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

		//update flight number from DB
		flightNumber = data.curFlNum;
		$(".flightNum").text(flightNumber);

		//get hostname of the camserver that last updated the database	
		camServer = 'http://' + data.chost;
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
	$('#camSelectors').load('camSelect.php', function(){
		buildImageTable( true ); //set up image table
		timedFunc();  //start showing/refreshing images	
	});

	//set time scale for slider
	$("#sliderMin").change(function() {
		var newTime = (-60 * $("#sliderMin").attr('value'));
		$("#slider").slider('option', 'min', newTime);
	});

	//set up tabs
//	$("#tabs").tabs();		

	//set up Slider
	$('#slider').slider({
		min: -300,
		max: maxVal,
		step: 1,
		slide: function(event, ui) {
			$("#autoUpdate").attr("checked", false);
			var curtimedate = new Date();
			var infostring = "&laquo ";
			var mins=Math.floor(-ui.value/60);
			if (mins) { infostring +=  mins + " Minutes " + (-ui.value%60) + " Seconds Ago"; }
			else { infostring += (-ui.value%60) + " Seconds Ago"; }
			curtimedate.setTime(now.valueOf() + (1000*ui.value) );
			infostring += ("&raquo " + niceTime(curtimedate.format("yymmdd-HHMMss")));
			$("#imgNum").html(infostring);
		},
		stop: function(event, ui) {
			getNames(ui.value, false)
		}
	});


	/*=========    SET UP EVENT HANDLERS    ============*/

	//autoscale events
	$("#autoScale").click(function() { autoscaler(); });
	$(window).resize(function() { autoscaler(); });

	//live flight data
	$("#fdCheck").click(function() {
		if ($("#fdCheck").attr('checked')) {
			$("#fdDiv").show();
		} else {
			$("#fdDiv").hide();
		}
	});

	//grid event
	$("#grids").click(function() {
		grids = $("#grids").attr('checked');
		if (!grids) {
			for (i=1; i<=$(".camCheck").size(); i=i+1){
				$("img.grid:eq("+(i-1)+")").hide();
			}
		} else { autoscaler(); }
		
	});					

	//request horizonal image layout
	$("#sideways").click(function() {
		buildImageTable($("#sideways").attr('checked'));	
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

});
