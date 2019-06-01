/*
Injects Captions 4 Sounds.js into YouTube page.

Content scripts are executed in an isolated environment, so to manipulate the player
need to execute script into the page.

http://stackoverflow.com/questions/9515704/building-a-chrome-extension-inject-code-in-a-page-using-a-content-script

https://developer.chrome.com/extensions/content_scripts.html#execution-environment
*/

var s = document.createElement('script');
s.src = chrome.extension.getURL("caption4sounds.js");

var video_id;
// var transcript;

s.onload = function() {
    this.parentNode.removeChild(this);

};

(document.head||document.documentElement).appendChild(s);

window.addEventListener("ReceiveFromPage", function(evt) {
	// chrome.runtime.sendMessage(evt.detail);
	video_id = evt.detail;
	console.log('got video id from page: ' + video_id);
}, false);

chrome.runtime.onMessage.addListener(
	function(request, sender, sendResponse) {
		if( request.message === "clicked_browser_action" ) {
			console.log('sending to background: ' + video_id);
			chrome.runtime.sendMessage({'message': 'video_id', 'video_id': video_id});
			// console.log(window.location.search.split('v=')[1]);
        }
        else if(request.message === "result") {
            console.log('got response from api: ' + request.result.audio_filename);
            var transcript = request.result.results;
            var event_response = new CustomEvent("PassToPage", {detail: transcript});

            window.dispatchEvent(event_response);

        }
	}
);

injectFont = function() {
    //inject the custom font for controls
    //http://stackoverflow.com/questions/4535816/how-to-use-font-face-on-a-chrome-extension-in-a-content-script
    //other css and font files are not loaded
    var fa = document.createElement('style');
    fa.type = 'text/css';
    fa.textContent = '@font-face { font-family: youtube-controls; src: url("'
            + chrome.extension.getURL('font/youtube-controls.woff')
            + '"); }';
    document.head.appendChild(fa);
}

injectFont();