function controller() {
	
}
controller.prototype.registerRowHover = function(controlObj, rowDom) {
	rowDom.hover(function(){
		V.showTooltip(controlObj);
	}, function(){
		V.hideTooltip(controlObj);
	});
}
controller.prototype.registerRowClick = function(controlObj, rowDom) {
	/* set click event handlers for all columns of the specified row */
	var tds = rowDom.children();

	tds.click(function(){
		V.selectedObj = controlObj;
		V.highlightRow(rowDom);
		V.showDetails(controlObj, "statusListenerDetails");
	});

	/* add dsms from dsmList to control tab, unless they're already there */
	if (typeof(M.sConf.dsms[controlObj.tag]) == "undefined") {
		var newdsm = {};
		newdsm[controlObj.tag] = {};
		newdsm[controlObj.tag]["name"] = controlObj.name;
		newdsm[controlObj.tag]["host"] = controlObj.host;
		newdsm[controlObj.tag]["controls"] = {};

		V.generateDsmControl(newdsm, true);
	}
}
controller.prototype.handleClickControl = function(cObj, meth) {
	/* clicking on a control button calles the exec() command on that object */
	cObj.methods[meth].exec(cObj.tag);
}
controller.prototype.handleMouseMove = function(e) {
	/* Keep the toolip div just under the cursor at all times */
	$("#tooltip").css({"top":e.pageY+23+"px", "left":e.pageX+3+"px"});
}
controller.prototype.save = function(){
	/* create a save dialog on the fly */	
	var div_conf = $("<div>");

	div_conf.appendTo($("#dialogs"));
	$(div_conf).text("Save New Configuration?").dialog({"title":"Confirm", 
		"modal":true,
		"width":450,
		"close":function(){
			$(this).remove();
		},"buttons": {
		/* save button calls php script to write out JSON data to file */
		"Save":function(){
			$(this).dialog("title", "Saving..");
			$(this).load("saveconfig.php", 
				{"conf":M.serialize()},
				function(ret, stat) {
					if (stat=="success") {
						if (ret == 0) { location.reload(true);}
						else {
							$(div_conf).text("Failed, error code: "+ret
							+". Check permissions on config file.");
						}
					} else { 
						$(div_conf).text("Failed to contact server. error: "
							+stat);
					}
				}
			);
		},
		/* Show JSON button displays the JSON text in the dialog */
		"Show JSON":function(){
			$(this).text(M.serialize());
		},
		/* Cancel destroys the dialog */
		"Cancel":function(){
			$(this).remove();
		}
	}});
	
}
controller.prototype.tabSelect = function(e, u) {
	if (u.index == 0) {
		$("#saveButton").hide();
	} else {
		$("#saveButton").show();
	}
}
controller.prototype.keypress = function(e) {
	if ($("#all_tabs").tabs("option","selected") != 0) {return;}
	switch( e.which ) { 
	case 0: /* 'esc' key */
		V.selectedObj = undefined;
		V.hideDetails(); 
		break;

	case 112: /* 'p' key */
		/* clear the timer if it's still running */
		clearTimeout(V.pingTimer);

		/* send ping request to each dsm */
		for (var el in V.table.elements) {
			$.getJSON("ping.php?tag="+el+"&hostname="+M.dsms[el].host,
			function(d, ts){
				V.table.elements[d.tag].find("td.ping").text(d.message)
					.css("color",M.sConf.statusColor[d.status]);
			});
		}

		/* in 15 seconds, grey out the result */
		V.pingTimer = setTimeout(function(){ 
			$("td.ping").css("color","#BBB"); 
		}, 15000);
		break;	

	case 102: /* 'f' key */
		var filterDom = "#viewFilter";
		/* generate the filter once, otherwise show/hide the dom */
		if (V.filterGenerated) {
			$(filterDom).toggle();
		} else {
			V.generateFilter("#viewFilter");
			V.filterGenerated = true;
		}
		break;

	case 104: /* 'h' key */
		V.alert("<p><b>h</b> - Show this quick reference.</p>"
			+ "<p><b>Esc</b> - Clear details field.</p>"
			+ "<p><b>p</b> - Ping all items with hostname.</p>"
			+ "<p><b>f</b> - Show filter controls.</p>",
			"Keyboard Reference");
		break;
	default: break;
	}
}
controller.prototype.initialize = function() {
	/* set up built-in jquery UI event handlers */
	$("#all_tabs").tabs({"select":this.tabSelect});

	/* Add rows for each dsm in the static config. Then Retrieve the 
	   DSM list from DSMServer, adding rows for each new dsm */
	M.getListFromStaticConfig();
	M.getListFromDsmServer();
	
	/* Create input & event handlers for settings tab */
	$("#saveButton").click(this.save);
	V.generateSettings();

	/* Register event handler for Mouse Movement */
	$().mousemove(this.handleMouseMove);

	/* Register keypress event handler */
	$().keypress(this.keypress);

	/* Create status listener event */
	this.statListenCmd = new xmlrpcCommand("localhost", M.sConf.statusListenerPort, "GetClocks", 
		function(data, ts) {
		for (var d in M.dsms) {	
			var curData = data[d];
			var timetagstatus = 2, resptext = 'no data recieved';
			
			if (typeof(curData) != "undefined") {
				curData = curData.substr(0, 19).replace(/-/g, ' ');
				var timein = Date.parse(curData), now=new Date();
				var criticallimit = 6000, warninglimit = 4000;
				var timediff = -1* (timein - now.getTimezoneOffset()*60*1000 - now);
				timetagstatus =  (timediff < warninglimit) ? 0 : 1;
				timetagstatus = (timediff < criticallimit) ? timetagstatus : 2;
				resptext = curData;
			}
		
			V.table.updateRow(d,
				{"message":resptext, "status":timetagstatus});
		}	

	});

	/* Set timer for status listener timestamp event */
	this.statListenTimer = setInterval(function(){
		C.statListenCmd.exec('');
	}, M.sConf.timetagUpdateInterval * 1000);
 	C.statListenCmd.exec('');
	
	/* Set timer for status listener details event */
	this.statDetailTimer = setInterval(function(){
		if (V.selectedObj !== undefined) { V.showDetails(V.selectedObj, "statusListenerDetails"); }
	}, M.sConf.dsmdetailsUpdateInterval * 1000);

	/* Create update nagios event */
	this.nagiosUpdateTimer = setInterval(function(){
		$.getJSON("nagios.php", V.table.updateNag);
	}, M.sConf.nagiosUpdateInterval * 1000);
	$.getJSON("nagios.php", V.table.updateNag);
} 



