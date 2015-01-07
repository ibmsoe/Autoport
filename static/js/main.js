var globalState = {
    hasInit: false,

    jenkinsUrlInit: "",
    localPathForTestResultsInit: "",
    pathForTestResultsInit: "",
    localPathForBatchFilesInit: "",
    pathForBatchFilesInit: "",
    githubTokenInit: "",
    configUsernameInit: "",
    configPasswordInit: "",

    jenkinsUrl: "",
    localPathForTestResults: "",
    pathForTestResults: "",
    localPathForBatchFiles: "",
    pathForBatchFiles: "",
    githubToken: "",
    configUsername: "",
    configPassword: "",

    isSearchTabActive: true,
    isBatchTabActive: false,
    isReportsTabActive: false,

    isHelpDisplayed: true,

    toggleHelp: function() {
        globalState.isHelpDisplayed = !globalState.isHelpDisplayed;
        $("#toggleHelpBtn").text((globalState.isHelpDisplayed?"Hide":"Show")+" help");
        $("#helpViewer").css("display", globalState.isHelpDisplayed?"block":"none");
    },

    headerChange: function(ev) {
        if(ev.target.id === "searchTab") {
            globalState.isSearchTabActive = true;
            globalState.isBatchTabActive = false;
            globalState.isReportsTabActive = false;
        }
        else if(ev.target.id === "batchTab") {
            globalState.isSearchTabActive = false;
            globalState.isBatchTabActive = true;
            globalState.isReportsTabActive = false;
        }
        else if(ev.target.id === "reportsTab") {
            globalState.isSearchTabActive = false;
            globalState.isBatchTabActive = false;
            globalState.isReportsTabActive = true;
        }
    },
    reset: function() {
        document.getElementById('url').value = globalState.jenkinsUrlInit;
        document.getElementById('ltest_results').value = globalState.localPathForTestResultsInit;
        document.getElementById('gtest_results').value = globalState.pathForTestResultsInit;
        document.getElementById('lbatch_files').value = globalState.localPathForBatchFilesInit;
        document.getElementById('gbatch_files').value = globalState.pathForBatchFilesInit;
        document.getElementById('github').value = globalState.githubTokenInit;
        document.getElementById('username').value = globalState.configUsernameInit;
        document.getElementById('password').value = globalState.configPasswordInit;
    },
    updateParameters: function () {
        jenkinsUrl = document.getElementById('url').value;
        localPathForTestResults = document.getElementById('ltest_results').value;
        pathForTestResults = document.getElementById('gtest_results').value;
        localPathForBatchFiles = document.getElementById('lbatch_files').value;
        pathForBatchFiles = document.getElementById('gbatch_files').value;
        githubToken = document.getElementById('github').value;
        configUsername = document.getElementById('username').value;
        configPassword = document.getElementById('password').value;
        $.post("/settings", {url: jenkinsUrl,
               ltest_results: localPathForTestResults, gtest_results: pathForTestResults,
               lbatch_files: localPathForBatchFiles, gbatch_files: pathForBatchFiles, github: githubToken,
               username: configUsername, password: configPassword}, settingsCallback, "json");
    }
};

if (!globalState.hasInit) {
    $.post("/init", {}, initCallback, "json");
}

var percentageState = {
    // Actual Numeric Values
    totalNumberOfJobs: 0,
    unfinishedJobs: 0,
    failingJobs: 0,
    unstableJobs: 0,
    successfulJobs: 0,

    // Percentages
    dangerPercentage: "width: 0%;",
    warningPercentage: "width: 0%;",
    successPercentage: "width: 0%;",
    updateProgressBar: function() {
        $.getJSON("/progress", {}, processProgressBar);
    }
};

