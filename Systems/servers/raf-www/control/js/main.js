/* These global variables will be pointers to the 
   Model, View and Controller singletons */
var M,V,C;


/*===============================*
 *          main function        *
 *===============================*/
/* This function is executed on page load, analogous to int main() */
$(function() {

	/* instantiate M,V,C objects */
	M = new model();
	V = new view();
	C = new controller();

	/* get configuration file using the jQuery ajax GET function. 
	   Then parse the result as JSON object, j */
	$.getJSON('js/config.json', function(j) { 
		/* this annonymous function is an asynchronous callback which 
		   will be executed when the ajax GET query returns. */

		M.sConf=j; /* store the static configuration in the Model */
		C.initialize(); /* Register event handlers and Start timed events */
	});

});


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
	} else if ( typeof(params) != "undefined" ) {
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
function controllable(name_in, tag_in, host_in) {
	this.name = name_in; /* human intentifier. Should be descriptive*/
	this.tag = tag_in;   /* statusListener indentifier. MUST BE UNIQUE */
	this.host = host_in; /* dns hostname. Used for ping test. */
	this.methods = {};   /* container for xmlrpcCommand objects */

	this.defaultHost = "localhost";
	this.defaultPort = M.sConf.dsmXmlRpcPort;
	this.defaultMethod = "help";

	/* Special Cases TODO: in config file somewhere? */
	if (tag_in == "dsm_server") {this.defaultPort = M.sConf.dsmServerPort;}
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
		/* avoid overwrite existing methods */
		V.alert("namespace conflict");
		return;
	}

	/* xmlrpcCommand ctor will apply callback only if it's a function */
	var newMethod = new xmlrpcCommand(newHost, newPort, newMethod, 
		paramsObj.callback);

	/* add the new method to the method list */
	this.methods[name] = newMethod;
}

/* The following three functions allow the site to dynamicly add methods
   that are specifed using introspection.
*/
controllable.prototype.getMethods = function() { 
	var that = this;
	var introspect = new xmlrpcCommand(this.host, this.defaultPort, 
	"system.listMethods", function(names,ts) { 
		if (ts != "success" || names.faultCode !== undefined) {return;}	
		for (i in names) {
			that.addMethod({ "method":names[i] });
		}
	});
	introspect.exec();
}
controllable.prototype.getParams = function() { alert("no getParams()!"); }
controllable.prototype.getHelp = function() { return "no getHelp()!" }

