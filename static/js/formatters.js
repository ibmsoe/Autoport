// Rivets.js formatters
// rv-size formatter
rivets.formatters.size = function(value) {
	if(value > 1024) {
		return Math.round(value / 1024) + " MB";
	} else {
		return value + " KB";
	}
};

// rv-date formatter
rivets.formatters.date = function(value) {
	return moment.utc(value).fromNow();
};

// rv-details formatter
rivets.formatters.detail = function(value) {
	return "/detail/" + value;
};

// For showing/hiding sorting methods in the dropdown
rivets.formatters.isRelevance = function(value) {
	return value === "relevance";
};
rivets.formatters.isStars = function(value) {
	return value === "popularity stars";
};
rivets.formatters.isForks = function(value) {
	return value === "forks";
};
rivets.formatters.isUpdated = function(value) {
	return value === "updated";
};

// For showing compiler/sdk options based on language
rivets.formatters.isJava = function(value) {
    return value === "Java";
};

// For displaying NA when no options were found instead of empty textbox
rivets.formatters.cleanOptionsOutput = function(value) {
    return (value === "" ? "NA" : value);
}

// report dropdown formatters
rivets.formatters.isBatchResults = function(value) {
    return value === "batchResults";
};
rivets.formatters.isProjectResults = function(value) {
    return value === "projectResults";
};
rivets.formatters.isBatchHistory = function(value) {
    return value === "batchHistory";
};
rivets.formatters.isProjectHistory = function(value) {
    return value === "projectHistory";
};
rivets.formatters.isProjectCompare = function(value) {
    return value === "projectCompare";
};

// Checks whether location is local or archived
rivets.formatters.isLocal = function(value) {
    return value === "local";
};
