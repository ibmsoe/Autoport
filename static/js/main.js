// Contains state of searching operations
var searchState = {
	ready: false,
	results: {}
};
// Contains state of loading view
var loadingState = {
	loading: false
}
// Contains state of detail view
var detailState = {
	ready: false,
	repo: null
}

// Rivets.js bindings
// Hides / shows loading panel
rivets.bind($('#loadingPanel'), {
	loadingState: loadingState
});
// Hides / shows results panel
rivets.bind($('#resultsPanel'), {
	searchState: searchState
});
// Hides / shows detail panel
rivets.bind($('#detailPanel'), {
	detailState: detailState
});
// Populates results table
rivets.bind($('#resultsTable'), {
	searchState: searchState
});

// Callback for when we recieve data from a search query request
function processSearchResults(data) {
	if(data.status !== "ok") {
		console.log("Bad response from /search!");
		console.log(data);
	} else if (data.type === "multiple") {
		// Got multiple results
		// Add addToJenkins function to each result
		data.results.forEach(function(result) {
			result.addToJenkins = function() {
				$.post("/createJob", {id: result.id}, addToJenkinsCallback, "json");
			};
		});

		searchState.results = data.results;
		loadingState.loading = false;
		searchState.ready = true;
	} else if (data.type === "detail") {
		// Got single repository result, show detail page
		showDetail(data);
	}
}

function showDetail(data) {
	if(data.status !== "ok" || data.type !== "detail") {
		console.log("Bad response while creating detail view!");
	} else {
		detailState.repo = data.repo;
		loadingState.loading = false;
		detailState.ready = true;
	}
}

// When the query textbox is changed, make a request to
// /query
$('#query').change(function(){
	searchState.ready = false;
	detailState.ready = false;
	loadingState.loading = true;
	var query = $(this).val();
	if(query.length > 0) {
		$.getJSON("/search", {q: query}, processSearchResults);
	}
});

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