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
    useTextAnalyticsInit: false,
    logLevelInit: "",

    jenkinsUrl: "",
    localPathForTestResults: "",
    pathForTestResults: "",
    localPathForBatchFiles: "",
    localPathForBatchTestResults: "",
    pathForBatchFiles: "",
    githubToken: "",
    configUsername: "",
    configPassword: "",
    useTextAnalytics: false,
    logLevel: "INFO",

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
        globalState.useTextAnalytics = globalState.useTextAnalyticsInit;
        document.getElementById('loglevel').value = globalState.logLevelInit;
    },
    updateParameters: function () {
        jenkinsState.loadingState.settingsLoading = true;
        jenkinsUrl = document.getElementById('url').value;
        localPathForTestResults = document.getElementById('ltest_results').value;
        pathForTestResults = document.getElementById('gtest_results').value;
        localPathForBatchFiles = document.getElementById('lbatch_files').value;
        pathForBatchFiles = document.getElementById('gbatch_files').value;
        githubToken = document.getElementById('github').value;
        configUsername = document.getElementById('username').value;
        configPassword = document.getElementById('password').value;
        useTextAnalytics = globalState.useTextAnalytics
        logLevel = document.getElementById('loglevel').value;
        $.post("settings",
               { url: jenkinsUrl,
                 ltest_results: localPathForTestResults, gtest_results: pathForTestResults,
                 lbatch_files: localPathForBatchFiles, gbatch_files: pathForBatchFiles,
                 github: githubToken, username: configUsername, password: configPassword,
                 usetextanalytics: useTextAnalytics, loglevel: logLevel
               },
               settingsCallback, "json").fail(settingsCallback);
    }
};

if (!globalState.hasInit) {
    $.post("init", {}, initCallback, "json").fail(initCallback);
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
        $.getJSON("progress", {}, processProgressBar).fail(processProgressBar);
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
                var json = JSON.stringify(batchState.convertToExternal(searchState.single.batchFile),
                    undefined, 2);
                var blob = new Blob([json], {type: "text/plain;charset=utf-8"});
                saveAs(blob, searchState.single.batchFile.config.name);

                // TODO: Check return code of saveAs() to determine if request was cancelled
                clearBatchFile(searchState.single.batchFile);
            },
            save: function (ev) {
                if (searchState.single.batchFile.config.name === "") {
                    searchState.single.batchFile.config.name =
                        searchState.single.batchFile.packages[0].name +
                        "-" + String(searchState.single.batchFile.packages.length);
                }
                var name = searchState.single.batchFile.config.name;
                var file = JSON.stringify(batchState.convertToExternal(searchState.single.batchFile),
                    undefined, 2);

                $.post("uploadBatchFile", {name: name, file: file},
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
                  var json =
                      JSON.stringify(batchState.convertToExternal(searchState.multiple.batchFile),
                      undefined, 2);
                  var blob = new Blob([json], {type: "text/plain;charset=utf-8"});
                  saveAs(blob, searchState.multiple.batchFile.config.name);

                  // TODO: Check return code of saveAs() to determine if request was cancelled
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
                  var file = JSON.stringify(batchState.convertToExternal(searchState.multiple.batchFile),
                      undefined, 2);
                  $.post("uploadBatchFile", {name: name, file: file},
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
                      $.getJSON("search/repositories", data, processSearchResults).fail(processSearchResults);
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
                $.post("uploadBatchFile", {name: name, file: e.target.result},
                    uploadBatchFileCallback, "json").fail(uploadBatchFileCallback);
            };
        }
    },

    // List/Select member variables and methods
    showListSelectTable: false, // Draw list/select table
    fileList: [],               // Stores batch files found in list/select
    selectedBatchFile: {},
    listLocalBatchFiles: function(ev) {
        batchState.showBatchReportsTable = false;
        batchState.showListSelectTable = false;
        $.getJSON("listBatchFiles/local", { filter: $("#batchFileFilter").val() },
            listBatchFilesCallback).fail(listBatchFilesCallback);
    },
    listArchivedBatchFiles: function(ev) {
        batchState.showBatchReportsTable = false;
        batchState.showListSelectTable = false;
        $.getJSON("listBatchFiles/gsa", { filter: $("#batchFileFilter").val() },
            listBatchFilesCallback).fail(listBatchFilesCallback);
    },
    listAllBatchFiles: function(ev) {
        batchState.showBatchReportsTable = false;
        batchState.showListSelectTable = false;
        $.getJSON("listBatchFiles/all", { filter: $("#batchFileFilter").val() },
            listBatchFilesCallback).fail(listBatchFilesCallback);
    },

    // Batch reports member variables and methods
    showBatchReportsTable: false,
    currentBatchJobs: [],
    selectedBatchJob: {},

    // Details member variables and methods
    batchFile: {},                          // content of batch file.  All fields resolved
    javaType: "",                           // Initial value in config section
    loading: false,                         // parsing batch file.  Size is variable
    showBatchFile: false,                   // draw batch file detail table
    saveBatchFileName: "",                  // user input to save button for new batch file name
    backToBatchList: function(ev) {
        batchState.showBatchFile = false;
        batchState.showListSelectTable = true;
        batchState.batchFile = {};
    },
    saveBatch: function(ev) {
        batchState.saveBatchFileName = $("#saveBatchFileFilter").val();
        batchState.batchFile.config.name = batchState.saveBatchFileName;
        var file = JSON.stringify(batchState.batchFile, undefined, 2);
        $.post("uploadBatchFile", {name: batchState.saveBatchFileName, file: file},
               batchSaveCallback, "json").fail(uploadBatchFileCallback);
    },
    buildAndTestDetail: function(ev, el) {
        var el = $("#batchBuildServersFromDetails")[0];
        var buildServers = getSelectedValues(el);
        var javaType = "";

        config = batchState.batchFile.config;
        if (config['java'] === "IBM Java")
            javaType = "JAVA_HOME=/opt/ibm/java"

        packages = batchState.batchFile.packages;
        for (var i = 0; i < buildServers.length; i++) {
            for (var j = 0; j < packages.length; j++) {
                package = batchState.batchFile.packages[j];

                // Skip projects that can't be built like documentation
                build = package.build;
                if (build.selectedBuild === "")
                    continue;

                $.post("createJob", {id: package.id, tag: packages.tag, javaType: javaType,
                       node: buildServers[i], selectedBuild: build.selectedBuild,
                       selectedTest: build.selectedTest, selectedEnv: build.selectedEnv,
                       artifacts: build.artifacts, buildSystem: build.buildSystem, is_batch_job: true},
                       addToJenkinsCallback, "json").fail(addToJenkinsCallback);
            }
        }
    },
    selectJavaType: function(ev, el) {
        var selection = $(ev.target).text().toLowerCase();
        if (selection === "open jdk") {
            batchState.batchFile.config.java = "System default";
        }
        else if (selection === "ibm java") {
            batchState.batchFile.config.java = "IBM Java";
        }
    },
    updateEnviron: function(ev, el) {

    },
    resetEnviron: function(ev, el) {
        batchState.batchFile.config.java = batchState.javaType;
    },

    // Actions for individual batch files
    buildAndTest: function(ev, el) {
        var servers = document.getElementById('batchBuildServers'),
            options = servers.getElementsByTagName('option'),
            selectedServers = [];
            for (var i=options.length; i--;) {
                if (options[i].selected) selectedServers.push(options[i].value)
            }
        if (selectedServers.length == 0){
            $.post("runBatchFile", {batchName: batchState.selectedBatchFile.filename,
                node: undefined}, runBatchFileCallback, "json").fail(runBatchFileCallback);
        }
        else{
            for (var i = 0; i < selectedServers.length; i++){
                $.post("runBatchFile", {batchName: batchState.selectedBatchFile.filename,
                    node: selectedServers[i]}, runBatchFileCallback, "json").fail(runBatchFileCallback);
            }
        }
    },
    detail: function(ev, el) {
        batchState.loading = true;
        batchState.showBatchFile = false;
        $.getJSON("parseBatchFile",
            {
                batchName: batchState.selectedBatchFile.filename
            }, function(data){
                parseBatchFileCallback(data, batchState);
            }, "json").fail(function(data){
                parseBatchFileCallback(data, batchState);
            }
        );
    },
    showReport: function(ev, el) {
        batchState.showListSelectTable = false;
        $.post("getBatchResults", {batchName: batchState.selectedBatchFile.filename},
            getBatchResultsCallback, "json").fail(getBatchResultsCallback);
    },
    remove: function(ev, el) {
        $.post("removeBatchFile", {filename: batchState.selectedBatchFile.filename,
            location: batchState.selectedBatchFile.location},
            removeBatchFileCallback, "json").fail(removeBatchFileCallback);
        var index = batchState.fileList.indexOf(batchState.selectedBatchFile);
        if(index > -1) {
            batchState.fileList.splice(index, 1);
        }
        $('#batchListSelectTable').bootstrapTable('load', batchState.fileList);
    },
    archive: function(ev, el) {
        $.post("archiveBatchFile", {filename: batchState.selectedBatchFile.filename},
            archiveBatchFileCallback, "json").fail(archiveBatchFileCallback);
    },
    convertToExternal: function(internal) {
        var external = {};
        external["config"] = $.extend(true, {}, internal["config"]);
        external["packages"] = [];

        internal["packages"].forEach(function(entry) {
            var packagesElement = {};
            packagesElement["id"] = entry["id"];
            packagesElement["name"] = entry["owner"] + "/" + entry["name"];
            packagesElement["tag"] = entry["useVersion"];
            if (entry["build"])
            {
                packagesElement["build"] = {};
                packagesElement["build"]["artifacts"] = entry["build"]["artifacts"];
                packagesElement["build"]["selectedBuild"] = entry["build"]["selectedBuild"];
                packagesElement["build"]["selectedTest"] = entry["build"]["selectedTest"];
                packagesElement["build"]["selectedEnv"] = entry["build"]["selectedEnv"];
            }
            external["packages"].push(packagesElement);
        });

        return external;
    }
};

