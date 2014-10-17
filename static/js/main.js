// Contains state of searching operations
var searchState = {
	sorting: "relevance",
	ready: false, // Whether or not to draw this view
	query: "", // User's query
	results: {}, // Search result data
	changeSort: function (ev) { // Called upon changing sort type
		searchState.sorting = $(ev.target).text().toLowerCase();
		doSearch();
	}
};

var batchState = {
    upload: function (ev) {
        //Why do I need the [0] in the jQuery but not the getElementByID, those should be equivalent?
        //var file = document.getElementById('batch_file').files[0];
        var file = $('#batch_file')[0].files[0]; 
        
        if (file) {
            var reader = new FileReader();
            reader.readAsText(file);
		
            reader.onload = function(e) {
                $.post("/uploadBatchFile", {file: e.target.result}, uploadBatchFileCallback, "json");
            };	
        }
    },
    build: function (ev) {
        console.log("In batchState.build");
    },
    buildAndTest: function (ev) { 
        console.log("In batchState.buildAndTest");
	    $.post("/runBatchFile", {batchName: ""}, runBatchFileCallback, "json");
    }
};

// Contains state of loading view
var loadingState = {
	loading: false // Whether or not to draw this view
}
// Contains state of detail view
var detailState = {
	ready: false,
	repo: null, // Repo data
	autoSelected: false, // Was this repository autoselected from search query?
	pie: null, // Pie chart
	backToResults: function() {
		detailState.ready = false;
		searchState.ready = true;
	},
	exitAutoSelect: function() {
		doSearch(false);
	}
}

// Rivets.js bindings
// Allows user to change sorting method
rivets.bind($('#searchBox'), {
	searchState: searchState
});
rivets.bind($('#fileUploadBox'), {
    batchState: batchState
});
rivets.bind($('#buildAndTestBox'), {
    batchState: batchState
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

// Disables all views except loading view
function switchToLoadingState() {
	searchState.ready = false;
	detailState.ready = false;
	loadingState.loading = true;
	detailState.autoSelected = false;
}

// Does the above and makes a search query
function doSearch(autoselect) {
	if(typeof(autoselect)==='undefined') autoselect = true;
	if(typeof(autoselect)!=='boolean') autoselect = true;
	
	// Do not switch to loading state if query is empty
	searchState.query = $('#query').val();
	if(searchState.query.length > 0) {
		switchToLoadingState();
		$.getJSON("/search", {
			q: searchState.query,
			sort: searchState.sorting,
			auto: autoselect
		}, processSearchResults);
	}
}

// When the query textbox is changed, do a search
$('#query').change(doSearch);

$('#batch_file').change(function () {
    console.log("Changed");
    $('#uploadFilename').val("File selected:  " + $('#batch_file').val());
});

// Callback for when we recieve data from a search query request
function processSearchResults(data) {
	if(data.status !== "ok") {
		console.log("Bad response from /search!");
		console.log(data);
	} else if (data.type === "multiple") {
		// Got multiple results
		// Add select function to each result
		data.results.forEach(function(result) {
			// Show detail view for repo upon selection
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

// Sets up and opens detail view for a repo
// TODO - add check boxes for architectures wanted
function showDetail(data) {
	if(data.status !== "ok" || data.type !== "detail") {
		console.log("Bad response while creating detail view!");
	} else {
		detailState.repo = data.repo;
		detailState.repo.addToJenkins = function(e) {
			$.post("/createJob", {id: detailState.repo.id, tag: e.target.innerHTML, arch: "x86"}, addToJenkinsCallback, "json");
			$.post("/createJob", {id: detailState.repo.id, tag: e.target.innerHTML, arch: "ppcle"}, addToJenkinsCallback, "json");
		};
		loadingState.loading = false;
		detailState.ready = true;
		// Make chart
		var ctx = $("#langChart").get(0).getContext("2d");
		if(detailState.pie !== null) {
			detailState.pie.destroy();
		}
		detailState.pie = new Chart(ctx).Pie(detailState.repo.languages, {
			segmentShowStroke: false
		});
		legend(document.getElementById('langLegend'), detailState.repo.languages)
	}
}

function uploadBatchFileCallback(data) {
    console.log("In uploadBatchFileCallback");
}

function runBatchFileCallback(data) {
    console.log("In runBatchFileCallback");
}

function addToJenkinsCallback(data) {
    // TODO - need to take in a list of sjobUrls and hjobUrls and then iterate over the list
	if(data.status === "ok") {
		// Preempt the newly created jobs.
		$.get(data.sjobUrl);
		// Open new windows with the jobs' home pages
		window.open(data.hjobUrl,'_blank');
	} else {
		console.log("Bad response from /createJob!");
		console.log(data);
	}
}
