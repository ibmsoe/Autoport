var globalState = {
	jenkinsUrl: "http://soe-test1.aus.stglabs.ibm.com:8080",
	gsaPathForCatalog: "/projects/p/powersoe/autoport/test_results/",
	gsaPathForUpload: "/projects/p/powersoe/autoport/batch_files/",
	githubToken: "9294ace21922bf38fae227abaf3bc20cf0175b08",
	reset: function() {
		jenkinsUrl =  "http://soe-test1.aus.stglabs.ibm.com:8080";
		gsaPathForCatalog = "/projects/p/powersoe/autoport/test_results/";
		gsaPathForUpload = "/projects/p/powersoe/autoport/batch_files/";
		githubToken = "9294ace21922bf38fae227abaf3bc20cf0175b08"
		document.getElementById('url').value = jenkinsUrl;
		document.getElementById('test_results').value = gsaPathForCatalog;
		document.getElementById('batch_files').value = gsaPathForUpload;
		document.getElementById('github').value = githubToken;
	},
	updateParameters: function () {
		jenkinsUrl = document.getElementById('url').value;
		gsaPathForCatalog = document.getElementById('test_results').value;
		gsaPathForUpload = document.getElementById('batch_files').value;
		githubToken = document.getElementById('github').value;
		$.post("/settings", {url: jenkinsUrl, test_results: gsaPathForCatalog, batch_files: gsaPathForUpload, github: githubToken}, settingsCallback, "json");
	}
};

// Contains state of searching operations
var searchState = {
    singleSearchBox: false,
    generateSearchBox: false,
	sorting: "relevance",
	ready: false, // Whether or not to draw this view
	query: "", // User's query
	results: {}, // Search result data
	setSingleSearchBox: function (ev) {
        searchState.singleSearchBox = (searchState.singleSearchBox) ? false : true;
	},
	setGenerateBatchBox: function (ev) {
        searchState.generateBatchBox = (searchState.generateBatchBox) ? false : true;
	},
	changeSort: function (ev) { // Called upon changing sort type
		searchState.sorting = $(ev.target).text().toLowerCase();
		doSearch();
	},
	queryTop: {
		limit:    25,
		sort:     "stars",
		language: "any",
		version:  "current",
		stars:    0,
		forks:    0,
		generate: function (ev) {
			// TODO: remove redundant query qualifiers (stars/forks == 0)
			var data = {
				// GitHub API parameters
				q:       " stars:>" + searchState.queryTop.stars +
						 " forks:>" + searchState.queryTop.forks +
						 (searchState.queryTop.language == "any" ? "" : (" language:" + searchState.queryTop.language)),
				sort:    searchState.queryTop.sort,

				// AutoPort parameters
				limit:   searchState.queryTop.limit,
				version: searchState.queryTop.version
			};

			console.log(data);
			switchToLoadingState();
			$.getJSON("/search/repositories", data, processSearchResults);
		}
	}
};

