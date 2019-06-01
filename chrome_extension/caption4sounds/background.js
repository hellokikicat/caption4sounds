var video_id

// Called when the user clicks on the browser action.
chrome.browserAction.onClicked.addListener(function(tab) {
  // Send a message to the active tab
	chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
		var activeTab = tabs[0];
		chrome.tabs.sendMessage(activeTab.id, {"message": "clicked_browser_action"});
  });
});

chrome.runtime.onMessage.addListener(
	function(request, sender, sendResponse) {
		if( request.message === "video_id" ) {
			video_id = request.video_id
			console.log('getting video '+video_id)
			fetch('http://3.15.60.80:8501/caption/'+video_id).then(r => r.text()).then(function(result) {
				console.log('got response from api: ' + result)
				chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
					var activeTab = tabs[0];
					chrome.tabs.sendMessage(activeTab.id, {"message": "result", "result": JSON.parse(result)});
				});

			})
			// chrome.tabs.create({"url": request.url});
		}
	}
);