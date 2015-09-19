// download page
// Usage:
//     phantomjs download.js url [cookie]


var system = require('system');
var page = require('webpage').create();
var url = system.args[1];
var cookie = "";

if(system.args.length > 1) {
	cookie = system.args[2];
}

page.open(url, function(status) {
	
	if(status != "success") {
		console.error("status ", status);
		phantom.exit(1);
		return;
	}
	
	console.log(page.content);
	phantom.exit(0);
});
