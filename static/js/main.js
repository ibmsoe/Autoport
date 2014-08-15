// Contains state of searching operations
var searchState = {
	ready: false,
	loading: false,
	results: {}
};

// Rivets.js bindings
// Hides / shows loading panel
rivets.bind($('#loadingPanel'), {
	searchState: searchState
});
// Hides / shows results panel
rivets.bind($('#resultsPanel'), {
	searchState: searchState
});
// Populates results table
rivets.bind($('#resultsTable'), {
	searchState: searchState
});

// Rivets.js binders
// rv-classification binder
rivets.binders.classification = function(el, value) {
	// Classification constants
	var GOOD = 1;
	var NEUTRAL = 2;
	var BAD = 3;
	var UNCERTAIN = 4;

	var classToAdd;
	switch(value) {
		case GOOD:
			classToAdd = "label-success";
			break;
		case NEUTRAL:
			classToAdd = "label-warning";
			break;
		case BAD:
			classToAdd = "label-danger";
			break;
		default:
			classToAdd = "label-default";
	}
	$(el).addClass(classToAdd);
}

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

// Callback for when we recieve data from a search query request
function processSearchResults(data) {
	if(data.status !== "ok") {
		console.log("Bad response from /search!")
		console.log(data)
	} else {
		// Add addToJenkins function to each result
		data.results.forEach(function(result) {
			result.addToJenkins = function() {
				addToJenkins(result);
			};
		});

		searchState.results = data.results
		searchState.loading = false;
		searchState.ready = true
	}
}

// When the query textbox is changed, make a request to
// /query
$('#query').change(function(){
	searchState.ready = false;
	searchState.loading = true;
	var query = $(this).val();
	if(query.length > 0) {
		$.getJSON("/search", {q: query}, processSearchResults);
	}
});

// This function gets added to each result object
function addToJenkins(repo) {
	var requestData = {
		name: repo.name,
		github_url: repo.url,
		git_url: repo.git_url,
		default_branch: repo.default_branch
	};
	$.post("/createJob", requestData, addToJenkinsCallback, "json");
}

function addToJenkinsCallback(data) {
	if(data.status === "ok") {
		window.location.href = data.jobUrl;
	} else {
		console.log("Bad response from /createJob!");
		console.log(data);
	}
}

//debug
$('#query').val("redis");
$('#query').change();