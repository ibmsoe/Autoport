var searchState = {
	ready: false,
	loading: false,
	results: {}
};


rivets.bind($('#loadingPanel'), {
	searchState: searchState
});

rivets.bind($('#resultsPanel'), {
	searchState: searchState
});

rivets.bind($('#resultsTable'), {
	searchState: searchState
});

rivets.formatters.size = function(value) {
	if(value > 1024) {
		return Math.round(value / 1024) + " MB";
	} else {
		return value + " KB";
	}
}

rivets.formatters.date = function(value) {
	return moment.utc(value).fromNow();
}

// Callback for when we recieve data from a search query request
function processSearchResults(data) {
	var now = moment.utc();
	if(data.status !== "ok") {
		console.log("Bad response from /search!")
		console.log(data)
	} else {
		data.results.forEach(function(result) {
			// Calculate days since last update
			var lastUpdate = moment.utc(result.last_update);
			var daysBetween = now.diff(lastUpdate, 'days');
			// Calculate color coding classifications
			result.coding = {}
			result.coding.stars = starClassifier(result.stars);
			result.coding.forks = forkClassifier(result.forks);
			result.coding.language = langClassifier(result.language);
			result.coding.size = sizeClassifier(result.size_kb);
			result.coding.date = dateClassifier(daysBetween);
			//Add addToJenkins function
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