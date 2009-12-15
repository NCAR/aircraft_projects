/* These will be pointers to the Model, View and Controller objects */
var M,V,C;

/* This function is executed on page load, analogous to int main() */
$(function() {

	/* create M,V,C objects */
	M = new model();
	V = new view();
	C = new controller();

	/* get configuration file and parse as JSON object */
	$.getJSON('js/config.json', function(j) { 
		/* this annonymous function is executed after the JSON config
		   file is loaded. */
		M.sConf=j; /* store the static configuration in the Model */
		C.initialize(); /* Register event handlers and Start timed events */
	});

});

/*
   This file contains my 'virtual' classes (sort of a misnomer in javascript).
   They are mainly used as templates for sub-classes in the model
*/


/*===============================*
 *      xmlrpcCommand Class      *
 *===============================*/

/* constructor for xmlrpcCommand. Allows specification of:
   host, port, method, and callback function */
function xmlrpcCommand(hostname, portnum, methodName, callback_func) {

	this.host = hostname;
	this.port = portnum;
	this.method = methodName;

	/* if store specified callback */
	this.callback = callback_func; 

}

/* .exec function generates a valid url and sends the ajax request to 
   xmlrpc.php to handle */
xmlrpcCommand.prototype.exec = function(params, callback_func) {

	/* choose correct callback function */
	var cback = this.callback_default;
	if (typeof(callback_func) == 'function') {
		cback = callback_func; 
	} else if (typeof(this.callback) == 'function') {
		cback = this.callback; 
	}

	/* generate url for proper HTTP GET request */
	var argstring='';
	if ( typeof(params) == 'object' ) {
		/* make params an associative array before sending */
		for (var i in params) {
			argstring += 'args[' + i + ']=' + params[i] + "&";
		}
	} else if ( typeof(params)!=undefined ) {
		/* otherwise the params' .toString() will be called, this is
		   valid for all other datatypes (number, string, etc) */
		argstring = 'args='+params;
	}
	
	/* send AJAX request */
	$.getJSON('xmlrpc.php'
		+'?port='+this.port
		+'&host='+this.host
		+'&method='+this.method
		+'&'+argstring, 
		cback);

}

/* .callback is the default callback function for xmlrpcCommands. It will
   call model.alert with appropriate status message */
xmlrpcCommand.prototype.callback_default = function(dataObj, statusString) {

	if (dataObj.faultCode) {
		/* show an error dialog box if a faultCode was returned */
		V.alert("faultCode: " + dataObj.faultCode + 
			"<br/> faultString: " + dataObj.faultString, "Error");

	} else if (typeof(dataObj) == 'object') {
		/* otherwise, show data returned in human-readable form */
		var outputstring='';
		for (var i in dataObj) {
			outputstring+=(i+": "+dataObj[i]+"<br>");
		}
		V.alert(outputstring,"Response");

	} else {
		/* otherwise, show data returned as string */
		V.alert( dataObj, "Response");
	}
}


/*===============================*
 *      controllable Class       *
 *===============================*/

/* constructor for controllable. Allows specification of:
   name, and tag */
function controllable(name_in, tag_in) {
	this.name = name_in; /* human intentifier. */
	this.tag = tag_in;   /* machine indentifier. */
	this.methods = {};   /* container of xmlrpcCommand objects */

	this.defaultHost = "localhost";
	this.defaultPort = 30003;
	this.defaultMethod = "help";
}

/* function to add a method to the methodlist, setting defaults for parameters
   that are not specified */
controllable.prototype.addMethod = function(paramsObj) { 
	/* apply host, port and method if specified, otherwise use defaults */
	var newHost = paramsObj.host? paramsObj.host: this.defaultHost;
	var newPort = paramsObj.port? paramsObj.port: this.defaultPort;
	var newMethod = paramsObj.method? paramsObj.method: this.defaultMethod;
	var name = paramsObj.name? paramsObj.name: newMethod;

	/* make sure we do not overwrite methodnames */
	if ( typeof(this.methods[name]) != "undefined" ) {
		/* add salt (random number) to name until we find a free name */
		V.alert("namespace conflict");
		return;
		//name = newMethod + Math.random();
	}

	/* xmlrpcCommand ctor will apply callback only if it's a function */
	var newMethod = new xmlrpcCommand(newHost, newPort, newMethod, 
		paramsObj.callback);

	/* add the new method to the method list */
	this.methods[name] = newMethod;
}

/* The following three functions do not exist for the 'virtual' 
   implementation of controllable. These functions are merely placeholders
   to avoid the consequenses of calling a non-existant function. 
   TODO: They could probably be removed after the site is fully developed
*/
controllable.prototype.getMethods = function() { alert("no getMethod()!"); }
controllable.prototype.getParams = function() { alert("no getParams()!"); }
controllable.prototype.getHelp = function() { return "no getHelp()!" }

