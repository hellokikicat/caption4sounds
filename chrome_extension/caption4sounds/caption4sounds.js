var cap4snd = function() {
	var c4s = {};
	c4s.PLAYER_ID = "movie_player";

	var player = document.getElementById(c4s.PLAYER_ID);
	// var header = document.getElementById("watch-header");
	
	video_id = player.getVideoData().video_id;
	
	var event = new CustomEvent("ReceiveFromPage", {detail: video_id});
	window.dispatchEvent(event);
	
	transcript = JSON.parse('{"0": ""}');

	window.addEventListener("PassToPage", function(evt) {
		// chrome.runtime.sendMessage(evt.detail);
		transcript = evt.detail;
		console.log('received transcript');
		console.log(transcript);
	}, false);
	
	c4s.showCaption = function(elem, txt) {
		elem.textContent = txt;
	}

	c4s.injectCaptionDiv = function() {
		var caption_div_html = "<span class=\"audio-caption\" style=\"font-size: 16px\">[dogs barking]</span>";
		// control_bar = document.getElementsByClassName("ytp-chrome-controls")[0];
		playerDiv = document.getElementsByClassName("html5-video-player")[0];

		var caption_div = document.createElement('div');
		caption_div.innerHTML = caption_div_html;
		// caption_div.setAttribute("data-layer", "4");
		// caption_div.setAttribute("class", "caption-window");
		caption_div.style.float = 'center';
		caption_div.style['margin-top'] = '2px';
		caption_div.style['position'] = 'absolute';
		caption_div.style['z-index'] = '38';

		var child = document.getElementsByClassName('ytp-chrome-bottom')[0];

		playerDiv.insertBefore(caption_div, child);

		var caption_span = document.getElementsByClassName("audio-caption")[0];
		c4s.showCaption(caption_span, "cat purring")
		
	}
	
	if (document.getElementsByClassName("html5-video-player")[0]) {
		// c4s.getVideoID();
		// transcript = c4s.getCaptions();
		
		c4s.injectCaptionDiv();
		
		// transcript = JSON.parse('{"0": "", "2": "abc", "5.3": "dog barking", "10.1": "cat purring"}');
		
		captionAt = function(time) {
			idx = Object.keys(transcript).reverse().find(function(x){return Number(x)*2<=time})
			return transcript[idx]
		}
		
		updateCaption = function() {
			var caption_span = document.getElementsByClassName("audio-caption")[0];
			var curr_time = player.getCurrentTime();
			// console.log(captionAt(curr_time));
			c4s.showCaption(caption_span, captionAt(curr_time));
			// if(curr_time > 30){
				// c4s.showCaption(caption_span, curr_time)
			// }
			// else {
				// c4s.showCaption(caption_span, 'cats purring')
			// }
			t = window.setTimeout(updateCaption, 200);

			// ytState = player.getPlayerState();
			// if(ytState == 1 /* && ytState < 3*/){
				// var caption_span = document.getElementsByClassName("audio-caption")[0];

				// var curr_time = player.getCurrentTime();
				// if(curr_time>30){
					// c4s.showCaption(caption_span, 'dogs barking')
				// }
				// t = window.setTimeout(c4s.updateCaption, 200);
			// }
		}
		
		updateCaption();
		// player.addEventListener("onStateChange", c4s.updateCaption);

	};
}

window.onload = cap4snd;