// Contains state of searching operations
var searchState = {
    singleSearchBox: false,
    generateSearchBox: false,
	sorting: "relevance",
	ready: false, // Whether or not to draw this view
    generateReady: false,
	query: "", // User's query
	singleResults: {}, // Search result data
	generateResults: {}, // Search result data
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
				version: searchState.queryTop.version,
                panel: "generate"
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
    ready: false, // Whether or not to draw the list/select batch file view
    exportReady: false, // Whether or not to draw the export batch file view
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
};
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
    projectFilter: "",
    batchFilter: "",
    listLocalProjects: function(ev) {
        switchToLoadingState();
        projectReportState.compareType = "project";
        projectReportState.compareRepo = "local";
        $.getJSON("/listTestResults/local", { filter: $("#projectFilter").val() }, processResultList);
        $("#resultArchiveBtn").show();
    },
    listGSAProjects: function(ev) {
        switchToLoadingState();
        projectReportState.compareType = "project";
        projectReportState.compareRepo = "archived";
        $.getJSON("/listTestResults/gsa", { filter: $("#projectFilter").val() }, processResultList);
        $("#resultArchiveBtn").hide();
    },
    listAllProjects: function(ev) {
        switchToLoadingState();
        projectReportState.compareType = "project";
        projectReportState.compareRepo = "all";
        $.getJSON("/listTestResults/all", { filter: $("#projectFilter").val() }, processResultList);
        $("#resultArchiveBtn").show();
    },
    listLocalBatch: function(ev) {
    },
    listGSABatch: function(ev) {
    },
    listAllBatch: function(ev) {
    },
	setJobManagePanel: function(ev) {
        reportState.jobManagePanel = (reportState.jobManagePanel) ? false : true;
	},
	setTestResultsPanel: function(ev) {
        reportState.testResultsPanel = (reportState.testResultsPanel) ? false : true;
	}
};

var jenkinsState = {
    jenkinsPanel: false,
    setJenkinsPanel: function(ev) {
        jenkinsState.jenkinsPanel = (jenkinsState.jenkinsPanel) ? false : true;
    }
};

function handleProjectListBtns() {
    if (Object.keys(projectReportState.selectedProjects).length === 2) {
        $("#compareResultsBtn").removeClass("disabled");
    } else {
        $("#compareResultsBtn").addClass("disabled");
    }
    if (Object.keys(projectReportState.selectedProjects).length === 0) {
        $("#testHistoryBtn").addClass("disabled");
        $("#testDetailBtn").addClass("disabled");
        $("#resultArchiveBtn").addClass("disabled");
    } else {
        $("#testHistoryBtn").removeClass("disabled");
        $("#testDetailBtn").removeClass("disabled");
        $("#resultArchiveBtn").removeClass("disabled");
    }
}

