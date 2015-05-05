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
        if (ev.target.id === "searchTab") {
            globalState.isSearchTabActive = true;
            globalState.isBatchTabActive = false;
            globalState.isReportsTabActive = false;
        }
        else if (ev.target.id === "batchTab") {
            globalState.isSearchTabActive = false;
            globalState.isBatchTabActive = true;
            globalState.isReportsTabActive = false;
        }
        else if (ev.target.id === "reportsTab") {
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
               username: configUsername, password: configPassword}, settingsCallback, "json").fail(settingsCallback);
    }
};

if (!globalState.hasInit) {
    $.post("/init", {}, initCallback, "json").fail(initCallback);
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
        $.getJSON("/progress", {}, processProgressBar).fail(processProgressBar);
    }
};

// Contains state of searching operations
var searchState = {
    single: {searchBoxReady: false,
            ready: false,
            exportReady: false, // Whether or not to draw the export batch file view
            sorting: "relevance",
            query: "",
            results: {},
            batchFile: {
                config: {
                    name : "",
                    owner : "",
                    java : ""
                },
                packages: []
            },
            removed: {
                config:   {},
                packages: []
            },
            removeBatchFile: function (ev) {
                clearBatchFile(searchState.single.batchFile);
            },
            download: function (ev) {
                if (searchState.single.batchFile.config.name === "") {
                    searchState.single.batchFile.config.name = 
                        searchState.single.batchFile.packages[0].name +
                        "-" + String(searchState.single.batchFile.packages.length);
                }
                var json = JSON.stringify(searchState.single.batchFile, undefined, 2);
                var data = "data: application/octet-stream;charset=utf-8," + encodeURIComponent(json);
                window.open(data);
                // TODO: Check return code of window.open() to determine if request was cancelled
                clearBatchFile(searchState.single.batchFile);
            },
            save: function (ev) {
                if (searchState.single.batchFile.config.name === "") {
                    searchState.single.batchFile.config.name = 
                        searchState.single.batchFile.packages[0].name +
                        "-" + String(searchState.single.batchFile.packages.length);
                }
                var name = searchState.single.batchFile.config.name;
                var file = JSON.stringify(searchState.single.batchFile, undefined, 2);

                $.post("/uploadBatchFile", {name: name, file: file},
                    singleSaveCallback, "json").fail(uploadBatchFileCallback);
            },
            setSearchBox: function (ev) {
                searchState.single.searchBoxReady = (searchState.single.searchBoxReady) ? false : true;
            },
            changeSort: function (ev) { // Called upon changing sort type
                searchState.single.sorting = $(ev.target).text().toLowerCase();
                doSearch();
            },
            loadingState: {
                loading: false
            }
    },
    multiple: {searchBoxReady: false,
              ready: false,
              results: {},
              batchFile: {
                  config: {
                      name : "",
                      owner : "",
                      java : ""
                  },
                  packages: []
              },
              removed: {
                  config:   {},
                  packages: []
              },
              download: function (ev) {
                  for (var i = 0; i < searchState.multiple.results.length; ++i) {
                      var result = searchState.multiple.results[i];
                      searchState.multiple.batchFile.packages.push(result);
                  }
                  if (searchState.multiple.batchFile.config.name === "") {
                      searchState.multiple.batchFile.config.name =
                          searchState.multiple.batchFile.packages[0].name +
                          "-" + String(searchState.multiple.batchFile.packages.length);
                  }
                  var json = JSON.stringify(searchState.multiple.batchFile, undefined, 2);
                  var data = "data: application/octet-stream;charset=utf-8," + encodeURIComponent(json);
                  window.open(data);

                  // TODO: Check return code of window.open() to determine if request was cancelled
                  clearBatchFile(searchState.multiple.batchFile);
              },
              save: function (ev) {
                  for (var i = 0; i < searchState.multiple.results.length; ++i) {
                      var result = searchState.multiple.results[i];
                      searchState.multiple.batchFile.packages.push(result);
                  }
                  if (searchState.multiple.batchFile.config.name === "") {
                      console.log("Save name: ", searchState.multiple.batchFile.packages[0].name);
                      searchState.multiple.batchFile.config.name =
                          searchState.multiple.batchFile.packages[0].name +
                          "-" + String(searchState.multiple.batchFile.packages.length);
                  }
                  var name = searchState.multiple.batchFile.config.name;
                  var file = JSON.stringify(searchState.multiple.batchFile, undefined, 2);

                  $.post("/uploadBatchFile", {name: name, file: file},
                      multipleSaveCallback, "json").fail(uploadBatchFileCallback);
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
                          q:       "stars:>" + searchState.multiple.query.stars +
                                   " forks:>" + searchState.multiple.query.forks +
                                   (searchState.multiple.query.language == "any" ? "" : (" language:" + searchState.multiple.query.language)),
                          sort:    searchState.multiple.query.sort,

                          // AutoPort parameters
                          limit:   searchState.multiple.query.limit,
                          version: searchState.multiple.query.version,
                          panel:   "generate"
                      };

                      console.log(data);
                      searchState.multiple.ready = false;
                      searchState.multiple.loadingState.loading = true;
                      $.getJSON("/search/repositories", data, processSearchResults).fail(processSearchResults);
                  }
              },
              loadingState: {
                  loading: false
              }
    }
};