/* 
  Functions Below are used for editing the config file.
*/
controller.prototype.removeDsm = function(that, tag) {
		delete M.sConf.dsms[tag];
		$(that).parent().parent().remove();

		$("#showDiv div").empty();
		$("#listDiv table").empty();
		$("#listDiv h3").text("Control List");
		
}

controller.prototype.addDsm = function(dName) {
		 
		/* get name & tag from input boxes, unless passed in */
		var newtag=(dName===undefined)? $("#newDsmInputT").val(): dName.tag;
		var newhost=(dName===undefined)? $("#newDsmInputH").val(): dName.host;
		var newname=(dName===undefined)? $("#newDsmInputN").val(): dName.name;

		if (dName !== undefined) { /* was a dynamic dsm */

			var newdsm = {};
			newdsm[newtag] = {};
			newdsm[newtag]["name"] = newname;
			newdsm[newtag]["host"] = newhost;
			newdsm[newtag]["controls"] = {};

			M.sConf.dsms[newtag] = newdsm[newtag];
			var newDom = "<img src='css/del.png' "
				+ "onclick='C.removeDsm(this,\"" + newtag  + "\");'/>";
			$(dName.dom).replaceWith(newDom);

			this.editDsm(newtag, newDom);	

		} else { 

			if (typeof(M.sConf.dsms[newtag]) == "undefined" && 
			typeof(M.dsms[newtag]) == "undefined") {

				/* validate input */
				var narray = ["#newDsmInputT", 
					"#newDsmInputH", "#newDsmInputN"];
				var good = true;
				for (var input in narray) {
					if ($(narray[input]).val() == "") { 
						$(narray[input]).effect('pulsate', {"times":2}, 200);
						good=false;	
					}
				}
				if (!good) {return;}
		
				/* create new item from valid input */	
				var newdsm = {};
				newdsm[newtag] = {};
				newdsm[newtag]["name"] = newname;
				newdsm[newtag]["host"] = newhost;
				newdsm[newtag]["controls"] = {};
				V.generateDsmControl(newdsm, false);
	
				M.sConf.dsms[newtag] = newdsm[newtag];
				$("#newDsmInputT,#newDsmInputH,#newDsmInputN,").val("");
	
			} else {
				V.alert('Tag must be unique!', "Error");
			}
		}

}

controller.prototype.editDsm = function(tag, that) {
		if (that) {V.highlightRow($(that));}
		$("#listDiv table, #listDiv h3, #showDiv div").empty();

		/* Get all the methods from dsm */
		var thisDsm = M.dsms[tag];
		if (thisDsm) {
			$("#listDiv h3").text(thisDsm.name);
			for (var i in thisDsm.methods) {
				$("#listDiv table").append("<tr><td>"+i
					+ "</td><td></td><td><img src='css/play.jpg' onclick='"
					+ "C.execDsmControl(\""+tag+"\",\""+i+"\")"
					+ "' /></td></tr>");
			}
		}

		/* Get any other methods from static config */
		if (M.sConf.dsms[tag]) {
			var dsm = M.sConf.dsms[tag].controls;

			$("#listDiv h3").text(M.sConf.dsms[tag].name);
			for (var i in dsm) {
				$("#listDiv table").append("<tr><td>"+i
					+ "<span onclick='C.showDsmControls(\""+ tag+"\",\""+i+"\")' "
					+ "class='little'>[edit]</span></td><td><img src='css/del.png'"
					+ " onclick='C.delDsmContrl(this,\""+tag+"\",\""+i+"\")"
					+ "' /></td><td><img src='css/play.jpg' onclick='"
					+ "C.execDsmControl(\""+tag+"\",\""+i+"\")"
					+ "' /></td></tr>");
			}
			
			$("#listDiv table").append("<tr style='height:35px'>"
				+ "<td colspan='2' style='border:none'></td></tr>"
				+ "<tr onclick='"
				+ "C.addDsmContrl(\"xmlrpc\",\""+tag+"\",false)"
				+ "'><td style='color:#888'>Add XML-RPC Command</td>"
				+ "<td></td><td><img src='css/add.png' /></td></tr>");

			$("#listDiv table").append("<tr onclick='"
				+ "C.addDsmContrl(\"shell\",\""+tag+"\",false)"
				+ "'><td style='color:#888'>Add Shell Command</td>"
				+ "<td></td><td><img src='css/add.png' /></td></tr>");
		}

}