var projectReportState = {
    prjCompareReady: false,
    compareRepo: "local",
    compareType: "project",
    projects: [],
    projectsTable: null,
    selectedProjects: {},
    prjTableReady: false,
    selectProject: function(id) {
        // find the corresponding project object.
        var projectName = "";
        var projectRepo = "";
        var isSelected = false;
        for (prj in projectReportState.projects) {
            if (projectReportState.projects[prj].id == id) {
                projectName = projectReportState.projects[prj].fullName;
                projectRepo = projectReportState.projects[prj].repository;
                isSelected = projectReportState.projects[prj].selectStatus;
                projectReportState.projects[prj].selectStatus = !isSelected;
                // Find the entry in the table
                projectReportState.projectsTable.data().each(function(d){
                    if (d.id == id) {
                        d.selectStatus = !isSelected;
                    }
                });
                break;
            }
        }
        if (projectName === "") {
            // Not found
            return;
        }
        var pos = projectReportState.selectedProjects[projectName];
        if (pos !== undefined) {
            delete projectReportState.selectedProjects[projectName];
        } else {
            projectReportState.selectedProjects[projectName] = projectRepo;
        }
        projectReportState.projectsTable.rows().invalidate().draw();
        handleProjectListBtns();
    },
    selectAll: function() {
        for (prj in projectReportState.projects) {
            var projectName = projectReportState.projects[prj].fullName;
            var projectRepo = projectReportState.projects[prj].repository;
            if (projectReportState.selectedProjects.indexOf(projectName) === -1) {
                projectReportState.selectedProjects[projectName] = projectRepo;
                projectReportState.projects[prj].selectStatus = true;
            }
        }
        projectReportState.projectsTable.data().each(function(d) {
            d.selectStatus = true;
        });
        projectReportState.projectsTable.rows().invalidate().draw();
        handleProjectListBtns();
    },
    selectNone: function() {
        for (prj in projectReportState.projects) {
            var projectName = projectReportState.projects[prj].fullName;
            projectReportState.projects[prj].selectStatus = false;
            if (projectReportState.selectedProjects[projectName] !== undefined) {
                delete projectReportState.selectedProjects[projectName];
            }
        }
        projectReportState.projectsTable.data().each( function(d) {
            d.selectStatus = false;
        });
        projectReportState.selectedProjects = {};
        projectReportState.projectsTable.rows().invalidate().draw();
        handleProjectListBtns();
    },
    testHistory: function() { // TODO single project or multiple?
        var sel = Object.keys(projectReportState.selectedProjects);
        var query = {};
        for (proj in sel) {
            query[sel[proj]] = projectReportState.selectedProjects[sel[proj]];
        }
        switchToLoadingState();
        $.ajax({
                type: "POST",
         contentType: "application/json; charset=utf-8",
                 url: "/getTestHistory",
                data: JSON.stringify({
                        projects: query
                      }),
             success: processTestHistory,
            dataType:'json'
        });
    },
    testDetail: function() {
        var sel = Object.keys(projectReportState.selectedProjects);
        var query = {};
        for (proj in sel) {
            query[sel[proj]] = projectReportState.selectedProjects[sel[proj]];
        }
        switchToLoadingState();
        $.ajax({
                type: "POST",
         contentType: "application/json; charset=utf-8",
                 url: "/getTestDetail",
                data: JSON.stringify({
                        projects: query
                      }),
             success: processTestDetail,
            dataType:'json'
        });
    },
    compareResults: function() {
        console.log("test compare");
        var sel = Object.keys(projectReportState.selectedProjects);
        if (sel.length === 2) {
            var leftProject = sel[0];
            var rightProject = sel[1];
            var leftRepo = projectReportState.selectedProjects[leftProject];
            var rightRepo = projectReportState.selectedProjects[rightProject];
            switchToLoadingState();
            $.getJSON("/getTestResults",
                      {
                        leftbuild: leftProject,
                        rightbuild: rightProject,
                        leftrepository: leftRepo,
                        rightrepository: rightRepo
                      },
                      processBuildResults);
        } else {
            $('#resultCompareSelectionAlert').modal();
        }
    },
    archive: function() {
        console.log("TODO archive");
        $.post("/archiveProjects",
            {
                projects: selectedProjects
            },
            archiveCallback, "json");
    },
    backToList: function(ev) {
        projectReportState.prjCompareReady = true;
        projectReportState.prjTableReady = false;
    }
};

// Rivets.js bindings
// Binders for tab headers
rivets.bind($('#searchTabHeader'), {
    globalState: globalState
});
rivets.bind($('#batchTabHeader'), {
    globalState: globalState
});
rivets.bind($('#reportsTabHeader'), {
    globalState: globalState
});
// Binders for tabs
rivets.bind($('#searchTab'), {
    globalState: globalState
});
rivets.bind($('#batchTab'), {
    globalState: globalState
});
rivets.bind($('#reportsTab'), {
    globalState: globalState
});
// Binders for job manage box
rivets.bind($('#jobManageButton'), {
    reportState: reportState
});
// Allows client to display progress on batch job
rivets.bind($('#jobManagePanel'), {
    projectReportState: projectReportState,
    reportState: reportState,
    percentageState: percentageState
});

// Binders for test results box
rivets.bind($('#testResultsButton'), {
    reportState: reportState
});
rivets.bind($('#testResultsPanel'), {
    reportState: reportState
});