function clearBatchFile(batchfile) {
    if (batchfile == searchState.single.batchFile) {
        searchState.single.batchFile.config.name = "";
        searchState.single.batchFile.config.owner = "";
        searchState.single.batchFile.config.java = "";
        searchState.single.batchFile.packages = [];
        searchState.single.exportReady = false;
        searchState.single.ready = false;
    } else {
        searchState.multiple.batchFile.config.name = "";
        searchState.multiple.batchFile.config.owner = "";
        searchState.multiple.batchFile.config.java = "";
        searchState.multiple.batchFile.packages = [];
        searchState.multiple.exportReady = false;
        searchState.multiple.ready = false;
    }
};

var batchState = {
    // Member variables and methods for viewing different panels within the batch tab
    showImportPanel: false, // Draw import panel condition
    showListPanel: false,   // Draw list/select panel condition
    setListPanel: function () {
        batchState.showListPanel = !batchState.showListPanel;
    },
    setImportPanel: function () {
        batchState.showImportPanel = !batchState.showImportPanel;
    },
    
    // Import member variables and methods
    upload: function (ev) {
        var file = $('#batchFile')[0].files[0]; 
        
        if (file) {
            var reader = new FileReader();
            reader.readAsText(file);

            reader.onload = function(e) {
                var batchFile = JSON.parse(e.target.result);
                name = batchFile.config.name;
                $.post("/uploadBatchFile", {name: name, file: e.target.result},
                    uploadBatchFileCallback, "json").fail(uploadBatchFileCallback);
            };	
        }
    },

    // List/Select member variables and methods
    showListSelectTable: false, // Draw list/select table
    fileList: [],               // Stores batch files found in list/select
    listLocalBatchFiles: function(ev) {
        batchState.showListSelectTable = false;
        $.getJSON("/listBatchFiles/local", { filter: $("#batchFileFilter").val() },
            listBatchFilesCallback).fail(listBatchFilesCallback);
    },
    listArchivedBatchFiles: function(ev) {
        batchState.showListSelectTable = false;
        $.getJSON("/listBatchFiles/gsa", { filter: $("#batchFileFilter").val() },
            listBatchFilesCallback).fail(listBatchFilesCallback);
    },
    listAllBatchFiles: function(ev) {
        batchState.showListSelectTable = false;
        $.getJSON("/listBatchFiles/all", { filter: $("#batchFileFilter").val() },
            listBatchFilesCallback).fail(listBatchFilesCallback);
    },

    // Actions for individual batch files
    buildAndTest: function (ev, el) {
        $.post("/runBatchFile", {batchName: el.file.filename},
            runBatchFileCallback, "json").fail(runBatchFileCallback);
    }
};

