var curResults; //Array of current search results

// Callback for when we recieve data from a search query request
function renderSearchResults(data) {
	curResults = data.results
	var now = moment.utc();
	$('#resultsTable').find("tr").remove();
	if(data.status !== "ok") {
		console.log("Bad response from /search!")
		console.log(data)
	} else {
		var index = 0;
		data.results.forEach(function(entry) {
			// Calculate days since last update
			var lastUpdate = moment.utc(entry.last_update);
			var daysBetween = now.diff(lastUpdate, 'days');
			// Calculate color coding classifications
			entry.coding = {}
			entry.coding.stars = starClassifier(entry.stars);
			entry.coding.forks = forkClassifier(entry.forks);
			entry.coding.language = langClassifier(entry.language);
			entry.coding.size = sizeClassifier(entry.size_kb);
			entry.coding.date = dateClassifier(daysBetween);

			$('#resultsTable').append(generateRow(entry, index));
			rivets.bind($('#row-' + index), {
				entry: entry
			});
			index++;
		})
	}
}

// When the query textbox is changed, make a request to
// /query
$('#query').change(function(){
	var query = $(this).val();
	if(query.length > 0) {
		$('#resultsTable').find("tr").remove();
		$('#resultsTable').append("<tr><td>Loading...<td></tr>");
		$.getJSON("/search", {q: query}, renderSearchResults);
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

// "Add to Jenkins" buttons
$(document).on('click', '.add-to-jenkins', function() {
	var index = $(this).attr("data-id");
	var entry = curResults[index];
	var requestData = {
		name: entry.name,
		github_url: entry.url,
		git_url: entry.git_url,
		default_branch: entry.default_branch
	};
	$.post("/createJob", requestData, addToJenkinsCallback, "json");
})

//debug
$('#query').val("redis");
$('#query').change();