// Binders for batch list box
rivets.bind($('#listBox'), {
	batchState: batchState
});
rivets.bind($('#listButton'), {
    batchState: batchState
});

// Binders for list/select box
rivets.bind($('#batchListPanel'), {
    batchState: batchState
});

// Binders for single project search box
rivets.bind($('#searchBox'), {
	searchState: searchState
});
rivets.bind($('#singleSearchButton'), {
    searchState: searchState
});

// Binders for multiple project search box
rivets.bind($('#generateBatchButton'), {
    searchState: searchState
});
rivets.bind($('#generateBox'), {
    batchState: batchState,
    searchState: searchState
});

// Binders for import box
rivets.bind($('#fileUploadBox'), {
    batchState: batchState
});
rivets.bind($('#importButton'), {
    batchState: batchState
});

/*
// Multiple result alert box
rivets.bind($('.multiple-alert'), {
	searchState: searchState
});
*/

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
// Allows user to change global settings
rivets.bind($('#settingsModal'), {
	globalState: globalState
});

// Allows client to display progress on batch job
rivets.bind($('#progressBar'), {
    percentageState: percentageState
});

/*TODO - Why do these need to be commented out, without these commented
out projectReportState.<function> is no longer a function according to rivets in the html
rivets.bind($('#testCompareSelectPanel'), {
    projectReportState: projectReportState
});
rivets.bind($("#testCompareRunAlert"), {
    projectReportState: projectReportState
});
rivets.bind($("#testCompareTablePanel"), {
    projectReportState: projectReportState
});
*/

/*Is this still needed?
rivets.bind($('#reportSelector'), {
    reportState: reportState
});
*/

// Jenkins Tab Bindings
rivets.bind($('#jenkinsManageButton'), {
    jenkinsState: jenkinsState
});
rivets.bind($('#jenkinsLink'), {
    globalState: globalState
});

rivets.bind($('#jenkinsPanel'), {
    jenkinsState: jenkinsState,
    percentageState: percentageState
});
rivets.configure({
    handler : function(context, ev, binding) {
        this.call(binding.observer.target, ev, binding.view.models);
    }
});

// Disables all views except loading view
function switchToLoadingState() {
	//searchState.ready = false;
	detailState.ready = false;
    projectReportState.prjCompareReady = false;
    projectReportState.prjTableReady = false;
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
			auto: autoselect,
            panel: "single"
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
				batchState.exportReady = true;
			};
		});
		detailState.autoSelected = false;
        if(data.panel === "generate") {
            console.log("generate");
		    searchState.generateResults = data.results;
		    loadingState.loading = false;
		    searchState.generateReady = true;
        }
        else if(data.panel === "single") {
            console.log("single");
		    searchState.singleResults = data.results;
		    loadingState.loading = false;
		    searchState.ready = true;
        }
	} else if (data.type === "detail") {
		// Got single repository result, show detail page
		detailState.autoSelected = true;
		showDetail(data);
	}
}

