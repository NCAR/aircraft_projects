function view() {
	this.table = new viewTable("#viewTable");

	this.dialogDiv = $("#dialogs");
	this.tooltiptimer;
	this.pingTimer;
	
	/* show filter console */
	//this.generateFilter("#viewFilter");
}
view.prototype.highlightRow = function(rowDom) {
	rowDom.siblings().children().removeClass("trSelTd");
	rowDom.children().addClass("trSelTd");
}
view.prototype.showControls = function(controlObj) {
	var controldom = $("#controls").empty();

	for (var i in controlObj.methods){
		var newButton = $("<input type='button' value='" + i 
			+ "' class='ui-corner-all ui-state-default'/>");
		newButton.click(function(){C.handleClickControl(controlObj, i);});
		newButton.hover(
			function(){
				V.showTooltip(controlObj, i);
			}, function(){
				V.hideTooltip();
			}
		);
		controldom.append(newButton);
	}

	controldom.show(); 
}
view.prototype.hideControls = function() { $("#controls").hide(); }

view.prototype.showDetails = function(controlObj, method) { 
	controlObj.methods[method].exec(controlObj.tag,function(data) {
		$("#details").html(data).show();
	});
}
view.prototype.hideDetails = function() { $("#details").hide(); }
             
view.prototype.showTooltip = function(controlObj) { 
	this.tooltiptimer = setTimeout(function() {
		$("#tooltip").html("Tag: "+controlObj.tag).fadeIn(); 
	}, M.sConf.toolTipTimer * 1000);
}
view.prototype.hideTooltip = function() { 
	clearTimeout(this.tooltiptimer);
	$("#tooltip").hide(); 
}

/* alert function displays a pop-up box with text */
view.prototype.alert = function(text_in, title_in) {
	var text = text_in? text_in: "Alert";
	var title = title_in? title_in: "Attention";

	var div = $("<div>");
	div.appendTo(this.dialogDiv);
	$(div).html(text).dialog({"title":title, "close":function(){
		$(this).remove();
	}});
}

/* prompt function displays a pop-up box with input, calling the supplied
   callback function with the user-specified data */
view.prototype.prompt = function(text_in, callback, initial) {
	var text = text_in? text_in: "Prompt";

		"<input id='jqPrompt_data' class='fulllength' value='"
		+ (initial === undefined? "": initial)  + "'/>"

	var div = $("<div>");
	div.appendTo(this.dialogDiv);
	$(div)
	.append("<input id='jqPrompt_data' class='fulllength' value='"
		+ (initial === undefined? "": initial)  + "'/>" )
	.dialog({
		"title":text, 
		"modal":true,
		"close":function(){
			$(this).remove();
		},
		"buttons":{
			"Ok":function(){
				ret_data = $("#jqPrompt_data").val();
				if (ret_data.toLowerCase() == "null") {
					callback();
					$(this).dialog('close').remove();
				} else if (ret_data != "") {
					callback(ret_data);
					$(this).dialog('close').remove();
				} else {
					$(this).effect('pulsate', {"times":2}, 200);
				}
			},
			"Cancel":function(){
				$(this).dialog('close').remove();
			}
		}
	});
}

/* function displays a pop-up box with input, calling the supplied
   callback function with the user-specified data */
view.prototype.promptParams = function(dsmtag, methname) {
	var dsmObj = M.dsms[dsmtag];
	var method = dsmObj.methods[methname];

	var text = "Parameters for "+methname+" on "+dsmObj.name;

	var div = $("<div>");
	div.appendTo(this.dialogDiv);

	$(div)
	.append("<span class='little'>[Send No Parameters]</span>")
	.dialog({
		"title":text, 
		"modal":true,
		"width":600,
		"close":function(){
			$(this).remove();
		},
		"buttons":{
			"Send":function(){
				var pNames = $(this).children().filter("input:even");
				var pValues = $(this).children().filter("input:odd");

				if (pNames == []) {
					method.exec();
				} else {
					var pMap = {};
					if (typeof(pNames) != "object") {
						pMap[pNames.val()] = pValues.val();	
					} else {
						for (var n = 0; n < pNames.length; n++) { 
							pMap[pNames[n].value] = pValues[n].value; 
						}
					}
					method.exec(pMap);
				}
				$(this).dialog('close').remove();
			},
			"Add Parameter":function(){
				$(this).append("Param: <input class='param'/>")
				       .append("Value: <input class='value'/><br />")
				       .find("span").remove();
			},
			"Cancel":function(){
				$(this).dialog('close').remove();
			}
		}
	});
}