// Contains state of detail view
var detailState = {
    ready: false,
    generateReady: false,
    repo: null,                                     // Single project search repo data
    generateRepo: null,                             // Multiple project search repo data
    autoSelected: false,                            // Was this repository autoselected from search query?
    pie: null, // Pie chart
    generatePie: null,
    //TODO - split single and generate out, this repetition is bad
    javaType: "Open JDK", // Open JDK or IBM Java
    generateJavaType: "Open JDK",
    javaTypeOptions: "",
    generateJavaTypeOptions: "",
    backToResults: function(ev) {
        var idName = ev.target.id;
        if (idName === "singleDetailBackButton") {
            detailState.ready = false;
            if (searchState.single.results.length > 0) {
                searchState.single.ready = true;
            }
        }
        else if (idName === "generateDetailBackButton") {
            detailState.generateReady = false;
            if (searchState.multiple.results.length > 0) {
                searchState.multiple.ready = true;
            }
        }
    },
    exitAutoSelect: function() {
        detailState.ready = false;
        detailState.autoSelected = false;
        doSearch(false);
    },
    // When the radio button is pressed update the server environment data
    selectJavaType: function(ev) {
        var selection = $(ev.target).text().toLowerCase();
        if (selection === "open jdk") {
            detailState.javaType = "Open JDK";
            detailState.javaTypeOptions = "";
    	}
    	else if (selection === "ibm java") {
            detailState.javaType = "IBM Java";
            detailState.javaTypeOptions = "JAVA_HOME=/opt/ibm/java";
    	}
    },
    // TODO - this is bad, this will be changed
    selectGenerateJavaType: function(ev) {
        var selection = $(ev.target).text().toLowerCase();
    	if (selection === "open jdk") {
            detailState.generateJavaType = "Open JDK";
            detailState.generateJavaTypeOptions = "";
    	}
    	else if (selection === "ibm java") {
            detailState.generateJavaType = "IBM Java";
            detailState.generateJavaTypeOptions = "JAVA_HOME=/opt/ibm/java";
    	}
    },
    changeBuildOptions: function(ev) {
        if (ev.target.className === "singleSearch") {
            detailState.repo.build.selectedBuild = ev.target.text;
        }
        else if (ev.target.className === "generateSearch") {
            detailState.generateRepo.build.selectedBuild = ev.target.text;
        }
    },
    changeTestOptions: function(ev) {
        if (ev.target.className === "singleSearch") {
            detailState.repo.build.selectedTest = ev.target.text;
        }
        else if (ev.target.className === "generateSearch") {
            detailState.generateRepo.build.selectedTest = ev.target.text;
        }
    },
    changeEnvOptions: function(ev) {
        if (ev.target.className === "singleSearch") {
            detailState.repo.build.selectedEnv = ev.target.text;
        }
        else if (ev.target.className === "generateSearch") {
            detailState.generateRepo.build.selectedEnv = ev.target.text;
        }
    },
    addToBatchFile: function(ev) {
        searchState.single.batchFile.packages.push(detailState.repo);
        searchState.single.exportReady = true;
        detailState.ready = false;
        detailState.autoSelected = false;
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
        projectReportState.prjCompareReady = false;
        projectReportState.prjTableReady = false;
        
        projectReportState.compareType = "project";
        projectReportState.compareRepo = "local";
        $.getJSON("/listTestResults/local", { filter: $("#projectFilter").val() }, processResultList).fail(processResultList);
        $("#resultArchiveBtn").show();
    },
    listGSAProjects: function(ev) {
        projectReportState.prjCompareReady = false;
        projectReportState.prjTableReady = false;
        
        projectReportState.compareType = "project";
        projectReportState.compareRepo = "archived";
        $.getJSON("/listTestResults/gsa", { filter: $("#projectFilter").val() }, processResultList).fail(processResultList);
        $("#resultArchiveBtn").hide();
    },
    listAllProjects: function(ev) {
        projectReportState.prjCompareReady = false;
        projectReportState.prjTableReady = false;
        
        projectReportState.compareType = "project";
        projectReportState.compareRepo = "all";
        $.getJSON("/listTestResults/all", { filter: $("#projectFilter").val() }, processResultList).fail(processResultList);
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
    nodeNames: [],
    nodeLabels: [],
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
        //TODO - add loading bar
        projectReportState.prjCompareReady = false;
        projectReportState.prjTableReady = false;
        $.ajax({
                type: "POST",
         contentType: "application/json; charset=utf-8",
                 url: "/getTestHistory",
                data: JSON.stringify({
                        projects: query
                      }),
             success: processTestHistory,
            dataType:'json'
        }).fail(processTestHistory);
    },
    testDetail: function() {
        var sel = Object.keys(projectReportState.selectedProjects);
        var query = {};
        for (proj in sel) {
            query[sel[proj]] = projectReportState.selectedProjects[sel[proj]];
        }
        //TODO - add loading bar
        projectReportState.prjCompareReady = false;
        projectReportState.prjTableReady = false;
        $.ajax({
                type: "POST",
         contentType: "application/json; charset=utf-8",
                 url: "/getTestDetail",
                data: JSON.stringify({
                        projects: query
                      }),
             success: processTestDetail,
            dataType:'json'
        }).fail(processTestDetail);
    },
    compareResults: function() {
        var sel = Object.keys(projectReportState.selectedProjects);
        if (sel.length === 2) {
            var leftProject = sel[0];
            var rightProject = sel[1];
            var leftRepo = projectReportState.selectedProjects[leftProject];
            var rightRepo = projectReportState.selectedProjects[rightProject];
            //TODO - add loading bar
            projectReportState.prjCompareReady = false;
            projectReportState.prjTableReady = false;
            $.getJSON("/getTestResults",
                      {
                        leftbuild: leftProject,
                        rightbuild: rightProject,
                        leftrepository: leftRepo,
                        rightrepository: rightRepo
                      },
                      processBuildResults).fail(processBuildResults);
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
        }).fail(archiveCallback);
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
    percentageState: percentageState
});

