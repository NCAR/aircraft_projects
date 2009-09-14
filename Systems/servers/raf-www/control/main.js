//  == global vars ==
var statusText = new Array( 'OK'  ,'WARNING','CRITICAL','UNKNOWN','Updating...');
var statusColor = new Array('#0A0', '#AA0'  ,'#A00'    ,'#505'   ,'#999' );
var dsmlist = new Array();
var DsmDetail = { en: false, list: [100], 
	next: function(){ var a=this.list.shift(); this.list.push(a); return a; }
}

/********************************************
 *      == jquery init function ==          *
 * bind all events here, as well as setting *
 * up timer inervals for looping functions  *
 ********************************************/
$(function(){
	//build table rows for the nagios items:
	var startStop = new Array("start", "stop");
	for (var item in nagiosItems) {
		makerow(0, 'nagItem'+item, nagiosItems[item].name, 4, "", startStop)
	}
	
	//build tabe rows for XMLRPC items:
	buildXMLRPCtable(false);

	//get status updates from nagios status file now, and every X seconds
	updateFromNagios();
	setInterval("updateFromNagios()", nagiosUpdateInterval*1000);

	//get timetags updates now and every X seconds
	updateTimetags();
	setInterval("updateTimetags()", timetagUpdateInterval*1000);

	//get detailed DSM data every X seconds
	setInterval("updateDsmDetails(true)", dsmdetailsUpdateInterval*1000);

	//enable hover states on buttons
	$('.ui-corner-all').css("cursor", "pointer").hover(
		function() { $(this).addClass('ui-state-hover'); }, 
		function() { $(this).removeClass('ui-state-hover'); }
	);

	//set test voltage button
	$('#testvolter').click(function() {
		if ($('.ui-selected').size() != 1) {
			$('#dsm-dialog')
				.html('Please Select a single DSM')
				.dialog('open');
		} else {
			var hname = $('.ui-selected:first').attr('id').split("-", 1);
			$('#dsm-dialog').text("Loading...").dialog('open');
			$.get(
				"xmlrpcHTML.php",
				{'port':'30003', 'method':'List_NCAR_A2Ds', 'rcvr':'rcvr', 'host':hname},
				function(data){
					var warning="<p><strong style='color:red'>OPERATION NOT YET VERIFIED! USE ADADS</strong></p>";
					$('#dsm-dialog').html(warning + data);
					$('form.vsel').attr('action', "../adads/control_dsm.php");
				});
		}
	});

	//calibrate button
	$('#calibrater').click(function() {
		$('#dsm-dialog')
			.html('not yet implemented')
			.dialog('open');
	});

	//soft reboot button
	$('#rebooter').click(function() {
		if ($('.ui-selected').size()) {
			$('#reboot-dialog')
				.html('<p><strong style="color:red">'
					+'Are you sure you want to ssh-reboot the following DSM(s):'
					+'</strong></p>')
				.dialog('option', 'buttons', { 
					'Reboot DSM(s)' : function(){
						rebootSelectedDsms(this);
					}, 
					'Cancel' : function () {
						$(this).dialog('close'); }
				});

			$('.ui-selected').each(function(idx, item) {
				var dsmID = item.id.split("-", 1);
				$('#reboot-dialog')
					.append(idx + ": " 
					+ $("#"+item.id+" td:first").text()
					+ " (" + dsmlist[dsmID] + ")<br />");
			});
		} else {
			$('#reboot-dialog')
				.html('No DSM(s) Selected! ')
				.dialog('option', 'buttons', {
					'Close' : function () { $(this).dialog('close'); }
				});
		}
		$('#reboot-dialog').dialog('open');

	});	

	//ping button
	$('#pinger').click(function() {
		$('.ui-selected').each(function(idx, item) {
			pingDSM(item.id.split("-", 1));
		});
	});

	$('#refreshNag').click(function(){updateFromNagios();});
	$('#refreshXMLRPC').click(function(){buildXMLRPCtable(true);});

	//make xmlrpc items selectable
	$(".sel").selectable({
		filter: 'tr',
		stop: function(event, ui) {
			DsmDetail.en = true;
			DsmDetail.list = [];
			$('.ui-selected').each(function(i) {
				var curID = $(this).attr('id').split("-",1);
				DsmDetail.list.push(curID);
			});
			updateButtonState();
			updateDsmDetails(false);
		},
	});

	//make div 'dsm-dialog' into a jquery dialog box
	$('#dsm-dialog').dialog({width: 700, autoOpen: false, modal: true, buttons: {
			'Close' : function () {
				$(this).dialog('close');
			}
		} });

	//make div 'reboot-dialog' into a jquery dialog box
	$('#reboot-dialog').dialog({autoOpen: false, modal: true  });

	//set correct states on action buttons
	updateButtonState();
});
function buildXMLRPCtable(clear) {

	if (clear) {
		$("#controls1 tbody tr").remove();
		DsmDetail.en = false;
	}

	//build table rows for xmlrpc items
	for (var item in xmlrpcItems) {
		var num = ((item-0)+100);
		makerow(1, num, xmlrpcItems[item].name, 3, "", null); 
		dsmlist[num] = 'localhost'; 
	}

	//ajax get json array of dsms, finnish the table with these:
	$.getJSON("xmlrpcJSON.php", function(data){
		var i=0;
		for (var host in data) {
			dsmlist[i] = host;
			makerow(1, i, data[host], 3, '&lt;-timetag-&gt;', null);
			i++;
		}
	});

}
function updateButtonState(){
	state = Math.max.apply(0,DsmDetail.list) >= 100;
	$("#rebooter, #testvolter")
		.attr("disabled", state)
		.css('color', state? "#888" : "#222");
}
function makerow(table, id, name, stat, message, options) {
//function makes a new row in a table, setting the ids and button actions
	var newrow = "<tr id='" + id + "-row'><td>" + name + "</td><td id='" + id;
	newrow += "-status' style='font-weight:bold;color:";
	newrow += statusColor[stat] + ";'>" + statusText[stat] + "</td>";
	newrow += "<td id='" + id + "-message' class='message'>" + message + "</td>";
	newrow += "<td id='" + id + "-control'>";
	for (var a in options) {
		newrow += "<button type='button' class='ui-state-default ";
		newrow += "ui-corner-all' onclick=\"execcontrol('";
		newrow += options[a] + "', '" + name + "')\">" + options[a] + "</button> ";
	}
	newrow += "</td></tr>";
	$("#controls"+table).append(newrow);
}
function execcontrol(action, name) {
//ajax function to call commands.php on server
	$('#reboot-dialog')
		.html('<p><strong style="color:#600">Are you sure you want to '
		+action+' '+name+'?</strong></p><p><input type="checkbox" id="keepTermOpen" /><label for="keepTermOpen">Keep terminal open after command finishes</label></p>')
		.dialog('option', 'buttons', { 
			'No' : function () { 
				$(this).dialog('close'); 
			},
			'Yes': function(){
				var profile = $('#keepTermOpen').attr('checked')? "stayopen": "default";
				$.get("commands.php", {"command":name, "action":action, "profile":profile });
				$(this).dialog('close'); 
			}
	 }).dialog('open');
}
function updateDsmDetails(highlight){
	if (DsmDetail.en) {
		var curDsmId = DsmDetail.next();
		var arg = (curDsmId >= 100) ?
		xmlrpcItems[curDsmId-100].xmlrpcTag : dsmlist[ curDsmId ];

		if (highlight) {
			$("#"+curDsmId+"-row").effect("highlight", {}, 500);
		}

		$.get("xmlrpcHTML.php?port=30006&method=GetStatus&args=" + arg,
		function(data){
			$('#dsm-table').html(data);
		});
	} else {
		$('#dsm-table').text('');
	}
}
function updateFromNagios(){
//this function updates the nagios status table by calling nagiosJSON.php
	$.getJSON("nagiosJSON.php", function(data){
		for (var item in nagiosItems) {
			var ni = nagiosItems[item];
			var newStat = 0, newMesg = '';
			for (var term in ni.nagiosTags) {
				var nt = ni.nagiosTags[term];
				newStat = Math.max(newStat, data['status'][nt]);
				newMesg += data['message'][nt]  + "; ";
			}
			$("#nagItem"+item+"-status")
				.text(statusText[newStat])
				.css('color', statusColor[newStat]);
			$("#nagItem"+item+"-message")
				.text(newMesg);
		}	
	 });
}
function updateTimetags() {
//this function updates the xmlrpc timetags, by calling xmlrpcJSON.php
	$.getJSON(
		"xmlrpcJSON.php",
		{'port':'30006', 'method':'GetClocks'},
		function(data){
			for (var i in dsmlist) {
				var curData = data[dsmlist[i]];
				var timetagstatus = 2, resptext = 'no data';
				if ( i >= 100 ) { curData = data[xmlrpcItems[i-100].xmlrpcTag]; } 

				if (typeof(curData) != "undefined") {
					curData = curData.substr(0, 19).replace(/-/g, ' ');
					var timein = Date.parse(curData), now=new Date();
					var criticallimit = 6000, warninglimit = 4000;
					var timediff = -1* (timein - now.getTimezoneOffset()*60*1000 - now);
					timetagstatus =  (timediff < warninglimit) ? 0 : 1;
					timetagstatus = (timediff < criticallimit) ? timetagstatus : 2;
					resptext = curData;
				}

				$("#"+i+"-message")
					.text(resptext)
					.css('color', (statusColor[timetagstatus]));
				$("#"+i+"-status")
					.text(statusText[timetagstatus])
					.css('color', (statusColor[timetagstatus]));
		}
	});
}
function pingDSM(rowID) {
//pings the dsm in the specified row, updating the table on completion
	$("#"+rowID+"-control").text(statusText[4]).css('color', (statusColor[4]));
	$.getJSON("commands.php", {'command':'ping', 'hostname':dsmlist[rowID]},
		function(data){
			$("#"+rowID+"-control")
				.text(data['message'])
				.css('opacity', 1) 
				.css('color', (statusColor[data['status']]));
			/*$("#"+rowID+"-status")
				.text(statusText[data['status']])
				.css('color', (statusColor[data['status']]));*/
			/*setTimeout("$('#"+rowID+"-control').css('opacity', 0.6);", 5000);*/
	});
}
function rebootSelectedDsms(that) {
//calls commands.php with the hostname of the dsm. commands.php
// will ssh into that dsm and issue the 'reboot' command
	$(that)
		.text('')
		.dialog('option', 'buttons', { 
			'Close' : function () { $(this).dialog('close'); }
		 });

	$('.ui-selected').each(function(idx, item) {
		var dsmID = item.id.split("-", 1);
		var hostname = dsmlist[dsmID];
			$(that).append('rebooting '+hostname+'...<br/>');
		$.get("commands.php", {'command':'reboot', 'hostname':hostname});
	});

	$(that).dialog('close');
}

