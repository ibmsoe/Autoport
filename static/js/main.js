// Contains state of searching operations
var searchState = {
	sorting: "relevance",
	ready: false,
	query: "",
	results: {},
	changeSort: function (ev) {
		searchState.sorting = $(ev.target).text().toLowerCase();
		doSearch();
	}
};
// Contains state of loading view
var loadingState = {
	loading: false
}
// Contains state of detail view
var detailState = {
	ready: false,
	repo: null,
	autoSelected: false
}

// Rivets.js bindings
// Allows user to change sorting method
rivets.bind($('#searchBox'), {
	searchState: searchState
});
// Multiple result alert box
rivets.bind($('.multiple-alert'), {
	searchState: searchState
});
// Autoselect alert box
rivets.bind($('.autoselect-alert'), {
	detailState: detailState
});
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

function switchToLoadingState() {
	searchState.ready = false;
	detailState.ready = false;
	loadingState.loading = true;
	detailState.autoSelected = false;
}

function doSearch() {
	switchToLoadingState();
	searchState.query = $('#query').val();
	if(searchState.query.length > 0) {
		$.getJSON("/search", {
			q: searchState.query,
			sort: searchState.sorting
		}, processSearchResults);
	}
}


// When the query textbox is changed, do a search
$('#query').change(doSearch);

// Callback for when we recieve data from a search query request
function processSearchResults(data) {
	if(data.status !== "ok") {
		console.log("Bad response from /search!");
		console.log(data);
	} else if (data.type === "multiple") {
		// Got multiple results
		// Add addToJenkins and select function to each result
		data.results.forEach(function(result) {
			result.select = function () {
				$.get("/detail/" + result.id, showDetail);
				switchToLoadingState();
			}
		});
		detailState.autoSelected = false;
		searchState.results = data.results;
		loadingState.loading = false;
		searchState.ready = true;
	} else if (data.type === "detail") {
		// Got single repository result, show detail page
		detailState.autoSelected = true;
		showDetail(data);
	}
}

function showDetail(data) {
	if(data.status !== "ok" || data.type !== "detail") {
		console.log("Bad response while creating detail view!");
	} else {
		detailState.repo = data.repo;
		detailState.repo.addToJenkins = function() {
			$.post("/createJob", {id: detailState.repo.id}, addToJenkinsCallback, "json");
		};
		loadingState.loading = false;
		detailState.ready = true;
		// Make chart
		var ctx = $("#langChart").get(0).getContext("2d");
		var pie = new Chart(ctx).Pie(detailState.repo.languages, {
			segmentShowStroke: false
		});
		legend(document.getElementById('langLegend'), detailState.repo.languages)
	}
}

function addToJenkinsCallback(data) {
	if(data.status === "ok") {
		window.location.href = data.jobUrl;
	} else {
		console.log("Bad response from /createJob!");
		console.log(data);
	}
}

$('#query').val("redis");
$('#query').change();