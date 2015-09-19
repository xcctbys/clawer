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

page.settings.resourceTimeout = 5000; // 5 seconds
page.onResourceTimeout = function(e) {
  console.error(e.errorCode);   // it'll probably be 408 
  console.error(e.errorString); // it'll probably be 'Network timeout on resource'
  phantom.exit(1);
};

page.open(url, function(status) {
	
	if(status != "success") {
		console.error("status ", status);
		phantom.exit(1);
		return;
	}
	
	console.log(page.content);
	phantom.exit();
});