// Does the above and makes a search query
function doSearch(autoselect) {
    if (typeof(autoselect)==='undefined') autoselect = true;
    if (typeof(autoselect)!=='boolean') autoselect = true;
	
    // Do not switch to loading state if query is empty
    searchState.single.query = $('#query').val();
    if (searchState.single.query.length > 0) {
        searchState.single.ready = false;
        searchState.single.loadingState.loading = true;
        $.getJSON("/search", {
               q: searchState.single.query,
            sort: searchState.single.sorting,
            auto: autoselect,
           panel: "single"
		}, processSearchResults).fail(processSearchResults);
	}
}

// When the query textbox is changed, do a search
$('#query').change(doSearch);

$('#batchFile').change(function () {
    $('#uploadFilename').val("File selected:  " + $('#batchFile').val());
});

function showAlert(message, data) {
    var text = message;
    if (typeof data !== "undefined") {
        text += "<br/>" + (data.responseJSON !== undefined ?
                            (data.responseJSON.error !== undefined ?
                              data.responseJSON.error :
                              data.error) :
                            data.error);
    }
    $("#apErrorDialogText").html(text);
    $("#errorAlert").modal();
}

// Callback for when we receive data from a search query request
function processSearchResults(data) {
    if (data.status !== "ok") {
        showAlert("Bad response from /search!", data);
    } else if (data.type === "multiple") {

        // Got multiple results
        // Add select function to each result
        data.results.forEach(function(result) {
            // Show detail view for repo upon selection
            result.select = function (ev) {
                var className = $(ev.target).attr('class');
                if (className === "generateDetailButton btn btn-primary") {
                    $.getJSON("/detail/" + result.id, {panel: "generate"}, showDetail).fail(showDetail);
                    searchState.multiple.ready = false;
                    searchState.multiple.loadingState.loading = true;
                }
                else if (className === "singleDetailButton btn btn-primary") {
                    $.getJSON("/detail/" + result.id, {panel: "single"}, showDetail).fail(showDetail);
                    searchState.single.ready = false;
                    searchState.single.loadingState.loading = true;
                }
            };
            result.addToBatchFile = function (ev) {
                var i = data.results.indexOf(result);
                var ele = data.results.splice(i, 1);
                searchState.single.batchFile.packages.push(result);
                if (data.results.length === 0) {
                    searchState.single.ready = false;
                }
                searchState.single.exportReady = true;
            };
            result.remove = function (ev) {
                var i = data.results.indexOf(result);
                var ele = data.results.splice(i, 1);
                searchState.multiple.removed.packages.push(ele);
                if (data.results.length === 0) {
                    searchState.multiple.ready = false;
                }
            };
        });

        if (data.panel === "generate") {
            searchState.multiple.results = data.results;
            searchState.multiple.loadingState.loading = false;
            searchState.multiple.ready = true;
        }
        else if (data.panel === "single") {
            searchState.single.results = data.results;
            searchState.single.loadingState.loading = false;
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
        showAlert("Bad response from /progress!", data);
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
        //TODO - add loading bar
        projectReportState.prjCompareReady = false;
        projectReportState.prjTableReady = false;
        
        $.getJSON("/listTestResults", {}, processResultList).fail(processResultList);
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
        showAlert("Error:", data);
    } else {
        var prjRegex = /(.*?)\.(.*?)\.(.*?)\.N-(.*?)\.(.*?)\.(\d\d\d\d-\d\d-\d\d-.\d\d-.\d\d-.\d\d)/;
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
                     hostname: prjObject[1],
                          uid: prjObject[2],
                         name: prjObject[4],
                          env: prjObject[3],
                           os: "", // TODO
                      version: prjObject[5],
                    completed: prjObject[6],
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
                     hostname: prjObject[1],
                          uid: prjObject[2],
                         name: prjObject[4],
                          env: prjObject[3],
                           os: "", // TODO
                      version: prjObject[5],
                    completed: prjObject[6],
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
        projectReportState.prjCompareReady = true;
        projectReportState.projectsTable.draw();
    }
}

function processBuildResults(data) {
    var tableContent = "";
    if (data.status != "ok") {
        showAlert("Error:", data);
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
        $("#prjHeader").html("for " + data.leftProject.Package + " version " +
            data.leftProject.Version + " on " + data.leftProject.Architecture +
            " / " + data.rightProject.Package + " version " +
            data.rightProject.Version + " on " + data.rightProject.Architecture);
    }
    $("#testResultsTable").html(tableContent);
    projectReportState.prjTableReady = true;
}

function processTestDetail(data) {
    if (data.status != "ok") {
        showAlert("Error:", data);
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
    projectReportState.prjTableReady = true;
}

function processTestHistory(data) {
    var tableContent = "";
    if (data.status != "ok") {
        showAlert("Error:", data);
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
    // refetch the list as previously checked
    reportState.listLocalProjects();
    handleProjectListBtns();
    $("#archiveCallbackText").html(text);
    $("#archiveCallbackAlert").modal();
}

function getSelectedValues(select) {
    var result = [];
    var options = select && select.options;
    var opt;

    for(var i=0, iLen=options.length; i<iLen; i++) {
        opt = options[i];

        if(opt.selected) {
            result.push(opt.value || opt.text);
        }
    }
    return result;
}

// Sets up and opens detail view for a repo
function showDetail(data) {
    if (data.status !== "ok" || data.type !== "detail") {
        showAlert("Bad response while creating detail view!", data);
    } else {
        if (data.panel === "single") {
            detailState.repo = data.repo;
            console.log(data.repo.build);
            detailState.repo.addToJenkins = function(e) {
                var buildInfo = detailState.repo.build;
        
                var selectedBuild = $("#singleSelectedBuild").val();
                selectedBuild = selectedBuild === "NA" ? "" : selectedBuild;
        
                var selectedTest = $("#singleSelectedTest").val();
                selectedTest = selectedTest === "NA" ? "" : selectedTest;
        
                var selectedEnv = $("#singleSelectedEnv").val();
                selectedEnv = selectedEnv === "NA" ? "" : selectedEnv;
        
                var el = $("#singleBuildServers")[0];
                var buildServers = getSelectedValues(el);

                for(var i=0; i < buildServers.length; i++) {
                    console.log(detailState.repo.useVersion + " version");
                    $.post("/createJob", {id: detailState.repo.id, tag: detailState.repo.useVersion, javaType: detailState.javaTypeOptions, node: buildServers[i], selectedBuild: selectedBuild, selectedTest: selectedTest, selectedEnv: selectedEnv, artifacts: buildInfo.artifacts}, addToJenkinsCallback, "json").fail(addToJenkinsCallback);
                }
            };
            detailState.repo.updateVersion = function(e) {
                detailState.repo.useVersion = e.target.innerHTML;
            };
            searchState.single.loadingState.loading = false;
            detailState.ready = true;
            // Make chart
            var ctx = $("#langChart").get(0).getContext("2d");
            if (detailState.pie !== null) {
                detailState.pie.destroy();
            }
            detailState.pie = new Chart(ctx).Pie(detailState.repo.languages, { segmentShowStroke: false });
            legend(document.getElementById('langLegend'), detailState.repo.languages);
        }
        else if (data.panel === "generate") {
            var buildInfo = data.repo.build;
            detailState.generateRepo = data.repo;
            detailState.generateRepo.addToJenkins = function(e) {
                var buildInfo = detailState.generateRepo.build;
                
                var selectedBuild = $("#generateSelectedBuild").val();
                selectedBuild = selectedBuild === "NA" ? "" : selectedBuild;
                
                var selectedTest = $("#generateSelectedTest").val();
                selectedTest = selectedTest === "NA" ? "" : selectedTest;
                
                var selectedEnv = $("#generateSelectedEnv").val();
                selectedEnv = selectedEnv === "NA" ? "" : selectedEnv;
                
                var el = $("#generateBuildServers")[0];
                var buildServers = getSelectedValues(el);

                for(var i=0; i < buildServers.length; i++) {
                    $.post("/createJob", {id: detailState.generateRepo.id, tag: detailState.generateRepo.useVersion, javaType: detailState.generateJavaTypeOptions, node: buildServers[i], selectedBuild: selectedBuild, selectedTest: selectedTest, selectedEnv: selectedEnv, artifacts: buildInfo.artifacts}, addToJenkinsCallback, "json").fail(addToJenkinsCallback);
                }
            };
            detailState.generateRepo.updateVersion = function(e) {
                detailState.generateRepo.useVersion = e.target.innerHTML;
            };
            searchState.multiple.loadingState.loading = false;
            detailState.generateReady = true;
            // Make chart
            var ctx = $("#generateLangChart").get(0).getContext("2d");
            if (detailState.generatePie !== null) {
                detailState.generatePie.destroy();
            }
            detailState.generatePie = new Chart(ctx).Pie(detailState.generateRepo.languages, { segmentShowStroke: false });
            legend(document.getElementById('generateLangLegend'), detailState.generateRepo.languages);
        }
    }
}

// assign variables in global state
function initCallback(data) {
    if (data.status !== "ok") {
        showAlert("Bad response from /init!", data);
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
        showAlert("Bad response from /settings!", data);
    }
}

function uploadBatchFileCallback(data) {
    console.log("In uploadBatchFileCallback");
    if (data.status !== "ok") {
        showAlert("", data);
    }
}

function singleSaveCallback(data) {
    console.log("In singleSaveCallback");
    if (data.status !== "ok") {
        showAlert("", data);
    }
    clearBatchFile(searchState.single.batchFile);
}

function multipleSaveCallback(data) {
    console.log("In multipleSaveCallback");
    if (data.status !== "ok") {
        showAlert("", data);
    }
    clearBatchFile(searchState.multiple.batchFile);
}

function runBatchFileCallback(data) {
    console.log("In runBatchFileCallback");
}

function listBatchFilesCallback(data) {
    if(data.status === "ok") {
        batchState.fileList = data.results;
        batchState.showListSelectTable = true;
    } else {
        showAlert("Error!", data);
    }
}

function addToJenkinsCallback(data) {
    // TODO - need to take in a list of sjobUrls and hjobUrls and then iterate over the list
    if (data.status === "ok") {
        // Open new windows with the jobs' home pages
        window.open(data.hjobUrl,'_blank');
        percentageState.updateProgressBar();
    } else {
        showAlert("Bad response from /createJob!", data);
    }
}

function getJenkinsNodesCallback(data) {
    if (data.status === "ok") {
        for(i = 0; i < data.nodeLabels.length; i++) {
            var name = data.nodeNames[i];
            var label = data.nodeLabels[i];
            if($.inArray(name, jenkinsState.nodeNames) === -1) {
                jenkinsState.nodeNames.push(data.nodeNames[i]);
            }
            if($.inArray(label, jenkinsState.nodeLabels) === -1) {
                jenkinsState.nodeLabels.push(data.nodeLabels[i]);
            }
        }

        console.log(jenkinsState.nodeLabels);
    }
    else {
        showAlert("Could not get Jenkins slaves", data);
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
    
    // NOTE - rivets does not play well with multiselect
    // Query Jenkins for list of build servers
    $.ajax({
        type: 'POST',
        url: "/getJenkinsNodes",
        data: {},
        success: getJenkinsNodesCallback,
        dataType: "json",
        async:false
    });
    // Initialize bootstrap multiselect plugin
    // Config options go here
    $('#singleBuildServers').multiselect({
        buttonClass: "btn btn-primary",
        buttonText: function(options, select) {
            return "Select build system type";
        }
    });
    $('#generateBuildServers').multiselect({
        buttonClass: "btn btn-primary",
        buttonText: function(options, select) {
            return "Select build system type";
        }
    });
});