// Updates percentages by polling a tab on the jenkins page
function processProgressBar(data) {
    if (data.status !== "ok") {
        console.log("Bad response from /progress!");
        console.log(data);
    } else {
        percentageState.totalNumberOfJobs = data.results[0][0] + data.results[0][1] + data.results[0][2] + data.results[0][3];
        percentageState.unfinishedJobs = data.results[0][0];
        percentageState.failingJobs = data.results[0][1];
        percentageState.unstableJobs = data.results[0][2];
        percentageState.successfulJobs = data.results[0][3];

        percentageState.dangerPercentage = "width: " + data.results[1][1] + "%;";
        percentageState.warningPercentage = "width: " + data.results[1][2] + "%;";
        percentageState.successPercentage = "width: " + data.results[1][3] + "%;";
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
    projectReportState.selectedProjects = [];
    projectReportState.projects = [];
    projectReportState.projectsTable.clear();
    if (data === undefined || data.status != "ok") {
        console.log("Error");// TODO error message
    } else {
        var prjRegex = /(.*?) - (.*?) - (.*?)-(.*)\.(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d)/;
        var filterRegex = new RegExp(reportState.projectFilter.toLowerCase());
        for (var project in data.results) {
            if (project !== undefined) {
                prjObject = prjRegex.exec(data.results[project][0]);
                if (prjObject === null) {
                    continue;
                }
                if (filterRegex.exec(data.results[project][0].toLowerCase()) === null) {
                    continue;
                }
                var prjId = data.results[project][0];
                // HTML element's 'id' attribute can't have spaces
                prjId = CryptoJS.MD5(prjId);
                projectReportState.projects.push({
                     fullName: prjObject[0],
                           id: prjId+data.results[project][1],
                         name: prjObject[3],
                          env: prjObject[2],
                           os: "", // TODO
                      version: prjObject[4],
                    completed: prjObject[5],
                   repository: data.results[project][1],
                 selectStatus: false,
                    selectBtn: '<a rv-href="#" rv-on-click="project.select">'+
                               '<button type="button" class="btn" rv-id="'+
                               prjId+data.results[project][1]+
                               '<span class="glyphicon glyphicon-remove"></span>'+
                               'Select</button></a>',
                       select: function(ev) {
                           projectReportState.selectProject(ev.target.id);
                       }
                });
                projectReportState.projectsTable.row.add({
                     fullName: prjObject[0],
                           id: prjId+data.results[project][1],
                         name: prjObject[3],
                          env: prjObject[2],
                           os: "",
                      version: prjObject[4],
                    completed: prjObject[5],
                   repository: data.results[project][1],
                 selectStatus: false,
                    selectBtn: '<a rv-href="#" onClick="projectReportState.selectProject(\''+
                               prjId+data.results[project][1]+'\')">'+
                               '<button type="button" class="btn" id="'+
                               prjId+data.results[project][1]+'">'+
                               '<span class="glyphicon glyphicon-remove"></span>'+
                               'Select</button></a>',
                       select: function(ev) {
                           projectReportState.selectProject(ev.target.id);
                       }
                });
            }
        }
        searchState.ready = false;
        detailState.autoSelected = false;
        loadingState.loading = false;
        projectReportState.prjCompareReady = true;
        projectReportState.projectsTable.draw();
    }
}

function processBuildResults(data) {
    var tableContent = "";
    if (data.status != "ok") {
        tableContent = "<tr><th>Error</th><th>"+data.error+"</th></td>";
    } else {
        var leftHeader = "";
        var rightHeader = "";
        if (data.leftProject.Architecture !== data.rightProject.Architecture) {
            leftHeader = data.leftProject.Architecture;
            rightHeader = data.rightProject.Architecture;
        } else if (data.leftProject.Version !== data.rightProject.Version) {
            leftHeader = data.leftProject.Version;
            rightHeader = data.rightProject.Version;
        } else {
            leftHeader = data.leftProject.Date;
            rightHeader = data.rightProject.Date;
        }
        tableContent = "<tr><th>Test</th><th colspan=\"4\">";
        tableContent += leftHeader + "</th><th colspan=\"4\">";
        tableContent += rightHeader + "</th></tr>";
        tableContent += "<tr><th/><th class=\"testResultArch\">T</th><th>F</th><th>E</th><th>S</th>";
        tableContent += "<th class=\"testResultArch\">T</th><th>F</th><th>E</th><th>S</th></tr>";
        var suiteKeys = Object.keys(data.results.results);
        for (var key in suiteKeys) {
            tableContent += "<tr><th class=\"testSuite\">" +
                 suiteKeys[key] +
                "</th><th class=\"testResultArch testSuite\" colspan=\"4\"/><th class=\"testResultArch testSuite\" colspan=\"4\"/></tr>";
            var testKeys = Object.keys(data.results.results[suiteKeys[key]]);
            for (testKey in testKeys) {
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
        tableContent += "<tr><th>Totals</th><th class=\"testResultArch\">"+
            data.results["total"][data.leftCol]+"</th><th class=\"testResult\">"+
            data.results["failures"][data.leftCol]+"</th><th class=\"testResult\">"+
            data.results["errors"][data.leftCol]+"</th><th class=\"testResult\">"+
            data.results["skipped"][data.leftCol]+"</th><th class=\"testResultArch\">"+
            data.results["total"][data.rightCol]+"</th><th class=\"testResult\">"+
            data.results["failures"][data.rightCol]+"</th><th class=\"testResult\">"+
            data.results["errors"][data.rightCol]+"</th><th class=\"testResult\">"+
            data.results["skipped"][data.rightCol]+"</th></tr>";
    }
    $("#testResultsTable").html(tableContent);
    $("#prjHeader").html("for " + data.leftProject.Package + " version " +
        data.leftProject.Version + " on " + data.leftProject.Architecture +
        " / " + data.rightProject.Package + " version " +
        data.rightProject.Version + " on " + data.rightProject.Architecture);
    loadingState.loading = false;
    projectReportState.prjTableReady = true;
}

function processTestDetail(data) {
    if (data.status != "ok") {
        tableContent = "<tr><th>Error</th><th>"+data.error+"</th></td>";
    } else {
        // based on the compare table
        var tableContent = "";
        for (project in data.results) {
            tableContent += "<tr><th colspan=\"5\"><h3>"+
                data.results[project].project["Package"]+" version "+
                data.results[project].project["Version"]+" on "+
                data.results[project].project["Architecture"]+" / repository: "+
                data.results[project].repository+"</h3></th></tr>";
            tableContent += "<tr><th>Test</th>";
            tableContent += "<th class=\"testResultArch\">T</th><th>F</th><th>E</th><th>S</th></tr>";

            var suiteKeys = Object.keys(data.results[project].results.results);
            for (var key in suiteKeys) {
                tableContent += "<tr><th class=\"testSuite\">" +
                     suiteKeys[key] +
                    "</th><th class=\"testResultArch testSuite\" colspan=\"4\"/></tr>";
                var testKeys = Object.keys(data.results[project].results.results[suiteKeys[key]]);
                for (testKey in testKeys) {
                    var tc = data.results[project].results.results[suiteKeys[key]][testKeys[testKey]];
                    if (tc === undefined ||
                        tc["total"] === undefined ||
                        tc["failures"] === undefined ||
                        tc["errors"] === undefined ||
                        tc["skipped"] === undefined)
                        continue;
                    tableContent += "<tr><td class=\"testClass\">"+testKeys[testKey]+
                        "</td><td class=\"testResultArch\">"+
                        tc["total"]+"</td><td class=\"testResult\">"+
                        tc["failures"]+"</td><td class=\"testResult\">"+
                        tc["errors"]+"</td><td class=\"testResult\">"+
                        tc["skipped"]+"</td></tr>";
                    
                }
            }
            tableContent += "<tr><th>Totals</th><th class=\"testResultArch\">"+
                data.results[project].results["total"]+"</th><th class=\"testResult\">"+
                data.results[project].results["failures"]+"</th><th class=\"testResult\">"+
                data.results[project].results["errors"]+"</th><th class=\"testResult\">"+
                data.results[project].results["skipped"]+"</th></tr>";
        }
    }
    $("#testResultsTable").html(tableContent);
    loadingState.loading = false;
    projectReportState.prjTableReady = true;
}

function processTestHistory(data) {
    if (data.status != "ok") {
        tableContent = "<tr><th>Error</th><th>"+data.error+"</th></td>";
    } else {
        // based on the compare table
        var tableContent = "";
        for (project in data.results) {
            tableContent += "<tr><th colspan=\"5\"><h3>"+
                data.results[project].name+"</h3></th></tr>";
            tableContent += "<tr><th>Date / repository</th>";
            tableContent += "<th class=\"testResultArch\">T</th><th>F</th><th>E</th><th>S</th></tr>";

            for (var dateRes in data.results[project].results) {
                tableContent += "<tr><td class=\"testClass\">" +
                     data.results[project].results[dateRes].project.Date +
                     " / " + data.results[project].results[dateRes].repository +
                    "</td>";
                var tc = data.results[project].results[dateRes].results;
                if (tc === undefined ||
                    tc["total"] === undefined ||
                    tc["failures"] === undefined ||
                    tc["errors"] === undefined ||
                    tc["skipped"] === undefined) {
                    tableContent += "<td class=\"testResult\" colspan=\"4\"></td></tr>";
                    continue;
                }
                tableContent += "<td class=\"testResultArch\">"+
                    tc["total"]+"</td><td class=\"testResult\">"+
                    tc["failures"]+"</td><td class=\"testResult\">"+
                    tc["errors"]+"</td><td class=\"testResult\">"+
                    tc["skipped"]+"</td></tr>";
            }
        }
    }
    $("#testResultsTable").html(tableContent);
    loadingState.loading = false;
    projectReportState.prjTableReady = true;
}

function archiveCallback(data) {
    // TODO show a confirmation or error dialog
    console.log("TODO");
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

// assign variables in global state
function initCallback(data) {
    if (data.status !== "ok") {
        console.log("Bad response from /init!");
        console.log(data);
    }
    globalState.hasInit = true;
    globalState.jenkinsUrlInit = data.jenkinsUrl;
    globalState.localPathForTestResultsInit = data.localPathForTestResults;
    globalState.pathForTestResultsInit = data.pathForTestResults;
    globalState.localPathForBatchFilesInit = data.localPathForBatchFiles;
    globalState.pathForBatchFilesInit = data.pathForBatchFiles;
    globalState.githubTokenInit = data.githubToken;
    globalState.configUsernameInit = data.configUsername;
    globalState.configPasswordInit = data.configPassword;

    globalState.jenkinsUrl = data.jenkinsUrl;
    globalState.localPathForTestResults = data.localPathForTestResults;
    globalState.pathForTestResults = data.pathForTestResults;
    globalState.localPathForBatchFiles = data.localPathForBatchFiles;
    globalState.pathForBatchFiles = data.pathForBatchFiles;
    globalState.githubToken = data.githubToken;
    globalState.configUsername = data.configUsername;
    globalState.configPassword = data.configPassword;
}

function settingsCallback(data) {
	if (data.status != "ok") {
		console.log("Bad response from /settings!");
		console.log(data);
	}
}

function uploadBatchFileCallback(data) {
    console.log("In uploadBatchFileCallback");
    if (data.status !== "ok") {
        window.alert(data.error);
    }
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
        percentageState.updateProgressBar();
	} else {
		console.log("Bad response from /createJob!");
		console.log(data);
	}
}

$(document).ready(function() {
    projectReportState.projectsTable = $("#projectListTable").DataTable({
        order: [[4, "desc"]],
        ordering: true,
        paging: true,
        searching: false,
        data: projectReportState.projects,
        columns: [
            { "data": "name", "ordering": "true" },
            { "data": "version", "ordering": "true" },
            { "data": "env", "ordering": "true" },
            { "data": "os", "ordering": "true" },
            { "data": "completed", "ordering": "true" },
            { "data": "repository", "ordering": "true" },
            { "data": "selectStatus", "ordering": "false", "render": function(data, type, row) {
                return '<a rv-href="#" onClick="projectReportState.selectProject(\''+
                               row.id+'\')">'+
                               '<button type="button" class="btn'+(data?' btn-primary':'')+
                               '" id="'+
                               row.id+'">'+
                               '<span class="glyphicon glyphicon-'+
                               (data?'ok':'remove')+
                               '"></span>'+
                               'Select</button></a>';
            } }
        ]
    });
});
