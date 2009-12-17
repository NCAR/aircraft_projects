function model() {

	/* create empty nagios and dsm lists */
	this.nagios = {};
	this.dsms = {};
	
	this.sConf = {};          /* Holds static configuration */
}
model.prototype.getListFromDsmServer = function() {
	var getList = new xmlrpcCommand("localhost", M.sConf.dsmServerPort, "GetDsmList");
	getList.exec("", function(data, ts) {

		if (ts != "success" || data.faultCode !== undefined) {
			V.alert("error fetching DSM List");
		} else {
			for (var Dsm in data) {
				/* add dsm, only if it's not already specified in sConf */
				if (M.sConf.dsms[Dsm] === undefined) {
					M.addDsm(data[Dsm], Dsm, Dsm, true);
				}
			}
		}
	});
}
model.prototype.getListFromStaticConfig = function() {
	for (var Dsm in this.sConf.dsms) {
		this.addDsm(this.sConf.dsms[Dsm].name, Dsm, 
			this.sConf.dsms[Dsm].host, false);
	}
}
model.prototype.addDsm = function(dsmName, dsmTag, dsmHost, dynamic){
	/* create a new controllable object to represent the DSM */
	var newDsm = new controllable(dsmName, dsmTag, dsmHost);

	/* add the new DSM to the View (table) */
	var newRowDom = V.table.register(dsmName, dsmHost, dsmTag, 
		(dynamic? "Dsm": "Static"));	

	/* let controller handle events related to this row */
	C.registerRowClick(newDsm, newRowDom);
	C.registerRowHover(newDsm, newRowDom);
	
	// TODO:
	// write get_params query
	// write get_help query

	/* add methods using xmlrpc introspection */
	newDsm.getMethods();

	/* add method to get detailed status from statuslistener */
	newDsm.addMethod({ 
		"name":"statusListenerDetails",
		"host":"localhost",
		"port": M.sConf.statusListenerPort,
		"method":"GetStatus"
	});

	/* add this dsm to the Model's dsm list */
	this.dsms[dsmTag] = newDsm;
}

model.prototype.eachDsm = function(inFunc) {

	/* call inFunc N times, setting the context of the function to
	   each respective dsm in the dsm list */
	for (var thisDsm in this.dsms) {
		inFunc.call(this.dsms[thisDsm]);
	}

}

/* serialize function takes an object as input and returns a string in valid 
   JSON form representing that object - used for storing the object */
model.prototype.serialize = function(_obj) {
   switch (typeof _obj)
   {
      // numbers, booleans, and functions are trivial:
      // just return the object itself since its default .toString()
      // gives us exactly what we want
      case 'number':
      case 'boolean':
      case 'function':
         return _obj;
         break;

      // for JSON format, strings need to be wrapped in quotes
      case 'string':
         return '\"' + _obj + '\"';
         break;

      case 'object':
         var str;
         if (_obj.constructor === Array || typeof _obj.callee !== 'undefined')
         {
            str = '[';
            var i, len = _obj.length;
            for (i = 0; i < len-1; i++) { 
				str += this.serialize(_obj[i]) + ','; 
			}
            str += this.serialize(_obj[i]) + ']';
         }
         else
         {
            str = '{';
            var key;
            for (key in _obj) {
				str += '"' + key + '":' 
				+ this.serialize(_obj[key]) + ',';
			}
            str = str.replace(/\,$/, '') + '}';
         }
         return str;
         break;

      default:
         return this.serialize(this.sConf);
         break;
   }
}