var batchState = {
    importBox: false,
    file_list: [],
    currentBatchFile: "",
    selectBatchFile: function (ev) {
        batchState.currentBatchFile = $(ev.target).text();
        console.log(batchState.currentBatchFile);
    },
    listBatchFiles: function (ev) {
        if (batchState.ready) {
            batchState.ready = false;
        }
        else {
	        $.post("/listBatchFiles", {}, listBatchFilesCallback, "json");
        }
    },
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
    buildAndTest: function (ev, el) { 
        console.log("In batchState.buildAndTest");
	    $.post("/runBatchFile", {batchName: el.result.filename}, runBatchFileCallback, "json");
    },
	setImportBox: function (ev) {
        batchState.importBox = (batchState.importBox) ? false : true;
	},
    query: {
        limit:    25,
        sort:     "stars",
        language: "any",
        version:  "current",
        stars:    0,
        forks:    0,
        upload: function (ev) {
            var data = document.getElementById('batchFileTextArea').value;
            $.post("/uploadBatchFile", {file: data}, uploadBatchFileCallback, "json");
        },
        generate: function (ev) {
            console.log("limit    = " + batchState.query.limit);
            console.log("sort     = " + batchState.query.sort);
            console.log("language = " + batchState.query.language);
            console.log("version  = " + batchState.query.version);
            console.log("stars    = " + batchState.query.stars);
            console.log("forks    = " + batchState.query.forks);

            // TODO: remove redundant query qualifiers (stars/forks == 0)
            var data = {
                // GitHub API parameters
                q:       " stars:>" + batchState.query.stars +
                         " forks:>" + batchState.query.forks +
                         (batchState.query.language == "any" ? "" : (" language:" + batchState.query.language)),
                sort:    batchState.query.sort,

                // AutoPort parameters
                limit:   batchState.query.limit,
                version: batchState.query.version
            };

            console.log(data);
            $.getJSON("/search/repositories", data, function(data, textStatus, jqXHR) {
                document.getElementById('batchFileTextArea').value = JSON.stringify(data, undefined, 4);
            });
        }
    },
    ready: false, // Whether or not to draw the batch file view
    batchFile: {
        config:   {},
        packages: []
    },
    download: function (ev) {
        var json = JSON.stringify(batchState.batchFile, undefined, 2);
        var data = "data: application/octet-stream;charset=utf-8," + encodeURIComponent(json);
        window.open(data);
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
	javaType: "", // Open JDK or IBM Java
	backToResults: function() {
		detailState.ready = false;
		searchState.ready = true;
	},
	exitAutoSelect: function() {
		doSearch(false);
	},
	// When the radio button is pressed update the server environment data
	selectJavaType:	function() {
    	var radio = document.getElementById('radio');
    	if (!document.getElementById('option1').checked) {
    		detailState.javaType = "";
    	}
    	else if (!document.getElementById('option2').checked) {
    		detailState.javaType = "JAVA_HOME=/opt/ibm/java";
    	}
	}
};

var reportState = {
    jobManagePanel: false,
    testResultsPanel: false,
    reportType:"batchResults",
    reportLabel:"Test results by batch by date",
    changeReportType: function(ev) {
        reportState.reportType = $(ev.target).attr('id');
        reportState.reportLabel = $(ev.target).text();
        doGetResultList();
    },
	setJobManagePanel: function (ev) {
        reportState.jobManagePanel = (reportState.jobManagePanel) ? false : true;
	},
	setTestResultsPanel: function (ev) {
        reportState.testResultsPanel = (reportState.testResultsPanel) ? false : true;
	}
};

var projectCompareSelectState = {
    prjCompareReady: false,
    projects: [],
    selectedProjects: [],
    prjTableReady: false,
    selectProject: function(id) {
        // find the corresponding project object.
        var projectName = "";
        for (prj in projectCompareSelectState.projects) {
            if (projectCompareSelectState.projects[prj].id == id) {
                projectName = projectCompareSelectState.projects[prj].fullName;
                break;
            }
        }
        if (projectName === "") {
            // Not found
            return;
        }
        var pos = projectCompareSelectState.selectedProjects.indexOf(projectName);
        if (pos != -1) {
            $("#"+id).toggleClass('btn-primary');
            projectCompareSelectState.selectedProjects.splice(pos, 1);
        } else if (projectCompareSelectState.selectedProjects.length < 2) {
            $("#"+id).toggleClass('btn-primary');
            projectCompareSelectState.selectedProjects.push(projectName);
        } else {
            console.log("More than 2 lines ");
            // TODO alert that only 2 lines can be selected or deselect the first?
        }
    },
    compareResults: function() {
        switchToLoadingState();
        if (projectCompareSelectState.selectedProjects.length === 2) {
            $.getJSON("/getTestResults?leftbuild="+projectCompareSelectState.selectedProjects[0]+
                      "&rightbuild="+projectCompareSelectState.selectedProjects[1],
                      {}, processBuildResults);
        }
    },
    backToList: function(ev) {
        projectCompareSelectState.prjCompareReady = true;
        projectCompareSelectState.prjTableReady = false;
    }
};

// Rivets.js bindings
rivets.bind($('#listButton'), {
    batchState: batchState
});
rivets.bind($('#jobManageButton'), {
    reportState: reportState
});
rivets.bind($('#jobManagePanel'), {
    reportState: reportState
});
rivets.bind($('#testResultsButton'), {
    reportState: reportState
});
rivets.bind($('#testResultsPanel'), {
    reportState: reportState
});
rivets.bind($('#importButton'), {
    batchState: batchState
});
rivets.bind($('#generateBatchButton'), {
    searchState: searchState
});
rivets.bind($('#singleSearchButton'), {
    searchState: searchState
});
rivets.bind($('#batchListPanel'), {
    batchState: batchState
});
// Allows user to change global settings
rivets.bind($('#settingsModal'), {
	globalState: globalState
});
rivets.bind($('#listBox'), {
	batchState: batchState
});
rivets.bind($('#searchBox'), {
	searchState: searchState
});
rivets.bind($('#fileUploadBox'), {
    batchState: batchState
});
rivets.bind($('#buildAndTestBox'), {
    batchState: batchState
});
rivets.bind($('#generateBox'), {
    batchState: batchState,
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
// Hides / shows batch file panel
rivets.bind($('#batchFilePanel'), {
	batchState: batchState
});
// Populates batch file table
rivets.bind($('#batchFileTable'), {
	batchState: batchState
});

rivets.bind($('#reportSelector'), {
    reportState: reportState
});
rivets.bind($('#testCompareSelectPanel'), {
    projectCompareSelectState: projectCompareSelectState
});
rivets.bind($("#testCompareRunAlert"), {
    projectCompareSelectState: projectCompareSelectState
});
rivets.bind($("#testCompareTablePanel"), {
    projectCompareSelectState: projectCompareSelectState
});

// Disables all views except loading view
function switchToLoadingState() {
	searchState.ready = false;
	detailState.ready = false;
    projectCompareSelectState.prjCompareReady = false;
    projectCompareSelectState.prjTableReady = false;
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
			};
			result.addToBatchFile = function () {
				batchState.batchFile.packages.push(result);
				batchState.ready = true;
			};
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

function doGetResultList() {
    switch (reportState.reportType) {
      case "projectCompare":
        switchToLoadingState();
        $.getJSON("/listTestResults", {}, processResultList);
        break;
      default:
        break;
    }
}

function processResultList(data) {
    projectCompareSelectState.selectedProjects = [];
    projectCompareSelectState.projects = [];
    if (data === undefined || data.status != "ok") {
        console.log("Error");// TODO error message
    } else {
        prjRegex = /(.*?) - (.*?) - (.*?)-(.*)\.(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d)/;
        for (var project in data.results) {
            if (project !== undefined) {
                prjObject = prjRegex.exec(data.results[project]);
                if (prjObject === null) {
                    continue;
                }
                var prjId = data.results[project];
                // HTML element's 'id' attribute can't have spaces
                prjId = CryptoJS.MD5(prjId);
                projectCompareSelectState.projects.push({
                     fullName: prjObject[0],
                           id: prjId,
                         name: prjObject[3],
                          env: prjObject[2],
                      version: prjObject[4],
                    completed: prjObject[5],
                       select: function(ev) {
                           projectCompareSelectState.selectProject(ev.target.id);
                       }
                });
            }
        }
        searchState.ready = false;
        detailState.autoSelected = false;
        loadingState.loading = false;
        projectCompareSelectState.prjCompareReady = true;
    }
}

function processBuildResults(data) {
    var tableContent = "";
    if (data.status != "ok") {
        tableContent = "<tr><th>Error</th><th>"+data.error+"</th></td>";
    } else {
        tableContent = "<tr><th>Test</th><th colspan=\"4\">";
        tableContent += data.leftCol + "</th><th colspan=\"4\">";
        tableContent += data.rightCol + "</th></tr>";
        tableContent += "<tr><th/><th class=\"testResultArch\">T</th><th>F</th><th>E</th><th>S</th>";
        tableContent += "<th class=\"testResultArch\">T</th><th>F</th><th>E</th><th>S</th></tr>";
        var suiteKeys = Object.keys(data.results.results);
        for (var key in suiteKeys) {
            console.log("Suite key: " + suiteKeys[key]);
            tableContent += "<tr><th class=\"testSuite\">" +
                 suiteKeys[key] +
                "</th><th class=\"testResultArch testSuite\" colspan=\"4\"/><th class=\"testResultArch testSuite\" colspan=\"4\"/></tr>";
            var testKeys = Object.keys(data.results.results[suiteKeys[key]]);
            for (testKey in testKeys) {
                console.log("testKey: "+testKeys[testKey]);
                var tc = data.results.results[suiteKeys[key]][testKeys[testKey]];
                if (tc === undefined ||
                    tc["total"] === undefined ||
                    tc["failures"] === undefined ||
                    tc["errors"] === undefined ||
                    tc["skipped"] === undefined)
                    continue;
                var hlTotal = (tc["total"][data.leftCol] > tc["total"][data.rightCol] ?
                            " testErr" : "");
                var hlFail = (tc["failures"][data.leftCol] < tc["failures"][data.rightCol] ?
                            " testErr" : "");
                var hlErr = (tc["errors"][data.leftCol] < tc["errors"][data.rightCol] ?
                            " testErr" : "");
                var hlSkip = (tc["skipped"][data.leftCol] < tc["skipped"][data.rightCol] ?
                            " testErr" : "");
                var hlTest = (hlTotal.length !== 0 ||
                    hlFail.length !== 0 ||
                    hlErr.length !== 0 ||
                    hlSkip.length !== 0 ? " testErr" : "");

                tableContent += "<tr><td class=\"testClass"+hlTest+"\">"+testKeys[testKey]+
                    "</td><td class=\"testResultArch\">"+
                    tc["total"][data.leftCol]+"</td><td class=\"testResult\">"+
                    tc["failures"][data.leftCol]+"</td><td class=\"testResult\">"+
                    tc["errors"][data.leftCol]+"</td><td class=\"testResult\">"+
                    tc["skipped"][data.leftCol]+"</td><td class=\"testResultArch"+hlTotal+"\">"+
                    tc["total"][data.rightCol]+"</td><td class=\"testResult"+hlFail+"\">"+
                    tc["failures"][data.rightCol]+"</td><td class=\"testResult"+hlErr+"\">"+
                    tc["errors"][data.rightCol]+"</td><td class=\"testResult"+hlSkip+"\">"+
                    tc["skipped"][data.rightCol]+"</td></tr>";
            }
        }
    }
    $("#testResultsTable").html(tableContent);
    loadingState.loading = false;
    projectCompareSelectState.prjTableReady = true;
}

// Sets up and opens detail view for a repo
// TODO - add check boxes for architectures wanted
function showDetail(data) {
	if(data.status !== "ok" || data.type !== "detail") {
		console.log("Bad response while creating detail view!");
	} else {
		detailState.repo = data.repo;
		detailState.repo.addToJenkins = function(e) {
			$.post("/createJob", {id: detailState.repo.id, tag: e.target.innerHTML, javaType: detailState.javaType, arch: "x86"}, addToJenkinsCallback, "json");
			$.post("/createJob", {id: detailState.repo.id, tag: e.target.innerHTML, javaType: detailState.javaType, arch: "ppcle"}, addToJenkinsCallback, "json");
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

function settingsCallback(data) {
	if (data.status != "ok") {
		console.log("Bad response from /settings!");
		console.log(data);
	}
}

function uploadBatchFileCallback(data) {
    console.log("In uploadBatchFileCallback");
}

function runBatchFileCallback(data) {
    console.log("In runBatchFileCallback");
}

function listBatchFilesCallback(data) {
    if(data.status === "ok") {
        batchState.file_list = data.files;
        batchState.ready = true;
    }
}

function addToJenkinsCallback(data) {
    // TODO - need to take in a list of sjobUrls and hjobUrls and then iterate over the list
	if(data.status === "ok") {
		// Open new windows with the jobs' home pages
		window.open(data.hjobUrl,'_blank');
	} else {
		console.log("Bad response from /createJob!");
		console.log(data);
	}
}
