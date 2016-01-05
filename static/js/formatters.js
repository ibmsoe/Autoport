// This file has the formatters used for Rivet.js and for Bootstrap Table addon
// When adding a new formatter, add it in the appropriate section

/************************************* Rivets.js formatters **********************************************/

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
    return (['Java', 'Scala', 'Clojure'].indexOf(value) != -1)
    //return value === "Java";
};

// For showing compiler/sdk options based on language
rivets.formatters.isJavaScript = function(value) {
    return value === "JavaScript";
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
rivets.formatters.shortName = function(value) {
    return value.replace(/.(\d\d\d\d-\d\d-\d\d-h\d\d-m\d\d-s\d\d)/,"").replace(/.(.*?)\.(.*?)\.(.*?)(-..-|-)/,"").replace("/","");

};

rivets.formatters.isEmptyObject = function(value) {
    return $.isEmptyObject(value);
};

rivets.formatters['eq'] = function (value, arg) {
    var return_value=false;
    if (value && arg)
       var return_value = value.toString().toLowerCase() == arg.toString().toLowerCase();
    else
        return_value = false;
    return return_value;
};

rivets.formatters['gt'] = function (value, arg) {
  return value > arg;
};

rivets.formatters['lteq'] = function (value, arg) {
  return value >= arg;
};

rivets.formatters['gt'] = function (value, arg) {
  return value < arg;
};

rivets.formatters['gteq'] = function (value, arg) {
  return value <= arg;
};
/************************************* Bootstrap Table addon formatters *********************************************/

// Returns 'Yes' if the package is up-datable, 'No' otherwise
function updatableFormatter(value, row) {
    return (value === true ? "Yes" : "No");
}
