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
    single: {searchBoxReady: false,
            ready: false,
            sorting: "relevance",
            query: "",
            results: {},
	        setSearchBox: function (ev) {
                searchState.single.searchBoxReady = (searchState.single.searchBoxReady) ? false : true;
	        },
	        changeSort: function (ev) { // Called upon changing sort type
		        searchState.single.sorting = $(ev.target).text().toLowerCase();
		        doSearch();
	        }
    },
    multiple: {searchBoxReady: false,
              ready: false,
              exportReady: false, // Whether or not to draw the export batch file view
              results: {},
              batchFile: {
                  config:   {},
                  packages: []
              },
              download: function (ev) {
                  console.log("download");
                  var json = JSON.stringify(searchState.multiple.batchFile, undefined, 2);
                  var data = "data: application/octet-stream;charset=utf-8," + encodeURIComponent(json);
                  window.open(data);
              },
	          setSearchBox: function (ev) {
                  searchState.multiple.searchBoxReady = (searchState.multiple.searchBoxReady) ? false : true;
	          },
              query: {
                  limit:    25,
                  sort:     "stars",
                  language: "any",
                  version:  "current",
                  stars:    0,
                  forks:    0,
                  generate: function (ev) {
                      // TODO: remove redundant query qualifiers (stars/forks == 0)
                      detailState.generateReady = false;
                      var data = {
                          // GitHub API parameters
                          q:       " stars:>" + searchState.multiple.query.stars +
                                   " forks:>" + searchState.multiple.query.forks +
                                   (searchState.multiple.query.language == "any" ? "" : (" language:" + searchState.multiple.query.language)),
                          sort:    searchState.multiple.query.sort,

                          // AutoPort parameters
                          limit:   searchState.multiple.query.limit,
                          version: searchState.multiple.query.version,
                          panel: "generate"
                      };

                      console.log(data);
                      switchToLoadingState();
                      $.getJSON("/search/repositories", data, processSearchResults);
                  }
              }
    }
};

var batchState = {
    ready: false, // Whether or not to draw the list/select batch file view
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
    },
    buildAndTest: function (ev, el) { 
	    $.post("/runBatchFile", {batchName: el.result.filename}, runBatchFileCallback, "json");
    },
	setImportBox: function (ev) {
        batchState.importBox = (batchState.importBox) ? false : true;
	}
};

