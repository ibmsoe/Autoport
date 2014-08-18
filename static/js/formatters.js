// Rivets.js formatters
// rv-size formatter
rivets.formatters.size = function(value) {
	if(value > 1024) {
		return Math.round(value / 1024) + " MB";
	} else {
		return value + " KB";
	}
}

// rv-date formatter
rivets.formatters.date = function(value) {
	return moment.utc(value).fromNow();
}

// rv-details formatter
rivets.formatters.detail = function(value) {
	return "/detail/" + value;
}