function viewTable(sel) {
	this.head = ["Name","Host","Type","Status","Message"];
	this.elements = {}; /* tag:DOM element maps */
	this.filter = {"apply":false, "col":"Name", "search":'', 
		"show":"false", "i":false};

	/* create HTML table, and append to the parent DOM element */
	this.dom = $("<table>");

	var baseTable = "<thead><tr>";
	for (var th in this.head){ 
		baseTable += "<th scope='col'>" + this.head[th] /*
		+ "<span class='ui-icon ui-icon-carat-2-n-s' onclick='"
		+ "V.table.sort(this, \"" + this.head[th]  + "\");'>" */
		+ "</th>";
	}
	baseTable += "<th scope='col></th></tr></thead><tbody />";
	this.dom.append(baseTable);

	this.parentDom = $(sel);
	this.parentDom.append(this.dom);
}
viewTable.prototype.sort = function(icon,column) {
	/* decide which way to sort the table */
	var reverse = $(icon).hasClass("ui-icon-carat-1-n");

	/* set all icons to double arrow */
	V.table.dom.find("span.ui-icon").each(function(){
		this.className = "ui-icon ui-icon-carat-2-n-s";
	});
	
	/* set the selected icon to north or south */
	icon.className = "ui-icon ui-icon-carat-1-"+ (reverse? "s":"n"); 
	
	/* TODO actually sort the table! */
	
	
}
viewTable.prototype.applyFilter = function(row) {
	//(row.find("td."+this.filter.col.toLowerCase()+":first")
	//.html().indexOf(this.filter.search) != -1)?

	var re=new RegExp(this.filter.search,(this.filter.i?"":"i"));
	re.test(row.find("td."+this.filter.col.toLowerCase()+":first")
	.html())?
		(this.filter.show == "true"? row.hide(): row.show()): 
		(this.filter.show == "true"? row.show(): row.hide());
}
viewTable.prototype.applyFilterAll = function() {
	if (! this.filter.apply) {return;}
	for (var i in this.elements) {
		this.applyFilter(this.elements[i]);
	}

	$("tr.nagios").each(function() {
		V.table.applyFilter($(this));
	});
}
viewTable.prototype.register = function(name, host, tag, type) {
	var newRow = $("<tr>");
	this.elements[tag] = newRow;

	newRow.append("<td class='name'>" + name
		+ "</td><td class='host'>" + host + "</td><td class='type'>" + type 
		+ "</td><td class='status'>"
		+ "</td><td class='message'></td><td class='ping'></td>" );

	this.dom.append(newRow);
	return(newRow);
}
viewTable.prototype.updateRow = function(tag, update){
	if (this.elements[tag] === undefined) {return;}

	if (typeof(update.message) != "undefined") {
		this.elements[tag].find("td.message:first").html(update.message);
	}
	if (typeof(update.status) != "undefined") {
		this.elements[tag].find("td.status:first")
			.html(M.sConf.statusText[update.status])
			.next().andSelf().css("color", 
				M.sConf.statusColor[update.status]);
	}

	if (this.filter.apply) { this.applyFilter(this.elements[tag]); }
}
viewTable.prototype.updateNag = function(d, ts) {
	/* check for successful ajax call */
	if (ts != "success") {
		V.alert("message: "+ts, "Error");
	} else {
		V.table.dom.find("tr.nagios").remove();
		V.table.dom.prepend("<tr class='nagios' ><td colspan='6' "
			+ "class='blank'></td></tr>");

		for (var n in d.status) {
			var st = M.sConf.statusText[d.status[n]];
			var sc = M.sConf.statusColor[d.status[n]];
			var mess = d.message[n];

			var newRow = $("<tr class='nagios'>");

			newRow.append("<td class='name' colspan='2'>" + n
				+ "</td><td class='type'>Nagios"
				+ "</td><td class='status' style='color:" + sc + ";'>" + st
				+ "</td><td colspan='2' class='message' style='color:" + sc 
				+ ";'>" + mess + "</td>" );

			V.table.dom.prepend(newRow);
			C.registerRowHover({"tag":n},newRow);
		}

		/* if there is an active filter, apply it to these new updates */
		if (V.table.filter.apply) { V.table.applyFilterAll(); }
	}
}
view.prototype.generateSettings = function() {
	
	for (var key in M.sConf) {
		var value = M.sConf[key];

		if (key == "dsms") {
			this.generateDsmControl(value, false);
		} else if (typeof(value) == "object") {
			for (var i in value) {
				$("#cg_list").append(	
					"<tr><td>"+key+" ["+i+"]</td><td><input value='"
					+ value[i]+"' onkeyup='M.sConf."+key+"["+i+"]=this.value;'/>"
					+ "</td></tr>");
			}
		} else {
			var newtr = $("<tr>");
			newtr.html("<td>"+key+"</td><td><input value='"
				+value+"' onkeyup='M.sConf."+key+"=this.value;'/></td>");
			newtr.appendTo("#cg_list");
		}

	}

}
view.prototype.generateDsmControl = function(slObj, dynamic) {
	/* Add an entry to the table for each item in the config file */
	for (var l in slObj) {
		var z = slObj[l];

		/* if the dsm in dynamic (from dsmserver list), then we need a "+" 
		   instead of an "x" to 'add' the dynamic dsm to the static list */
		var icon = dynamic?
			"<td><img src='css/add.png' onclick='C.addDsm({\"tag\":\""
			+ l + "\",\"name\":\"" + z.name + "\",\"dom\":this})'/></td></tr>":

			"<td><img src='css/del.png' onclick='C.removeDsm(this,\""
			+ l + "\")'/></td></tr>";

		$("#cd_list").append("<tr><td onclick='C.editDsm(\""+l+"\",this)'>"
				+ z.name +"</td>"+ "<td onclick='C.editDsm(\""+l+"\",this)'>" 
				+ l +"</td>"+ "<td onclick='C.editDsm(\""+l+"\",this)'>" 
				+ z.host + "</td>" + icon );
	}

}
view.prototype.generateFilter = function(sel) {
	var column = $("<select class='ui-corner-all' />");
	var match = $("<select />");
	var search = $("<input />");
	var engage = $("<input type='checkbox' id='enChck' checked />");
	var casesense = $("<input type='checkbox' id='iChck' />");
	
	for (var i in this.table.head) {
		column.append("<option value='"+this.table.head[i]+"' >"
		+this.table.head[i]+"</option>");
	}
	
	match.append("<option value='false' >Matches</option>");
	match.append("<option value='true' >Does Not Match</option>");

	$(sel)
		.append('<strong id="fltrLbl">Table Filter </strong>')
		.append(casesense)
		.append("<label for='iChck'>Match Case</label>")
		.append(engage)
		.append("<label for='enChck'>Enable</label><br>")
		.append(column)
		.append(match)
		.append(search)
		.append('<span class="little">[regular expressions supported]</span>');

	V.table.filter.apply = true;

	column.change(function() { 
		V.table.filter.col = $(this).val(); 
		V.table.applyFilterAll();
	});
	match.change(function() { 
		V.table.filter.show = $(this).val(); 
		V.table.applyFilterAll();
	});
	casesense.change(function() { 
		V.table.filter.i = $(this).is(":checked"); 
		V.table.applyFilterAll();
	});
	engage.change(function() { 
		var checked = $(this).is(":checked"); 
		V.table.filter.apply = checked;
		if (checked) { V.table.applyFilterAll(); }
		else { $("table tr").show(); }
	});
	search.keyup(function() {
		V.table.filter.search = $(this).val();	
		V.table.applyFilterAll();
	});

	$(sel).show();
}