// Contains state of loading view
var loadingState = {
	loading: false // Whether or not to draw this view
};
// Contains state of detail view
var detailState = {
	ready: false,
    generateReady: false,
	repo: null, // Repo data
    generateRepo: null,
	autoSelected: false, // Was this repository autoselected from search query?
	pie: null, // Pie chart
    generatePie: null,
    //TODO - split single and generate out, this repetition is bad
	javaType: "Open JDK", // Open JDK or IBM Java
    generateJavaType: "Open JDK",
    javaTypeOptions: "",
    generateJavaTypeOptions: "",
	backToResults: function(ev) {
        var idName = ev.target.id;
		if(idName === "singleDetailBackButton") {
            detailState.ready = false;
		    searchState.single.ready = true;
        }
        else if(idName === "generateDetailBackButton") {
            detailState.generateReady = false;
		    searchState.multiple.ready = true;
        }
	},
	exitAutoSelect: function() {
        detailState.ready = false;
        detailState.autoSelected = false;
		doSearch(false);
	},
	// When the radio button is pressed update the server environment data
	selectJavaType:	function(ev) {
		var selection = $(ev.target).text().toLowerCase();
    	if(selection === "open jdk") {
            detailState.javaType = "Open JDK";
    		detailState.javaTypeOptions = "";
    	}
    	else if(selection === "ibm java") {
            detailState.javaType = "IBM Java";
    		detailState.javaTypeOptions = "JAVA_HOME=/opt/ibm/java";
    	}
	},
    // TODO - this is bad, this will be changed
	selectGenerateJavaType:	function(ev) {
		var selection = $(ev.target).text().toLowerCase();
    	if(selection === "open jdk") {
            detailState.generateJavaType = "Open JDK";
    		detailState.generateJavaTypeOptions = "";
    	}
    	else if(selection === "ibm java") {
            detailState.generateJavaType = "IBM Java";
    		detailState.generateJavaTypeOptions = "JAVA_HOME=/opt/ibm/java";
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
        $("#resultArchiveBtn").hide();
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
        var sel = Object.keys(projectReportState.selectedProjects);
        var query = {};
        for (proj in sel) {
            query[sel[proj]] = projectReportState.selectedProjects[sel[proj]];
        }
        $.ajax({
                type: "POST",
         contentType: "application/json; charset=utf-8",
                 url: "/archiveProjects",
                data: JSON.stringify({
                        projects: query
                      }),
             success: archiveCallback,
            dataType:'json'
        });
    },
    backToList: function(ev) {
        projectReportState.prjCompareReady = true;
        projectReportState.prjTableReady = false;
    }
};

rivets.bind($('#toolContainer'), {
    globalState: globalState,
    reportState: reportState,
    projectReportState: projectReportState,
    searchState: searchState,
    batchState: batchState,
    detailState: detailState,
    jenkinsState: jenkinsState,
    percentageState: percentageState,
	loadingState: loadingState
});

// Disables all views except loading view
function switchToLoadingState() {
	//detailState.ready = false;
    projectReportState.prjCompareReady = false;
    projectReportState.prjTableReady = false;
	loadingState.loading = true;
	//detailState.autoSelected = false;
}

// Does the above and makes a search query
function doSearch(autoselect) {
	if(typeof(autoselect)==='undefined') autoselect = true;
	if(typeof(autoselect)!=='boolean') autoselect = true;
	
	// Do not switch to loading state if query is empty
	searchState.single.query = $('#query').val();
	if(searchState.single.query.length > 0) {
		switchToLoadingState();
		$.getJSON("/search", {
			q: searchState.single.query,
			sort: searchState.single.sorting,
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
			result.select = function (ev) {
                var className = $(ev.target).attr('class');
                if(className === "generateDetailButton btn btn-primary") {
				    $.getJSON("/detail/" + result.id, {panel: "generate"}, showDetail);
                    searchState.multiple.ready = false;
                }
                else if(className === "singleDetailButton btn btn-primary") {
				    $.getJSON("/detail/" + result.id, {panel: "single"}, showDetail);
                    searchState.single.ready = false;
                }

				switchToLoadingState();
			};
			result.addToBatchFile = function () {
				searchState.multiple.batchFile.packages.push(result);
				searchState.multiple.exportReady = true;
			};
		});
		detailState.autoSelected = false;
        if(data.panel === "generate") {
		    searchState.multiple.results = data.results;
		    loadingState.loading = false;
		    searchState.multiple.ready = true;
        }
        else if(data.panel === "single") {
		    searchState.single.results = data.results;
		    loadingState.loading = false;
		    searchState.single.ready = true;
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
        var prjRegex = /(.*) - (.*?) - (.*?)-(.*)\.(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d)/;
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
                         name: prjObject[1]+" - "+prjObject[3],
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
                         name: prjObject[1]+" - "+prjObject[3],
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
    var tableContent = "";
    if (data.status != "ok") {
        tableContent = "<tr><th>Error</th><th>"+data.error+"</th></td>";
    } else {
        for (var project in data.results) {
            var resultData = {
                results: {},
                duration: {},
                total: {},
                failures: {},
                errors: {},
                skipped: {}
            };
            tableContent += "<tr><th colspan=\"6\"><h3>"+
                data.results[project].name+"</h3></th></tr>";
            tableContent += "<tr><th colspan=\"2\">Test</th><th class=\"testResultArch\" rowspan=\"2\">T</th>"+
                "<th rowspan=\"2\">F</th><th rowspan=\"2\">E</th><th rowspan=\"2\">S</th></tr>";
            tableContent += "<tr><th>Platform</th><th>Date / repository</th></tr>";

            for (var dateRes in data.results[project].results) {
                var testDate = data.results[project].results[dateRes].project.Date;
                var testArch = data.results[project].results[dateRes].project.Architecture;
                var testRepo = data.results[project].results[dateRes].repository;
                var res = data.results[project].results[dateRes].results;
                var suiteKeys = Object.keys(res.results);
                for (var key in suiteKeys) {
                    var testKeys = Object.keys(res.results[suiteKeys[key]]);
                    for (testKey in testKeys) {
                        var tc = res.results[suiteKeys[key]][testKeys[testKey]];
                        if (tc === undefined ||
                            tc["total"] === undefined ||
                            tc["failures"] === undefined ||
                            tc["errors"] === undefined ||
                            tc["skipped"] === undefined)
                            continue;
                        if (resultData.results[suiteKeys[key]] === undefined)
                            resultData.results[suiteKeys[key]] = {};
                        if (resultData.results[suiteKeys[key]][testKeys[testKey]] === undefined)
                            resultData.results[suiteKeys[key]][testKeys[testKey]] = {};
                        if (resultData.results[suiteKeys[key]][testKeys[testKey]][testArch] === undefined)
                            resultData.results[suiteKeys[key]][testKeys[testKey]][testArch] = {};
                        if (resultData.results[suiteKeys[key]][testKeys[testKey]][testArch][testDate+" / "+testRepo] === undefined)
                            resultData.results[suiteKeys[key]][testKeys[testKey]][testArch][testDate+" / "+testRepo] = {};
                        resultData.results[suiteKeys[key]][testKeys[testKey]][testArch][testDate+" / "+testRepo] = {
                            "duration": tc["duration"],
                            "total": tc["total"],
                            "failures": tc["failures"],
                            "errors": tc["errors"],
                            "skipped": tc["skipped"]
                        };
                    }
                }
                if (res === undefined ||
                    res["total"] === undefined ||
                    res["failures"] === undefined ||
                    res["errors"] === undefined ||
                    res["skipped"] === undefined) {
                    continue;
                }
                if (resultData.duration[testArch] === undefined)
                    resultData.duration[testArch] = {};
                if (resultData.duration[testArch][testDate+" / "+testRepo] === undefined)
                    resultData.duration[testArch][testDate+" / "+testRepo] = res["duration"];
                if (resultData.total[testArch] === undefined)
                    resultData.total[testArch] = {};
                if (resultData.total[testArch][testDate+" / "+testRepo] === undefined)
                    resultData.total[testArch][testDate+" / "+testRepo] = res["total"];
                if (resultData.failures[testArch] === undefined)
                    resultData.failures[testArch] = {};
                if (resultData.failures[testArch][testDate+" / "+testRepo] === undefined)
                    resultData.failures[testArch][testDate+" / "+testRepo] = res["failures"];
                if (resultData.errors[testArch] === undefined)
                    resultData.errors[testArch] = {};
                if (resultData.errors[testArch][testDate+" / "+testRepo] === undefined)
                    resultData.errors[testArch][testDate+" / "+testRepo] = res["errors"];
                if (resultData.skipped[testArch] === undefined)
                    resultData.skipped[testArch] = {};
                if (resultData.skipped[testArch][testDate+" / "+testRepo] === undefined)
                    resultData.skipped[testArch][testDate+" / "+testRepo] = res["skipped"];
            }
            var suites = Object.keys(resultData.results);
            for (var suite in suites) {
                tableContent += "<tr><th colspan=\"6\">"+suites[suite]+"</th></tr>";
                var tests = Object.keys(resultData.results[suites[suite]]);
                for (var test in tests) {
                    tableContent += "<tr><td colspan=\"6\">"+tests[test]+"</td></tr>";
                    var platforms = Object.keys(resultData.results[suites[suite]][tests[test]]);
                    for (platform in platforms) {
                        // count the number of dates
                        var dates = Object.keys(resultData.results[suites[suite]][tests[test]][platforms[platform]]);
                        var nbtests = dates.length;
                        var firstRes = false;
                        tableContent += "<tr><td rowspan=\""+nbtests+"\">"+
                            platforms[platform]+
                            "</td>";
                        for (var date in dates) {
                            var res = resultData.results[suites[suite]][tests[test]][platforms[platform]][dates[date]];
                            if (firstRes)
                                tableContent += "<tr>";
                            firstRes = true;
                            tableContent += "<td>"+dates[date]+"</td><td class=\"testResultArch\">"+
                                res.total+"</td><td>"+
                                res.failures+"</td><td>"+
                                res.errors+"</td><td>"+
                                res.skipped+
                                "</td></tr>";
                        }
                    }
                }
            }
            tableContent += "<tr><th colspan=\"6\">Totals</th></tr>";
            var platforms = Object.keys(resultData.total);
            for (var platform in platforms) {
                var dates = Object.keys(resultData.total[platforms[platform]]);
                var nbtests = dates.length;
                var firstRes = false;
                tableContent += "<tr><td rowspan=\""+nbtests+"\">"+platforms[platform]+"</td>";
                for (var date in dates) {
                    if (firstRes)
                        tableContent += "<tr>";
                    firstRes = true;
                    tableContent += "<td>"+dates[date]+"</td><td class=\"testResultArch\">"+
                        resultData.total[platforms[platform]][dates[date]]+"</td><td>"+
                        resultData.failures[platforms[platform]][dates[date]]+"</td><td>"+
                        resultData.errors[platforms[platform]][dates[date]]+"</td><td>"+
                        resultData.skipped[platforms[platform]][dates[date]]+"</td></tr>";
                }
            }
        }
        tableContent += "</table>";
    }
    $("#testResultsTable").html(tableContent);
    loadingState.loading = false;
    projectReportState.prjTableReady = true;
}

function archiveCallback(data) {
    var errors = data.errors;
    var alreadyThere = data.alreadyThere;
    var text = "The selected results have been archived.";
    if (alreadyThere.length !== 0) {
        text += "<br/>The following results were already found in the archive:<br/><ul>";
        for (proj in alreadyThere) {
            text += "<li>" + alreadyThere[proj] + "</li>";
        }
        text += "</ul>";
    }
    if (errors.length !== 0) {
        text = "The following projects could not be saved:<br/><ul>";
        for (error in errors) {
            text += "<li>" + errors[error] + "</li>";
        }
        text += "</ul>";
    }
    $("#archiveCallbackText").html(text);
    $("#archiveCallbackAlert").modal();
}

// Sets up and opens detail view for a repo
// TODO - add check boxes for architectures wanted
function showDetail(data) {
	if(data.status !== "ok" || data.type !== "detail") {
		console.log("Bad response while creating detail view!");
	} else {
		loadingState.loading = false;
        if(data.panel === "single") {
		    detailState.repo = data.repo;
		    detailState.repo.addToJenkins = function(e) {
			    $.post("/createJob", {id: detailState.repo.id, tag: e.target.innerHTML, javaType: detailState.javaTypeOptions, arch: "x86"}, addToJenkinsCallback, "json");
			    $.post("/createJob", {id: detailState.repo.id, tag: e.target.innerHTML, javaType: detailState.javaTypeOptions, arch: "ppcle"}, addToJenkinsCallback, "json");
		    };
		    detailState.ready = true;
		    // Make chart
		    var ctx = $("#langChart").get(0).getContext("2d");
		    if(detailState.pie !== null) {
			    detailState.pie.destroy();
		    }
		    detailState.pie = new Chart(ctx).Pie(detailState.repo.languages, {
			    segmentShowStroke: false
		    });
		    legend(document.getElementById('langLegend'), detailState.repo.languages);
        }
        else if(data.panel === "generate") {
		    detailState.generateRepo = data.repo;
		    detailState.generateRepo.addToJenkins = function(e) {
			    $.post("/createJob", {id: detailState.generateRepo.id, tag: e.target.innerHTML, javaType: detailState.generateJavaTypeOptions, arch: "x86"}, addToJenkinsCallback, "json");
			    $.post("/createJob", {id: detailState.generateRepo.id, tag: e.target.innerHTML, javaType: detailState.generateJavaTypeOptions, arch: "ppcle"}, addToJenkinsCallback, "json");
		    };
		    detailState.generateReady = true;
		    // Make chart
		    var ctx = $("#generateLangChart").get(0).getContext("2d");
		    if(detailState.generatePie !== null) {
			    detailState.generatePie.destroy();
		    }
		    detailState.generatePie = new Chart(ctx).Pie(detailState.generateRepo.languages, {
			    segmentShowStroke: false
		    });
		    legend(document.getElementById('generateLangLegend'), detailState.generateRepo.languages);
        }
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