controller.prototype.showDsmControls = function(tag, i) {
		var showDom = $("#showDiv div");
		var cont = M.sConf.dsms[tag].controls[i];

		if (typeof(cont) == 'string') {
			var inp = $("<input class='fulllength' />").val(cont).keyup(function(){
				C.editDsmContrl(tag, i, this.value);
			});
			showDom.empty().append("<h3>" + i  + "</h3>").append(inp);
		} else {
			full_cont = "<h3>" + i  + "</h3>"
				+ "host: <input id='hostInput' value='" +  cont.host 
				+ "' onkeyup='C.editDsmContrl(\""+tag+"\",\""+i+"\")'/>"
				+ "<br>port: <input id='portInput' value='" + cont.port 
				+ "' onkeyup='C.editDsmContrl(\""+tag+"\",\""+i+"\")'/>"
				+ "<br>method: <input id='methInput' value='" + cont.method
				+ "' onkeyup='C.editDsmContrl(\""+tag+"\",\""+i+"\")'/>"
				+ "<br>params: " + "<ul id='paramsList'>";
			
			for (var j in cont.params) {
				full_cont += "<li>" + j 
					+ ": <input value='" + cont.params[j] + "'"
					+ "' onkeyup='C.editDsmContrl(\""+tag+"\",\""+i+"\")' />"
					+ "<img src='css/del.png' onclick='C.delDsmContrlParam(this,\""+tag+"\",\""+i+"\",\""+j+"\")' />"
					+ "</li>";
			}
			full_cont += "</ul><span  class=\"add\""
				+ "onclick='C.addDsmContrlParam(\""+tag+"\",\""+i+"\")'"
				+ " ><i>Add Param</i><img src='css/add.png'/></span>";
			showDom.html(full_cont);
		}
}

controller.prototype.addDsmContrl = function(type, tag) {
		V.prompt("Enter the name of the new Command.", function(resp){
			M.sConf.dsms[tag].controls[resp] = 
			(type == "xmlrpc")? {"name":resp, "params":{}}: "";
	
			C.editDsm(tag);	
		});
}

controller.prototype.delDsmContrl = function(that, tag, name) {
		delete M.sConf.dsms[tag].controls[name];
		$(that).parent().parent().remove();
		$("#showDiv div").empty();
}

controller.prototype.editDsmContrl = function(tag, name, param) {
		if (typeof(param) == "string") {
			M.sConf.dsms[tag].controls[name] = param;
		} else {
			var newdsm = {
				"host": $("#hostInput").val(),
				"port": $("#portInput").val(), 
				"method": $("#methInput").val(),
				"params": {}
			}
			
			$("#paramsList li").each(function(){
				newdsm["params"][$(this).text().split(":")[0]] = $(this).children("input").val();
			});
			M.sConf.dsms[tag].controls[name] = newdsm;
		}
}

controller.prototype.addDsmContrlParam = function(tag, com) {
		V.prompt("Enter the name of the new Parameter.", function(cname){
			M.sConf.dsms[tag].controls[com].params[cname] = "0";
			C.showDsmControls(tag, com);
		});
}

controller.prototype.delDsmContrlParam = function(that, tag, com, cn) {
		delete M.sConf.dsms[tag].controls[com].params[cn];
		$(that).parent().remove();
		//this.showDsmControls(tag, com);	
}
controller.prototype.execDsmControl = function(tag, cmd) {
	
	var meth, params;

	/* check for method in dsm's internal methods */
	if (M.dsms[tag] !== undefined) {
		meth = M.dsms[tag].methods[cmd];
	}

	/* if we got here, and meth is defined, get the parameters and call exec */
	if (meth !== undefined) {
		V.prompt("Parameters for "+cmd+" : ", function(p){meth.exec(p)}, tag);

	} else {
		/* otherwise, create the command from static conf and exec it */
		var scmd = M.sConf.dsms[tag].controls[cmd];
		if (typeof(scmd) == "string") { /* it is a shell command */
			meth = new xmlrpcCommand(M.sConf.shell_host, 
				M.sConf.shell_port, "shell_exec");
			meth.exec([M.sConf.gnomeTerminalProfile,cmd,scmd]);
		} else {	/* its a native xmlrpc commmand */
			meth = new xmlrpcCommand(scmd.host, scmd.port, scmd.method);
			meth.exec(scmd.params);
		}
	}
	
}