// Object for batch reporting
var batchReportState = {
    // member variables and methods
    showListSelectTable: false, // Allow batch table display
    fileList: [],               // Stores batch files found
    selectedBatchFile: {},
    testResultsPanel: false,
    batchReportFilter: "",
    showBatchReportsTable: false,
    currentBatchJobs: [],
    selectedBatchJob: {},
    batchReportTableReady: false,
    batchFile: {},                          // content of batch file.  All fields resolved
    javaType: "",                           // Initial value in config section
    loading: false,                         // parsing batch file.  Size is variable
    showBatchFile: false,                   // draw batch file detail table
    saveBatchFileName: "",                  // user input to save button for new batch file name
    listLocalBatch: function(ev) {
        // reset report state to initial state so that data reflected is correctly on fresh canvas.
        batchReportState.reset();
        batchReportState.showBatchReportsTable = false;
        batchReportState.showListSelectTable = false;
        // callback to render data to Batch Report table
        $.getJSON("listBatchReports/local", { filter: $("#batchReportFilter").val() },
            listBatchReportFilesCallback).fail(listBatchReportFilesCallback);
    },
    listGSABatch: function(ev) {
        // reset report state to initial state so that data reflected is correctly on fresh canvas.
        batchReportState.reset();
        batchReportState.showBatchReportsTable = false;
        batchReportState.showListSelectTable = false;
        // callback to render data to Batch Report table
        $.getJSON("listBatchReports/gsa", { filter: $("#batchReportFilter").val() },
            listBatchReportFilesCallback).fail(listBatchReportFilesCallback);
    },
    listAllBatch: function(ev) {
        // reset report state to initial state so that data reflected is correctly on fresh canvas.
        batchReportState.reset();
        batchReportState.showBatchReportsTable = false;
        batchReportState.showListSelectTable = false;
        // callback to render data to Batch Report table
        $.getJSON("listBatchReports/all", { filter: $("#batchReportFilter").val() },
            listBatchReportFilesCallback).fail(listBatchReportFilesCallback);
    },
    setTestResultsPanel: function(ev) {
        // Toggle show/hide batch report listing
        batchReportState.testResultsPanel = ! batchReportState.testResultsPanel;
    },
    backToBatchList: function(ev) {
        // For going back to displaying batch listing and hiding details.
        batchReportState.batchReportTableReady = false;
        batchReportState.showListSelectTable = true;
        batchReportState.batchFile = {};
    },
    history: function(){
        console.log("Batch History implementation is in progress");
    },
    compare: function(){
        console.log("Test Compare implementation is in progress");
    },
    reset: function(){
        // reset the Batch Report section to default values.
        batchReportState.showBatchReportsTable = false;
        batchReportState.showListSelectTable = false;
        batchReportState.fileList = [];
        batchReportState.selectedBatchFile = {};
        batchReportState.batchReportFilter = "";
        batchReportState.showBatchReportsTable = false;
        batchReportState.currentBatchJobs = [];
        batchReportState.selectedBatchJob = {};
        batchReportState.batchFile = {};
        batchReportState.javaType = "";
        batchReportState.loading = false;
        batchReportState.showBatchFile = false;
        batchReportState.saveBatchFileName = "";
    },
    detail: function(ev, el) {
        // fetch, render and display Report in table.
        batchReportState.loading = true;
        batchReportState.showBatchFile = false;

        // Get list of all selected batch test runs for fetchinf details.
        var selectedBatchJobs = $('#batchReportListSelectTable').bootstrapTable('getSelections');
        if (selectedBatchJobs.length > 0){
            var query = {};
            // Generate key-value pair with batch name and repository location, repository being the key of dictionary
            for (var i = 0; i < selectedBatchJobs.length; i ++) {
                if (query[selectedBatchJobs[i].repo] === undefined){
                    query[selectedBatchJobs[i].repo] = [];
                }
                query[selectedBatchJobs[i].repo].push(selectedBatchJobs[i].filename);
            }

            // fetch the Batch details and handle it appropriately.
            $.ajax({
                type: "POST",
                contentType: "application/json; charset=utf-8",
                url: "getBatchTestDetails",
                data: JSON.stringify({
                    batchList: query
                }),
                success: function(data){
                    processBatchDetails(data, batchReportState);
                },
                dataType:'json'
            }).fail(function(data){
                processBatchDetails(data, batchReportState);
            });
        }else{
            showMessage("Error: ", "At Least one Batch job needs to be selected.");
        }
    },
    archive: function(ev, el){
        console.log("Under development");
    },
    remove: function(ev, el) {
        // Will fire remove batch job test/build result.
        $.post("removeBatchFile", {filename: batchReportState.selectedBatchFile.filename,
            location: batchReportState.selectedBatchFile.location},
            removeBatchFileCallback, "json").fail(removeBatchFileCallback);
        var index = batchReportState.fileList.indexOf(batchReportState.selectedBatchFile);
        if(index > -1) {
            batchReportState.fileList.splice(index, 1);
        }
        $('#batchReportListSelectTable').bootstrapTable('load', batchReportState.fileList);
    },
    convertToExternal: function(internal) {
        var external = {};
        external["config"] = $.extend(true, {}, internal["config"]);
        external["packages"] = [];

        internal["packages"].forEach(function(entry) {
            var packagesElement = {};
            packagesElement["id"] = entry["id"];
            packagesElement["name"] = entry["owner"] + "/" + entry["name"];
            packagesElement["tag"] = entry["useVersion"];
            if (entry["build"])
            {
                packagesElement["build"] = {};
                packagesElement["build"]["artifacts"] = entry["build"]["artifacts"];
                packagesElement["build"]["selectedBuild"] = entry["build"]["selectedBuild"];
                packagesElement["build"]["selectedTest"] = entry["build"]["selectedTest"];
                packagesElement["build"]["selectedEnv"] = entry["build"]["selectedEnv"];
            }
            external["packages"].push(packagesElement);
        });

        return external;
    }
};
// batchReportState object ends

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
    javaType: "OpenJDK", // OpenJDK or IBM Java
    generateJavaType: "OpenJDK",
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
        if (selection === "openjdk") {
            detailState.javaType = "OpenJDK";
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
        if (selection === "openjdk") {
            detailState.generateJavaType = "OpenJDK";
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
    listLocalProjects: function(ev) {
        projectReportState.prjCompareReady = false;
        projectReportState.prjTableReady = false;

        projectReportState.compareType = "project";
        projectReportState.compareRepo = "local";
        $.getJSON("listTestResults/local", { filter: $("#projectFilter").val() }, processResultList).fail(processResultList);
        $("#resultArchiveBtn").show();
    },
    listGSAProjects: function(ev) {
        projectReportState.prjCompareReady = false;
        projectReportState.prjTableReady = false;

        projectReportState.compareType = "project";
        projectReportState.compareRepo = "archived";
        $.getJSON("listTestResults/gsa", { filter: $("#projectFilter").val() }, processResultList).fail(processResultList);
        $("#resultArchiveBtn").hide();
    },
    listAllProjects: function(ev) {
        projectReportState.prjCompareReady = false;
        projectReportState.prjTableReady = false;

        projectReportState.compareType = "project";
        projectReportState.compareRepo = "all";
        $.getJSON("listTestResults/all", { filter: $("#projectFilter").val() }, processResultList).fail(processResultList);
        $("#resultArchiveBtn").hide();
    },
    removeProjects: function(ev) {
        var selectedProjects = $('#testCompareSelectPanel').bootstrapTable('getSelections');
        var query = {};
        var sel = [];
        if (confirm("Remove selected project(s)?") != true) {
            return false;
        }
        for (var i = 0; i < selectedProjects.length; i ++) {
            sel[i] = selectedProjects[i].fullName;
            query[sel[i]] = selectedProjects[i].repository;
        }
        $.ajax({
            type: "POST",
            contentType: "application/json; charset=utf-8",
            url: "removeProjects",
            data: JSON.stringify({projects: query}),
            success: removeProjectResp,
            dataType:'json'
        }).fail(removeProjectResp);
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
    nodeUbuntu: [],
    nodeRHEL: [],
    nodeDetails: [],
    jenkinsPanel: false,
    jenkinsSlavePanel: false,
    manageSingleSlavePanel: false,
    manageMultipleSlavePanel: false,
    manageManagePanelFilter: false,
    uploadPackagePanel: false,
    showPackageTypeSelector: false,
    setJenkinsPanel: function(ev) {
        jenkinsState.jenkinsPanel = (jenkinsState.jenkinsPanel) ? false : true;
    },
    setJenkinsSlavePanel: function(ev) {
        jenkinsState.jenkinsSlavePanel = (jenkinsState.jenkinsSlavePanel) ? false : true;
    },
    setManageSingleSlavePanel: function(ev) {
        jenkinsState.manageSingleSlavePanel = (jenkinsState.manageSingleSlavePanel) ? false : true;
    },
    setManageMultipleSlavePanel: function(ev) {
        jenkinsState.manageMultipleSlavePanel = (jenkinsState.manageMultipleSlavePanel) ? false : true;
    },
    setUploadPackagePanel: function(ev) {
        jenkinsState.uploadPackagePanel = (jenkinsState.uploadPackagePanel) ? false : true;
    },
    buildServer: "",                        // The selected slave/ build server to perform a list package operation
    changeBuildServer: function () {
        jenkinsState.buildServer =  $("#singleJenkinsBuildServers").find(":selected").text();
        jenkinsState.singleSlavePackageTableReady = false; // hide the table if user changes the build server/slave selection
    },
    onPackageFileSelected: function() {
        if ($('#packageFile').val().indexOf('.tar') != -1
            || $('#packageFile').val().indexOf('.zip') != -1
            || $('#packageFile').val().indexOf('.bin') != -1) {
            jenkinsState.showPackageTypeSelector = true;
        } else {
            jenkinsState.showPackageTypeSelector = false;
        }
    },
    loadingState: {
        packageListLoading: false,
        packageActionLoading: false,
        managedPackageListLoading: false,
        managedPackageActionLoading: false,
        settingsLoading: false,
    },
    singleSlavePackageTableReady: false,    // Draw package table for single slave if true
    packageListSingleSlave: [],             // Package list retrieved for a Single Slave
    selectedSingleSlavePackage: {},         // Package selected by the user
    pkgInstallRemoveResponseCounter: 0,
    totalSelectedSingleSlavePkg: 0,
    pkgInstallRemoveStatusSingleSlave: [],
    listPackageForSingleSlave: function(ev) {
        jenkinsState.singleSlavePackageTableReady = false;
        jenkinsState.loadingState.packageListLoading = true;
        jenkinsState.selectedSingleSlavePackage = [];
        $("#singlePanelInstallBtn").addClass("disabled");
        $("#singlePanelRemoveBtn").addClass("disabled");
        $.getJSON("listPackageForSingleSlave",
        {
            packageFilter: $("#packageFilter_Single").val(),
            buildServer: jenkinsState.buildServer
        },
        listPackageForSingleSlaveCallback).fail(listPackageForSingleSlaveCallback);
    },
    // performActionOnSingleSlave Function performs install / remove action
    // on the packages selected in single panel
    // Argument:
    //    clickAction: takes values 'install/remove'
    performActionOnSingleSlave: function(clickAction) {
        var selectedPackageList = $('#singleServerPackageListTable').bootstrapTable('getSelections');
        if(selectedPackageList.length > 1 && clickAction == "install"){
            var tempPackArray = [];
            for(var obj of selectedPackageList){
                if(!obj.updateAvailable){
                    continue;
                }
                var isUpdatedToTemp = false;
                for(var tempObj of tempPackArray){
                    if((tempObj.packageName == obj.packageName) && compareVersion(tempObj.updateVersion, obj.updateVersion)){
                        tempObj['updateVersion'] = tempObj['updateVersion'];
                        isUpdatedToTemp = true;
                    }
                }
                if(!isUpdatedToTemp){
                    tempPackArray.push(obj);
                }
            }
            if(tempPackArray.length > 0){
                selectedPackageList = tempPackArray;
            }
            var message = "The below packages are eligible for Install/Update \n";
            for(var o of selectedPackageList){
               message = message+o.packageName + ", Version - "+o.updateVersion;
            }
            if(message != "") {
               var confRes = confirm(message);
               if(!confRes){
                   return false;
               }
            }
        }
        jenkinsState.pkgInstallRemoveResponseCounter = 0;
        jenkinsState.totalSelectedSingleSlavePkg = selectedPackageList.length;
        jenkinsState.pkgInstallRemoveStatusSingleSlave = [];
        var messageText = "Package cannot be installed or Removed";
        for (var selectedPkg in selectedPackageList ) {
            var  package_type = "", package_tagname = "";
            // Exclude packages not eligible for installation
            if (selectedPackageList[selectedPkg].updateAvailable == false && clickAction == 'install') {
                jenkinsState.pkgInstallRemoveStatusSingleSlave.push({
                    'packageName':selectedPackageList [selectedPkg].packageName,
                    'packageAction':'install',
                    'status': 'The package is already at the latest level!'
                    });
                jenkinsState.totalSelectedSingleSlavePkg -= 1;
                messageText = "The selected package(s) is/are already installed";
                continue;
            }
            // Exclude packages not eligible for removal
            if (selectedPackageList[selectedPkg].packageInstalled == false && clickAction == 'remove') {
                jenkinsState.pkgInstallRemoveStatusSingleSlave.push({
                    'packageName':selectedPackageList [selectedPkg].packageName,
                    'packageAction':'remove',
                    'status': 'The package is not installed and therefore cannot be removed!'
                    });
                jenkinsState.totalSelectedSingleSlavePkg -= 1;
                messageText = "The selected packages are not installed and therefore cannot be removed!";
                continue;
            }
            if (selectedPackageList [selectedPkg].packageType != undefined)
                package_type = selectedPackageList [selectedPkg].packageType;
            if (selectedPackageList [selectedPkg].package_tagname != undefined)
                package_tagname = selectedPackageList [selectedPkg].package_tagname;
            jenkinsState.loadingState.packageActionLoading = true;
            $.getJSON("managePackageForSingleSlave",
            {
                package_name: selectedPackageList [selectedPkg].packageName,
                package_version: selectedPackageList [selectedPkg].updateVersion,
                extension: selectedPackageList [selectedPkg].packageExt,
                action: clickAction,
                type: package_type,
                buildServer: jenkinsState.buildServer
            },
            managePackageForSingleSlaveCallback).fail(managePackageForSingleSlaveCallback);
        }
        // If no packages are eligible for intall / remove display the message
        if (jenkinsState.totalSelectedSingleSlavePkg == 0) {
            showAlert(messageText);
        }
    },
    installPackageForSingleSlave: function(ev) {
        jenkinsState.performActionOnSingleSlave('install');
    },
    removePackageForSingleSlave: function(ev) {
         jenkinsState.performActionOnSingleSlave('remove');
    },
    managedPackageTableReady: false,   // Draw managed package table if true
    managedPackageList: [],            // Managed Package list

    selectedMultiSlavePackage: [],     // Managed Packages selected by the user

    serverGroup: "",                   // Takes value All or UBUNTU or RHEL depending on the "List x" button clicked. Variable to be used during Synch operation.
    listManagedPackages: function(ev) {
        jenkinsState.managedPackageTableReady = false;
        jenkinsState.loadingState.managedPackageListLoading = true;
        jenkinsState.selectedMultiSlavePackage = [];
        var id = ev.target.id;
        jenkinsState.serverGroup = "All";
        $("#addToManagedList").addClass("disabled");
        $("#removeFromManagedList").addClass("disabled");
        buildServersToSync = [];
        if (id === "mlRHEL") {
            jenkinsState.serverGroup = "RHEL";
            buildServersToSync = jenkinsState.nodeRHEL;
        } else if (id === "mlUbuntu") {
            jenkinsState.serverGroup = "UBUNTU";
            buildServersToSync = jenkinsState.nodeUbuntu;
        } else {
            buildServersToSync = jenkinsState.nodeLabels;
        }
        buildServerJsonObj = [];
        for(var buildServObj of buildServersToSync){
            item = {}
            item ["value"] = buildServObj;
            item ["label"] = buildServObj;
            buildServerJsonObj.push(item);
        }
        $("#buildServersToSyncDropDown").multiselect('dataprovider', buildServerJsonObj);
        jenkinsState.manageManagePanelFilter = ($("#packageFilter_Multiple").val()!='')?true:false;
        $.getJSON("listManagedPackages", { distro: jenkinsState.serverGroup, package: $("#packageFilter_Multiple").val() },
            listManagedPackagesCallback).fail(listManagedPackagesCallback);
    },
    getSelectedManagedPackageData: function(type){
        var selectedPackageList = $('#multiServerPackageListTable').bootstrapTable('getSelections');
        if(selectedPackageList.length > 1 && type == "add"){
            var tempPackArray = [];
            for(var obj of selectedPackageList){
                var isUpdatedToTemp = false;
                for(var tempObj of tempPackArray){
                    if((tempObj.packageName == obj.packageName) && compareVersion(tempObj.updateVersion, obj.updateVersion)){
                            tempObj['updateVersion'] = tempObj['updateVersion'];
                    }
                }
                if(!isUpdatedToTemp){
                    tempPackArray.push(obj);
                }
            }
            if(tempPackArray.length > 0){
                selectedPackageList = tempPackArray;
            }
        }
        var packageListObj = [];
        var message = "";
        for(var obj in selectedPackageList){
            if(type=="Add" && selectedPackageList[obj].isAddable) {
                if(message=="")  message = "The below packages are eligible for "+type+"\n"
                message = message + selectedPackageList[obj].packageName+", version - "+selectedPackageList[obj].updateVersion+"\n";
            } else if(type == "Remove" && selectedPackageList[obj].isRemovable){
                if(message=="")  message = "The below packages are eligible for "+type+"\n"
                message = message + selectedPackageList[obj].packageName+", version - "+selectedPackageList[obj].installedVersion+"\n";
            } else {
                continue;
            }
            packageListObj.push({
                'package_name': selectedPackageList[obj].packageName,
                'package_version': selectedPackageList[obj].updateVersion,
                'extension': selectedPackageList[obj].packageExt,
                'distro': selectedPackageList[obj].distro,
                'arch': selectedPackageList[obj].arch,
                'removable': selectedPackageList[obj].removablePackage,
                'package_type': selectedPackageList[obj].packageType,
                'installed_version': selectedPackageList[obj].installedVersion,
                'installableExt': selectedPackageList[obj].installableExt,
                'removableExt': selectedPackageList[obj].removableExt
            });
        }
        if(message != "") {
            var confRes = confirm(message);
            if(!confRes){
                return "[]";
            }
        }
        return packageListObj;
    },
    addToManagedList: function(ev, el) {
        var packageListObj = JSON.stringify(jenkinsState.getSelectedManagedPackageData("Add"));
        if(packageListObj == "[]") {
            showAlert("No Package is eligible for Add");
            return false;
        }
        $.post("addToManagedList", { action: 'install', packageDataList: packageListObj}, editManagedListCallback, "json").fail(editManagedListCallback);
    },
    removeFromManagedList: function(ev, el) {
        var packageListObj = JSON.stringify(jenkinsState.getSelectedManagedPackageData("Remove"));
        if(packageListObj == "[]") {
            showAlert("No Package is eligible for Remove");
            return false;
        }
        $.post("removeFromManagedList",
        {
            action: 'remove',
            packageDataList: packageListObj
        },
        editManagedListCallback).fail(editManagedListCallback);
    },
    synchManagedPackageList: function() {
        var selectedBuildServer = $('#buildServersToSyncDropDown  option:selected');
        var selectedBuildServerCsv = "";
        $(selectedBuildServer).each(function(index, brand){
            if (selectedBuildServerCsv == "")
                selectedBuildServerCsv = $(this).val()
            else
                selectedBuildServerCsv =  selectedBuildServerCsv + ','  + $(this).val();
        });
        if (selectedBuildServerCsv == undefined || selectedBuildServerCsv == "") {
            showAlert("Please select build server");
            return false;
        }
        jenkinsState.loadingState.managedPackageActionLoading = true;
        $("#syncManagedPackageButton").addClass("disabled");
        $("#notifyManagedPanel").html("");
        $("#notifyManagedPanel").hide();
        $.getJSON("synchManagedPackageList", { serverNodeCSV: selectedBuildServerCsv }, synchManagedPackageListCallback).fail(synchManagedPackageListCallback);
    },
    uploadPackage: function (ev) {
        var file = $('#packageFile')[0].files[0];
        var packageType = $("#packageTypeOnPackageUpload").find(":selected").val();
        if(($('#packageFile').val().indexOf('.tar') != -1
            || $('#packageFile').val().indexOf('.zip') !=-1
            ||  $('#packageFile').val().indexOf('.bin') !=-1) &&
            (packageType == undefined || packageType == "")){
            alert("Please select Package Type");
            return false;
        }
        jenkinsState.loadingState.packageUploadLoading = true
        var formData = new FormData();
        formData.append('packageFile', file);
        formData.append('packageType',packageType);

                $.ajax({
                 url: "uploadToRepo",
                 type: 'POST',
                 data: formData,
                        async: true,
                success: uploadPackageCallback,
                        cache: false,
                contentType: false,
                        processData: false
                 }).fail(uploadPackageCallback);

            return false;
    },
    stateFormatter(value, row, index){
        var retVal=false;
        if(!row.enableCheckBox)
            retVal = true;
        return {
            disabled: retVal
        };
    }
};

var projectReportState = {
    prjCompareReady: false,
    compareRepo: "local",
    compareType: "project",
    projects: [],
    projectsTable: null,
    prjTableReady: false,
    testHistory: function() { // TODO single project or multiple?
        var selectedProjects = $('#testCompareSelectPanel').bootstrapTable('getSelections');
        var sel = [];
        var query = {};
        for (var i = 0; i < selectedProjects.length; i ++) {
            sel[i] = selectedProjects[i].fullName;
            query[sel[i]] = selectedProjects[i].repository;
        }
        //TODO - add loading bar
        projectReportState.prjCompareReady = false;
        projectReportState.prjTableReady = false;
        $.ajax({
                type: "POST",
         contentType: "application/json; charset=utf-8",
                 url: "getTestHistory",
                data: JSON.stringify({
                        projects: query
                      }),
             success: processTestHistory,
            dataType:'json'
        }).fail(processTestHistory);
    },
    testDetail: function() {
        var selectedProjects = $('#testCompareSelectPanel').bootstrapTable('getSelections');
        var sel = [];
        var query = {};
        for (var i = 0; i < selectedProjects.length; i ++) {
            sel[i] = selectedProjects[i].fullName;
            query[sel[i]] = selectedProjects[i].repository;
        }
        //TODO - add loading bar
        projectReportState.prjCompareReady = false;
        projectReportState.prjTableReady = false;
        $.ajax({
                type: "POST",
         contentType: "application/json; charset=utf-8",
                 url: "getTestDetail",
                data: JSON.stringify({
                        projects: query
                      }),
             success: processTestDetail,
            dataType:'json'
        }).fail(processTestDetail);
    },
    compareResults: function() {
        var selectedProjects = $('#testCompareSelectPanel').bootstrapTable('getSelections');
        var sel = [];
        for (var i = 0; i < selectedProjects.length; i++){
            sel[i] = selectedProjects[i].fullName;
        }
        if (sel.length === 2) {
            var leftProject = sel[0];
            var rightProject = sel[1];
            var leftRepo = selectedProjects[0].repository;
            var rightRepo = selectedProjects[1].repository;
            //TODO - add loading bar
            projectReportState.prjCompareReady = false;
            projectReportState.prjTableReady = false;
            $.getJSON("getTestResults",
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
    compareLogs: function(ev) {
        var logFile = "test_result.arti"
        var buttonID = $(ev.target).attr('id');
        if (buttonID === "compareBuildLogsBtn")
            logFile = "build_result.arti"
        var selectedProjects = $('#testCompareSelectPanel').bootstrapTable('getSelections');
        var sel = [];
        for (var i = 0; i < selectedProjects.length; i++){
            sel[i] = selectedProjects[i].fullName;
        }
        if (sel.length === 2) {
            var leftProject = sel[0];
            var rightProject = sel[1];
            var leftRepo = selectedProjects[0].repository;
            var rightRepo = selectedProjects[1].repository;
            //TODO - add loading bar
            projectReportState.prjCompareReady = false;
            projectReportState.prjTableReady = false;
            projectReportState.loadingState.diffLoading = true;
            $.getJSON("getDiffLogResults",
                      {
                        logfile: logFile,
                        leftbuild: leftProject,
                        rightbuild: rightProject,
                        leftrepository: leftRepo,
                        rightrepository: rightRepo
                      },
                      processLogCompareResults).fail(processLogCompareResults);
        }
        else {
            $('#resultCompareSelectionAlert').modal();
        }
    },
    archive: function() {
        var selectedProjects = $('#testCompareSelectPanel').bootstrapTable('getSelections');
        var sel = [];
        var query = {};
        for (var i = 0; i < selectedProjects.length; i ++) {
            sel[i] = selectedProjects[i].fullName;
            query[sel[i]] = selectedProjects[i].repository;
        }
        $.ajax({
                type: "POST",
         contentType: "application/json; charset=utf-8",
                 url: "archiveProjects",
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
    },
    loadingState: {
        diffLoading: false
    }
};

rivets.bind($('#toolContainer'), {
    globalState: globalState,
    reportState: reportState,
    projectReportState: projectReportState,
    searchState: searchState,
    batchState: batchState,
    batchReportState: batchReportState,
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
        $.getJSON("search", {
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

$('#packageFile').change(function () {
    $('#uploadPackageName').val("File selected: " + $('#packageFile').val());
});

function showAlert(message, data) {
    var text = "";
    $("#apErrorDialogText").hide();
    if (typeof data !== "undefined") {
        text += "<br/>" + (data.responseJSON !== undefined ?
                            (data.responseJSON.error !== undefined ?
                              data.responseJSON.error :
                              data.error) :
                            data.error);
        $("#apErrorDialogText").show();
    }
    $('#errorAlert').css("z-index","9999");
    $('#errorAlert').find('.modal-header').html(message);
    $("#apErrorDialogText").html(text);
    $("#errorAlert").modal();
}

function showMessage(header, message) {
    $("#apErrorDialogText").hide();
    if (typeof header !== "undefined" && typeof message !== "undefined") {
        header = '<span style="font-size: 22px; font-family: Caption; text-align: center;">' + header + '</span><br/>';
        message = '<span style="font-size: 16px; font-family: Arial;">' + message + '</span><br/>';
        $("#apErrorDialogText").show();
    }
    $('#errorAlert').css("z-index","9999");
    $('#errorAlert').find('.modal-header').html(header);
    $("#apErrorDialogText").html(message);
    $("#errorAlert").modal();
}

// Callback for when we receive data from a search query request
function processSearchResults(data) {
    if (data.status !== "ok") {
        if (searchState.multiple.loadingState.loading) {
            searchState.multiple.loadingState.loading = false;
        }
        showAlert("Bad response from /search!", data);
    } else if (data.type === "multiple") {

        // Got multiple results
        // Add select function to each result
        data.results.forEach(function(result) {
            // Show detail view for repo upon selection
            result.select = function (ev) {
                var className = $(ev.target).attr('class');
                if (className === "generateDetailButton btn btn-primary") {
                    $.getJSON("detail/" + result.id, {panel: "generate"}, showDetail).fail(showDetail);
                    searchState.multiple.ready = false;
                    searchState.multiple.loadingState.loading = true;
                }
                else if (className === "singleDetailButton btn btn-primary") {
                    $.getJSON("detail/" + result.id, {panel: "single"}, showDetail).fail(showDetail);
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

        $.getJSON("listTestResults", {}, processResultList).fail(processResultList);
        break;
      default:
        break;
    }
}

function processResultList(data) {
    projectReportState.selectedProjects = [];
    projectReportState.projects = [];
    $("#resultRemoveBtn").addClass("disabled");
    if (data === undefined || data.status != "ok") {
        showAlert("Error:", data);
    } else {
        projectReportState.projects = data.results;
        console.log("In processResultList, project list=", projectReportState.projects)
        detailState.autoSelected = false;
        projectReportState.prjCompareReady = true;
        $('#testCompareSelectPanel').bootstrapTable('load', projectReportState.projects);
    }
}

function removeProjectResp(data){
    if (data.status != "ok") {
        showAlert("Error:", data);
    }else{
        showAlert("Deleted Successfully !");
        if(projectReportState.compareRepo == "local"){
            reportState.listLocalProjects();
        }else if(projectReportState.compareRepo == "archived"){
            reportState.listGSAProjects();
        }else {
            reportState.listAllProjects();
        }
    }
}

function processBuildResults(data) {
    var tableContent = "";
    var difftableConent ="";

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

        $("#prjHeader").html(" " + data.leftProject.Package + " and " + data.rightProject.Package);

    }
    $("#testResultsTable").html(tableContent);
    projectReportState.prjTableReady = true;
}

function processLogCompareResults(data) {
    if (projectReportState.loadingState.diffLoading) {
        projectReportState.loadingState.diffLoading = false;
    }
    if (data.status != "ok") {
        showAlert("Error:", data);
    } else {
        var left = data.leftCol;
        var right = data.rightCol;
        var headerContent = "<table id=\"logdiffHeader\" >" +
                                 "<th style=\"border:none\">" +
                                      left['log'] + "<br />" +
                                      "[" + left['repo'] + "] " + left['job'] + "<br />" +
                                      left['pkgname'] + "-" + left['pkgver'] + "<br />" +
                                      left['distro'] +
                                 "</th>" +
                                 "<th style=\"border:none\">" +
                                      right['log'] + "<br />" +
                                      "[" + right['repo'] + "] " + right['job'] + "<br />" +
                                      right['pkgname'] + "-" + right['pkgver'] + "<br />" +
                                      right['distro'] +
                                 "</th>" +
                            "</table>";
        $("#logdiffHeader").html(headerContent);
        $("#leftdiff").html(data.results['diff'][left['diffName']]);
        $("#rightdiff").html(data.results['diff'][right['diffName']]);
        $('#logdiffModal').modal('show');
    }
    projectReportState.prjCompareReady = true;
}

function processTestDetail(data) {
    var headerContent = "";
    var tableContent = "";
    if (data.status != "ok") {
        showAlert("Error:", data);
    } else {
        // based on the compare table
        var i = 0;
        for (project in data.results) {

            // Header lists Jenkins Jobs.  Last character trimmed below
            if (++i < 8) {
                headerContent += " " + data.results[project].job + ",";
            }
            else if (i == 8) {
                headerContent += " ....";
            }

            tableContent += "<tr><th colspan=\"5\"><h3>"+
                "Test results for " + data.results[project].pkg + "-" +
                 data.results[project].ver +
                "</h3></th></tr>";
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
        headerContent = headerContent.slice(0, -1);
    }
    $("#prjHeader").html(headerContent);
    $("#testResultsTable").html(tableContent);
    projectReportState.prjTableReady = true;
}

// Batch Details population logic
function populate_batch_table_data(test_name, job_results){
    if (!job_results){
        console.log(job_results);
        return null;
    }
    var tr = document.createElement('tr');
    tr.setAttribute('class', 'testBatchResultsTableData');

    var total = job_results["total"] || 0;
    var errors = job_results["errors"] || 0;
    var failures = job_results["failures"] || 0;
    var skipped = job_results["skipped"] || 0;
    var data_array = ['', test_name, total, errors, failures, skipped];

    for (var i = 0; i < data_array.length; i++){
        var table_header_elem = document.createElement('td');
        var table_data_elem = document.createTextNode(data_array[i]);
        table_header_elem.appendChild(table_data_elem);
        tr.appendChild(table_header_elem);
    }
    return tr;
}

function populate_batch_table_headers(pkg_name, pkg_version){
    var tr = document.createElement('tr');
    tr.setAttribute('class', 'testBatchResultsTableHeader');
    var header_array = [pkg_name + " " + pkg_version, "Test", 'T', 'E', 'F', 'S'];

    for (var i = 0; i < header_array.length; i++){
        var table_header_elem = document.createElement('th');
        var table_data_elem = document.createTextNode(header_array[i]);
        table_header_elem.appendChild(table_data_elem);
        tr.appendChild(table_header_elem);
    }

    return tr;
}

/*
 * This function will be called to render Batch job report data.
*/
function processBatchDetails(data) {
    // If the response is not a success display error message and return.
    if (data.status != "ok") {
        showAlert("Error:", data);
    } else {
        // Hide listing of Batch jiobs before showing the batch details.
        batchReportState.showListSelectTable = false;
        // Initialize a new blank table holding Batch report data
        var main_table = document.getElementById("testBatchResultsTable");
        main_table.innerHTML = '';
        var data_table = document.createElement('table');
        data_table.setAttribute('border', '1');
        var blank_row = document.createElement('tr');
        var blank_cell = document.createElement('td');
        blank_cell.setAttribute('colspan', '6');
        var blank_text = document.createTextNode('');
        blank_cell.appendChild(blank_text);
        blank_row.appendChild(blank_cell);
        main_table.appendChild(blank_row);
        main_header_data = null;

        // Populate Batch details in table.
        for (var i in data.results) {
            if(main_header_data !== null){
                main_header_data += ', ' + data.results[i].job;
            }else{
                main_header_data = data.results[i].job;
            }

            data_table.appendChild(populate_batch_table_headers(data.results[i].pkg, data.results[i].ver));
            data_table.appendChild(populate_batch_table_data(data.results[i].pkg, data.results[i].results));
            var blank_text = document.createTextNode('');
            blank_cell.appendChild(blank_text);
            blank_row.appendChild(blank_cell);
            data_table.appendChild(blank_row);
        }

        // finally append the Batch details table to the placeholder table on UI.
        var tr = document.createElement('tr');
        tr.appendChild(data_table);
        main_table.appendChild(tr);

        $("#batchHeader").html(main_header_data); // Add code to generate headers data similar to existing logic for projecrts
        batchReportState.batchReportTableReady = true;
    }
}

function processTestHistory(data) {
    var tableContent = "";
    var headerContent = "";
    if (data.status != "ok") {
        showAlert("Error:", data);
    } else {
        var i = 0;
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

                // Header lists Jenkins Jobs.   Last charactered trimmed below
                if (++i < 8) {
                    headerContent += " " + data.results[project].results[dateRes].name + ",";
                }
                else if (i == 8) {
                    headerContent += " ....";
                }

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
        headerContent = headerContent.slice(0, -1);
    }
    $("#prjHeader").html(headerContent);
    $("#testResultsTable").html(tableContent);
    projectReportState.prjTableReady = true;
}

function archiveCallback(data) {
    if (data.status === "ok" ) {
        var errors = data.error;
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
    else {
        showAlert("Archive test results failed!", data);
    }
}

function getSelectedValues(select) {
    var result = [];
    var options = select && select.options;
    var opt;

    for(var i=0, iLen=options.length; i<iLen; i++) {
        opt = options[i];

        if (opt.selected) {
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

                for (var i=0; i < buildServers.length; i++) {
                    console.log(detailState.repo.useVersion + " version");
                    $.post("createJob", {id: detailState.repo.id, tag: detailState.repo.useVersion, javaType: detailState.javaTypeOptions, node: buildServers[i], selectedBuild: selectedBuild, selectedTest: selectedTest, selectedEnv: selectedEnv, artifacts: buildInfo.artifacts, buildSystem: buildInfo.buildSystem}, addToJenkinsCallback, "json").fail(addToJenkinsCallback);
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
                    $.post("createJob", {id: detailState.generateRepo.id, tag: detailState.generateRepo.useVersion, javaType: detailState.generateJavaTypeOptions, node: buildServers[i], selectedBuild: selectedBuild, selectedTest: selectedTest, selectedEnv: selectedEnv, artifacts: buildInfo.artifacts, buildSystem: buildInfo.buildSystem}, addToJenkinsCallback, "json").fail(addToJenkinsCallback);
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
    globalState.useTextAnalyticsInit = data.useTextAnalytics;
    globalState.logLevelInit = data.logLevel;

    globalState.jenkinsUrl = data.jenkinsUrl;
    globalState.localPathForTestResults = data.localPathForTestResults;
    globalState.pathForTestResults = data.pathForTestResults;
    globalState.localPathForBatchFiles = data.localPathForBatchFiles;
    globalState.pathForBatchFiles = data.pathForBatchFiles;
    globalState.githubToken = data.githubToken;
    globalState.configUsername = data.configUsername;
    globalState.configPassword = data.configPassword;
    globalState.useTextAnalytics = data.useTextAnalytics;
    globalState.logLevel = data.logLevel;

    if (data.gsaConnected !== undefined) {
       if (data.gsaConnected) {
           $('#gsaConnectionStatus').text("GSA connected");
           $('#gsaConnectionStatus').css("color","green");
       } else {
           $('#gsaConnectionStatus').text("GSA not connected");
           $('#gsaConnectionStatus').css("color","red");
       }
    }
}

function settingsCallback(data) {
    console.log("In settingsCallback data=", data);
    jenkinsState.loadingState.settingsLoading = false;
    if (data.status != "ok") {
        showAlert("Bad response from /settings!", data);
    } else {
        showAlert("Updated successfully");
    }
    if (data.gsaConnected !== undefined) {
       if (data.gsaConnected) {
           $('#gsaConnectionStatus').text("GSA connected");
           $('#gsaConnectionStatus').css("color","green");
       } else {
           $('#gsaConnectionStatus').text("GSA not connected");
           $('#gsaConnectionStatus').css("color","red");
       }
    }
}

function uploadBatchFileCallback(data) {
    console.log("In uploadBatchFileCallback");
    if (data.status !== "ok") {
        showAlert("", data);
    }
}

function uploadPackageCallback(data) {
    jenkinsState.loadingState.packageUploadLoading = false;
    $("#uploadPackageName").val('');
    jenkinsState.showPackageTypeSelector = false;
    $("#packageTypeOnPackageUpload option").multiselect("clearSelection");
    console.log("In uploadPackageCallback");
    if (data.status !== "ok") {
        showAlert("", data);
    }
    if (data.status == "ok") {
        showAlert("Uploaded Successfully !");
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

function batchSaveCallback(data) {
    console.log("In batchSaveCallback");
    if (data.status !== "ok") {
        showAlert("", data);
    } else {
        batchState.fileList.push(batchState.batchFile);
    }
}

function runBatchFileCallback(data) {
    console.log("In runBatchFileCallback");
    if (data.status !== "ok") {
        showAlert("", data);
    }
}

function getBatchResultsCallback(data) {
    console.log("In getBatchResultsCallback");
    batchState.currentBatchJobs = data.results;
    console.log(batchState.currentBatchJobs);
    batchState.showBatchReportsTable = true;
    $('#batchReportsTable').bootstrapTable('load', batchState.currentBatchJobs);
}

/*
 * This function parses the response from API call and prepares data for rendering onto UI
*/
function parseBatchFileCallback(data, batch_obj){
    batch_obj.loading = false;
    if (data.status === "ok") {
        // If data is retrieved successfuly continue preparations.
        // Get data and update batchReportState attributes.
        batch_obj.showListSelectTable = false;
        batch_obj.showBatchFile = true;
        batch_obj.batchFile = data.results;
        batch_obj.saveBatchFileName = data.results.config.name;
        batch_obj.javaType = data.results.config.java;
        // Defined the behaviour for moving packages up/down/remove if batchState object
        data.results.packages.forEach(function(package) {
            package.down = function (ev) {
                var i = data.results.packages.indexOf(package);
                if (i < data.results.packages.length - 1) {
                    var ele1 = data.results.packages[i];
                    var ele2 = data.results.packages[i+1];
                    data.results.packages.splice(i, 2, ele2, ele1);
                    batch_obj.batchFile.packages = data.results.packages;
                }
            };
            package.up = function (ev) {
                var i = data.results.packages.indexOf(package);
                if (i > 0) {
                    var ele1 = data.results.packages[i-1];
                    var ele2 = data.results.packages[i];
                    data.results.packages.splice(i-1, 2, ele2, ele1);
                    batch_obj.batchFile.packages = data.results.packages;
                }
            };
            package.remove = function (ev) {
                var i = data.results.packages.indexOf(package);
                var ele = data.results.packages.splice(i, 1);
                batch_obj.batchFile.packages = data.results.packages;
                if (data.results.packages.length === 0) {
                    batch_obj.showBatchFile = false;
                    batch_obj.showListSelectTable = true;
                }
            };
        });
    } else {
        showAlert("", data);
    }
}

function listBatchFilesCallback(data) {
    if (data.status === "ok") {
        batchState.fileList = data.results;
        console.log(batchState.fileList);
        batchState.showListSelectTable = true;

        $('#batchListSelectTable').bootstrapTable('load', batchState.fileList);
    } else {
        showAlert("Error!", data);
    }
}

function listBatchReportFilesCallback(data) {
    if (data.status === "ok") {
        console.log(data.results);
        batchReportState.fileList = data.results;
        batchReportState.showListSelectTable = true;

        $('#batchReportListSelectTable').bootstrapTable('load', batchReportState.fileList);
    } else {
        showAlert("Error!", data);
    }
}

function removeBatchFileCallback(data) {
    if (data.status === "failure") {
        showAlert("Error!", data);
    }
}

function archiveBatchFileCallback(data) {
    if (data.status === "failure") {
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
        for (i = 0; i < data.nodeLabels.length; i++) {
            var name = data.nodeNames[i];
            var label = data.nodeLabels[i];
            if ($.inArray(name, jenkinsState.nodeNames) === -1) {
                jenkinsState.nodeNames.push(data.nodeNames[i]);
            }
            if ($.inArray(label, jenkinsState.nodeLabels) === -1) {
                jenkinsState.nodeLabels.push(data.nodeLabels[i]);
            }
        }
        console.log("All nodes: ", jenkinsState.nodeLabels);
    }
    else {
        showAlert("Could not get Jenkins slaves", data);
    }
}

function getJenkinsNodeDetailsCallback(data) {
    console.log("In getJenkinsNodeDetailsCallback");
    if (data.status === "ok") {
        jenkinsState.nodeDetails = data.details;
        jenkinsState.nodeUbuntu = data.ubuntu;
        jenkinsState.nodeRHEL = data.rhel;
        console.log("Ubuntu nodes: ", jenkinsState.nodeUbuntu);
        console.log("RHEL nodes: ", jenkinsState.nodeRHEL);
        for (i = 0; i < jenkinsState.nodeDetails.length; i++) {
            console.log("Node details: ", jenkinsState.nodeDetails[i]);
        }
    }
    else {
        showAlert("Could not get Jenkins slaves", data);
    }
}

function listPackageForSingleSlaveCallback(data) {
    jenkinsState.loadingState.packageListLoading = false;
    if (data.status === "ok") {
        jenkinsState.packageListSingleSlave = data.packageData
        jenkinsState.singleSlavePackageTableReady = true;

        $('#singleServerPackageListTable').bootstrapTable('load', jenkinsState.packageListSingleSlave);
    } else {
        showAlert("Error!", data);
    }
}

function managePackageForSingleSlaveCallback(data) {
    jenkinsState.pkgInstallRemoveResponseCounter++;
    if (data.status === "ok") {
        jenkinsState.singleSlavePackageTableReady = false;
        jenkinsState.pkgInstallRemoveStatusSingleSlave.push({'packageName':data.packageName, 'packageAction':data.packageAction, 'status': data.buildStatus});
    } else {
        jenkinsState.pkgInstallRemoveStatusSingleSlave.push({'packageName':data.packageName, 'packageAction':data.packageAction, 'status': data.error});
    }
    if ( jenkinsState.pkgInstallRemoveResponseCounter == jenkinsState.totalSelectedSingleSlavePkg ) {
        jenkinsState.loadingState.packageActionLoading = false;
        var text = '<table class="table table-condensed">';
        text += '<tr class="active"><td>Package Name</td><td>Action</td><td>Status</td></tr>';
        if (jenkinsState.pkgInstallRemoveStatusSingleSlave.length>0) {
            var activeclass = "active";
            for(var i in jenkinsState.pkgInstallRemoveStatusSingleSlave) {
                if (jenkinsState.pkgInstallRemoveStatusSingleSlave[i].status == 'SUCCESS') {
                    activeclass = "success";
                }
                else if (jenkinsState.pkgInstallRemoveStatusSingleSlave[i].status == 'FAILURE') {
                    activeclass = "warning";
                }
                else if (jenkinsState.pkgInstallRemoveStatusSingleSlave[i].status != '') {
                    activeclass = "info";
                }
                text += '<tr class="' + activeclass + '">';
                text += '<td>' + jenkinsState.pkgInstallRemoveStatusSingleSlave[i].packageName + '</td>';
                text += '<td>' + jenkinsState.pkgInstallRemoveStatusSingleSlave[i].packageAction + '</td>';
                text += '<td>' + jenkinsState.pkgInstallRemoveStatusSingleSlave[i].status + '</td>';
                text += '</tr>';
            }
        }
        text += '</table>';
        showAlert(text);
    }
}

function listManagedPackagesCallback(data) {
    jenkinsState.loadingState.managedPackageListLoading = false;
    if (data.status === "ok") {
        jenkinsState.managedPackageList = data.packages;
        jenkinsState.managedPackageTableReady = true;
        $('#multiServerPackageListTable').bootstrapTable('load', jenkinsState.managedPackageList);
    } else {
        showAlert("Error!", data);
    }
}

function editManagedListCallback(data) {
    if (data.status === "ok") {
        showAlert("Success!");
        $("#multiServerPackageListTable").bootstrapTable('togglePagination').bootstrapTable('uncheckAll').bootstrapTable('togglePagination');
        $("#addToManagedList").addClass("disabled");
        $("#removeFromManagedList").addClass("disabled");
    }
}

// function pollingState: objects maintains the polling state
var pollingState =  function(){
   var dataJob = {};
   var pollCounter = 0;      // polling counter
   var timeInterval = 60000; // polling interval in milliseconds
   var pollAttempts = 20;    // # of polling attempts
   return {
       // function setData sets the data that needs to be passed to the server during polling
       setData: function(data) {
           dataJob = data;
       },
       // function poll: polls server using ajax
       poll: function() {
           console.log("polling....."+JSON.stringify(dataJob));
           if (pollCounter < pollAttempts) {
               if (dataJob.jobName != undefined) {
                   jenkinsState.loadingState.managedPackageActionLoading = true;
                   $("#syncManagedPackageButton").addClass("disabled");

                   $.getJSON("monitorJob", dataJob, notificationCallback(this)).fail(notificationCallback(this));
                   pollCounter++;
               }
           }
           else{
               $("#notifyManagedPanel").append("<br><span>Unable to fetch data from server.</span>");
               jenkinsState.loadingState.managedPackageActionLoading = false;
               $("#syncManagedPackageButton").removeClass("disabled");
           }
        },
        /* function socketPoll:  socket polling -  TODO:
        socketPoll: function() {
            //socket.emit('monitorJob event', {'jobName':dataJob.jobName,'nodeLabel':dataJob.nodeLabel});
        }*/
    };
};

function notificationCallback(obj){
    var title = "", message = "",type="", classcss="";

    return function(data) {
        if (data.jobstatus) {
            title =data.jobstatus;
            if (data.jobstatus == "SUCCESS") {
                message= "Sync completed on "+data.nodeLabel;
                type = "success";
                classcss = "text-success";
            }
            if (data.jobstatus == "FAILURE") {
                message= "Sync failed on "+data.nodeLabel;
                type = "danger";
                classcss = "text-warning";
            }
            $.notify({
                 title: "<strong>"+title+"</strong> ",
                 message: message
            },
            {
                type: type
            });
            $("#notifyManagedPanel").append("<br><span class='"+classcss+"'><strong>"+title+"</strong> "+message+"</span>");
            jenkinsState.loadingState.managedPackageActionLoading = false;
            $("#syncManagedPackageButton").removeClass("disabled");
        }
        else{
            jenkinsState.loadingState.managedPackageActionLoading = true;
            $("#syncManagedPackageButton").addClass("disabled");
            setTimeout(obj.poll(),obj.timeInterval);
        }

    };
}

function synchManagedPackageListCallback(data) {
    if (data.status === "ok") {
        showAlert(data.message);
        $("#notifyManagedPanel").show();
        $("#notifyManagedPanel").append("<br>"+data.message);
        //Client server polling
        if (data.jobList.length > 0){
            for (var i=0; i< data.jobList.length; i++) {
                console.log(data.jobList[i]);
                var dataJob = data.jobList[i];
                $("#notifyManagedPanel").append("<br>"+dataJob.install +" package(s) to be installed and "
                                               + dataJob.uninstalls + " package(s) to be uninstalled on "
                                               + dataJob.nodeLabel);
                var pollObj = new pollingState();
                pollObj.setData(dataJob);
                setTimeout(pollObj.poll(),5000);
            }
        }
    } else {
        showAlert("Error!", data);
    }
}

// Compares two versions
function compareVersion(version1,version2){
    var result=false;
    if(typeof version1!=='object'){ version1=version1.toString().split('.'); }
    if(typeof version2!=='object'){ version2=version2.toString().split('.'); }
    for(var i=0;i<(Math.max(version1.length,version2.length));i++){
        if(version1[i]==undefined){ version1[i]=0; }
        if(version2[i]==undefined){ version2[i]=0; }
        if(Number(version1[i])<Number(version2[i])){
            result=true;
            break;
        }
        if(version1[i]!=version2[i]){
            break;
        }
    }
    return(result);
}

function toggleBatchReportButtons(){
    var selectedProjects = $('#batchReportListSelectTable').bootstrapTable('getSelections');
    if (selectedProjects.length === 2) {
        $("#batch_report_compare").removeClass("disabled");
    } else {
        $("#batch_report_compare").addClass("disabled");
    }
}

$(document).ready(function() {
    // NOTE - rivets does not play well with multiselect
    // Query Jenkins for list of build servers
    // TODO: add selections for default (goes through jenkins master), linux distributions, specific build servers
    $.ajax({
        type: 'POST',
        url: "getJenkinsNodes",
        data: {},
        success: getJenkinsNodesCallback,
        dataType: "json",
        async:false
    });
    // TODO : Make this asynchronous as there may be a lot of build slaves.  Enhance autoport driver to use threads
    //        for parallelism but with a synchronous return wrt thread to aggregate data for caller
    $.ajax({
        type: 'POST',
        url: "getJenkinsNodeDetails",
        data: {},
        success: getJenkinsNodeDetailsCallback,
        dataType: "json",
        async:false
    });
    // Initialize bootstrap multiselect plugin
    // Config options go here
    $('#singleBuildServers').multiselect({
        buttonClass: "btn btn-primary",
        buttonText: function(options, select) {
            return "Select build server";
        }
    });
    $('#generateBuildServers').multiselect({
        buttonClass: "btn btn-primary",
        buttonText: function(options, select) {
            return "Select build server";
        }
    });
    $('#batchBuildServers').multiselect({
        buttonClass: "btn btn-primary",
        buttonText: function(options, select) {
            return "Build server";
        }
    });
    $('#batchBuildServersFromDetails').multiselect({
        buttonClass: "btn btn-primary",
        buttonText: function(options, select) {
            return "Build server";
        }
    });
    $('#singleJenkinsBuildServers').multiselect({
        buttonClass: "btn btn-primary",
        buttonText: function(options, select) {
            return "Build server";
        }
    });
    $('#packageTypeOnPackageUpload').multiselect({
        buttonClass: "btn btn-primary",
        buttonText: function(options, select) {
            return "Package Type";
        }
    });
    $('#buildServersToSyncDropDown').multiselect({
        buttonClass: "btn btn-primary",
        buttonText: function(options, select) {
            return "Build server";
        }
    });
    // Initializes an empty bach reports table
    $('#batchReportsTable').bootstrapTable({
        data: []
    });
    $('#batchReportsTable').on('check.bs.table', function (e, row) {
        batchState.selectedBatchJob = row;
    });
    // Initializes an empty batch list/select table
    $('#batchListSelectTable').bootstrapTable({
        data: []
    });
    $('#batchListSelectTable').on('check.bs.table', function (e, row) {
        batchState.selectedBatchFile = row;
    });
    // Initializes an empty batch Report list/select table
    $('#batchReportListSelectTable').bootstrapTable({
        data: []
    });
    $('#batchReportListSelectTable').on('check.bs.table', function (e, row) {
        batchReportState.selectedBatchFile = row;
    });
    // Initializes an empty package list table on the single slave panel
    $('#singleServerPackageListTable').bootstrapTable({
        data: []
    });
    $('#singleServerPackageListTable').on('check.bs.table', function (e, row) {
        jenkinsState.selectedSingleSlavePackage = row;
        var selectedPackages = $('#singleServerPackageListTable').bootstrapTable('getSelections');
        if(selectedPackages.length === 0) {
            $("#singlePanelInstallBtn").addClass("disabled");
            $("#singlePanelRemoveBtn").addClass("disabled");
            jenkinsState.selectedSingleSlavePackage = [];
        }
        else {
            $("#singlePanelInstallBtn").removeClass("disabled");
            $("#singlePanelRemoveBtn").removeClass("disabled");
        }
    });
    $('#singleServerPackageListTable').on('check-all.bs.table', function (e, row) {
        $("#singlePanelInstallBtn").removeClass("disabled");
        $("#singlePanelRemoveBtn").removeClass("disabled");
    });
    $('#singleServerPackageListTable').on('uncheck-all.bs.table', function (e, row) {
       var selectedPackages = $('#singleServerPackageListTable').bootstrapTable('getSelections');
        if(selectedPackages.length === 0) {
            $("#singlePanelInstallBtn").addClass("disabled");
            $("#singlePanelRemoveBtn").addClass("disabled");
        }
    });
    // Initializes an empty package list table on the Managed Slave panel
    $('#multiServerPackageListTable').bootstrapTable({
        data: []
    });
    $('#multiServerPackageListTable').on('check.bs.table', function (e, row) {
        $("#addToManagedList").removeClass("disabled");
        $("#removeFromManagedList").removeClass("disabled");
    });
    $('#multiServerPackageListTable').on('uncheck.bs.table', function (e, row) {
       var selectedPackages = $('#multiServerPackageListTable').bootstrapTable('getSelections');
        if (selectedPackages.length === 0) {
            $("#addToManagedList").addClass("disabled");
            $("#removeFromManagedList").addClass("disabled");
        }
    });
    $('#multiServerPackageListTable').on('check-all.bs.table', function (e, row) {
        $("#addToManagedList").removeClass("disabled");
        $("#removeFromManagedList").removeClass("disabled");
    });
    $('#multiServerPackageListTable').on('uncheck-all.bs.table', function (e, row) {
       var selectedPackages = $('#multiServerPackageListTable').bootstrapTable('getSelections');
        if(selectedPackages.length === 0) {
            $("#addToManagedList").addClass("disabled");
            $("#removeFromManagedList").addClass("disabled");
        }
    });


    //Initalize Project Results table
    $('#testCompareSelectPanel').bootstrapTable({
        data: []
    });
    $('#testCompareSelectPanel').on('check.bs.table', function (e, row) {
        projectReportState.projects = row;
    });

    //Handles display of project list buttons
    $('#testCompareSelectPanel').change(function() {
        var selectedProjects = $('#testCompareSelectPanel').bootstrapTable('getSelections');
        if (selectedProjects.length === 2) {
            $("#compareResultsBtn").removeClass("disabled");
            $("#compareBuildLogsBtn").removeClass("disabled");
            $("#compareTestLogsBtn").removeClass("disabled");
        } else {
            $("#compareResultsBtn").addClass("disabled");
            $("#compareBuildLogsBtn").addClass("disabled");
            $("#compareTestLogsBtn").addClass("disabled");
        }
        if (selectedProjects.length === 0) {
            $("#testHistoryBtn").addClass("disabled");
            $("#testDetailBtn").addClass("disabled");
            $("#resultArchiveBtn").addClass("disabled");
            $("#resultRemoveBtn").addClass("disabled");
        } else {
            $("#testHistoryBtn").removeClass("disabled");
            $("#testDetailBtn").removeClass("disabled");
            $("#resultArchiveBtn").removeClass("disabled");
            $("#resultRemoveBtn").removeClass("disabled");
        }
    });

    //Handles display of Batch Report list buttons
    $('#batchReportListSelectTable').change(function() {
        toggleBatchReportButtons();
    });

    $('#batchReportListSelectTable').show(function() {
        console.log("Showing reports");
        toggleBatchReportButtons();
    });
});
