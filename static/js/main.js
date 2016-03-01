try {
    google.load('search', '1');
}
catch(err) {
    console.log(err.message);
}

var globalState = {
    hasInit: false,
    cloudNodeInfo: [],

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
    isJenkinsTabActive: false,

    isHelpDisplayed: true,
    tempJenkinsUrl:"",
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
            globalState.isJenkinsTabActive = false;
        }
        else if (ev.target.id === "batchTab") {
            globalState.isSearchTabActive = false;
            globalState.isBatchTabActive = true;
            globalState.isReportsTabActive = false;
            globalState.isJenkinsTabActive = false;
        }
        else if (ev.target.id === "reportsTab") {
            globalState.isSearchTabActive = false;
            globalState.isBatchTabActive = false;
            globalState.isReportsTabActive = true;
            globalState.isJenkinsTabActive = false;
        }
        else if (ev.target.id === "jenkinsTab") {
            globalState.isSearchTabActive = false;
            globalState.isBatchTabActive = false;
            globalState.isReportsTabActive = false;
            globalState.isJenkinsTabActive = true;
        }
    },
    reset: function() {
        document.getElementById('ltest_results').value = globalState.localPathForTestResultsInit;
        document.getElementById('gtest_results').value = globalState.pathForTestResultsInit;
        document.getElementById('lbatch_files').value = globalState.localPathForBatchFilesInit;
        document.getElementById('gbatch_files').value = globalState.pathForBatchFilesInit;
        document.getElementById('github').value = globalState.githubTokenInit;
        document.getElementById('username').value = globalState.configUsernameInit;
        document.getElementById('password').value = globalState.configPasswordInit;
        globalState.useTextAnalytics = globalState.useTextAnalyticsInit;
        document.getElementById('loglevel').value = globalState.logLevelInit;
        globalState.tempJenkinsUrl = globalState.jenkinsUrl;
    },
    updateParameters: function () {
        jenkinsState.loadingState.settingsLoading = true;
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
               { ltest_results: localPathForTestResults, gtest_results: pathForTestResults,
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
                    java : "",
                    javascript : ""
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
                searchState.single.batchFile.config.includeTestCmds = "True";
                searchState.single.batchFile.config.includeInstallCmds = "False";
                searchState.single.batchFile.config.java = detailState.javaType;
                searchState.single.batchFile.config.javascript = detailState.javaScriptType;
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
                      java : "",
                      javascript : ""
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
                  searchState.multiple.batchFile.config.includeTestCmds = "True";
                  searchState.multiple.batchFile.config.includeInstallCmds = "False";
                  searchState.multiple.batchFile.config.java = detailState.JavaType;
                  searchState.multiple.batchFile.config.javascript = detailState.generateJavaScriptType;
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
                      if (searchState.multiple.query.limit == '' ||parseInt(searchState.multiple.query.limit) <= 0){
                         showAlert("Number of repository must be greater than 0.");
                         return false;
                      }
                      detailState.generateReady = false;
                      var data = {
                          // GitHub API parameters
                          q:       "stars:>" + searchState.multiple.query.stars +
                                   " forks:>" + searchState.multiple.query.forks +
                                   " fork:true" +
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
        searchState.single.batchFile.config.javascript = "";
        searchState.single.batchFile.packages = [];
        searchState.single.exportReady = false;
        searchState.single.ready = false;
    } else {
        searchState.multiple.batchFile.config.name = "";
        searchState.multiple.batchFile.config.owner = "";
        searchState.multiple.batchFile.config.java = "";
        searchState.single.batchFile.config.javascript = "";
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
    batchListingRepo: "",
    listLocalBatchFiles: function(ev) {
        batchState.loading = true;
        batchState.showBatchReportsTable = false;
        batchState.showListSelectTable = false;
        batchState.showBatchFile = false;
        batchState.selectedBatchFile = {};
        batchState.batchListingRepo = "local";
        $('#batch_file_archive').addClass('disabled');
        $('#batch_file_archive').show();
        $.getJSON("listBatchFiles/local", { filter: $("#batchFileFilter").val() },
            listBatchFilesCallback).fail(listBatchFilesCallback);
    },
    listArchivedBatchFiles: function(ev) {
        batchState.loading = true;
        batchState.showBatchReportsTable = false;
        batchState.showListSelectTable = false;
        batchState.selectedBatchFile = {};
        batchState.showBatchFile = false;
        batchState.batchListingRepo = "gsa";
        $('#batch_file_archive').addClass('disabled');
        $('#batch_file_archive').hide();
        $.getJSON("listBatchFiles/gsa", { filter: $("#batchFileFilter").val() },
            listBatchFilesCallback).fail(listBatchFilesCallback);
    },
    listAllBatchFiles: function(ev) {
        batchState.loading = true;
        batchState.showBatchReportsTable = false;
        batchState.showListSelectTable = false;
        batchState.showBatchFile = false;
        batchState.selectedBatchFile = {};
        batchState.batchListingRepo = "all";
        $('#batch_file_archive').addClass('disabled');
        $('#batch_file_archive').show();
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
    javaScriptType: "",                     // Initial value in config section
    includeTestCmds: true,                  // Initial value in config section
    includeInstallCmds: false,              // Initial value in config section
    loading: false,                         // parsing batch file.  Size is variable
    showBatchFile: false,                   // draw batch file detail table
    saveBatchFileName: "",                  // user input to save button for new batch file name
    backToBatchList: function(ev) {
        batchState.showBatchFile = false;
        batchState.showListSelectTable = true;
        batchState.batchFile = {};
    },
    saveBatch: function(ev) {
        var batchObj = $('#batchListSelectTable').bootstrapTable('getSelections')[0];
        batchState.saveBatchFileName = $("#saveBatchFileFilter").val();
        batchState.batchFile.config.name = batchState.saveBatchFileName;
        if (batchState.includeTestCmds) {
            batchState.batchFile.config.includeTestCmds = "True";
        } else {
            batchState.batchFile.config.includeTestCmds = "False";
        }
        if (batchState.includeInstallCmds) {
            batchState.batchFile.config.includeInstallCmds = "True";
        } else {
            batchState.batchFile.config.includeInstallCmds = "False";
        }
        console.log("In batchState.saveBatch, batchFile.config=", batchState.batchFile.config);
        for (var i=0; i<batchState.batchFile.packages.length; i++){
            if (batchState.batchFile.packages[i].build.userDefined != "True") {
                delete batchState.batchFile.packages[i].build;
            }
        }

        var file = JSON.stringify(batchState.convertToExternal(batchState.batchFile), undefined, 2);
        if (batchState.saveBatchFileName == batchObj.name) {
            $.post("updateBatchFile", {name: batchObj.filename, file: file, location: batchObj.location},function(data){
                batchSaveCallback(data,batchState), "json"}).fail(uploadBatchFileCallback);
        } else {
            $.post("uploadBatchFile", {name: batchState.saveBatchFileName, file: file},function(data){
                batchSaveCallback(data,batchState), "json"}).fail(uploadBatchFileCallback);
        }
    },
    selectNodeJsType: function(ev, el) {
        batchState.batchFile.config.javascript = $(ev.target).text();;
        console.log("selectNodeJsType: setting javascript=", batchState.batchFile.config.javascript)
    },
    selectJavaType: function(ev, el) {
        batchState.batchFile.config.java = $(ev.target).text();
        console.log("selectJavaType: setting java=", batchState.batchFile.config.java)
    },
    updateEnviron: function(ev, el) {
        $("#batchCommandsTableContanier").hide();
        $("#settingsBatchModal1").show();
        $('#showModifyButton').show();
        $("#batchBuildCommandBackButton").hide();
    },
    resetEnviron: function(ev, el) {
        batchState.batchFile.config.java = batchState.javaType;
        batchState.batchFile.config.javascript = batchState.javaScriptType;
        $('#batchSettingsTestCkBox').prop('checked', true);
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
    displayBatchCommandsTable:function(ev, el) {
         $("#batchCommandsTableContanier").show();
         $("#settingsBatchModal1").hide();
         $('#showModifyButton').hide();
         $("#batchBuildCommandBackButton").show();
    },
    onTestCheckBoxChanged: function(ev, el) {
        if($("#batchSettingsTestCkBox").is(":checked")){
            batchState.batchFile.config.includeTestCmds = "True";
        }else {
            batchState.batchFile.config.includeTestCmds = "False";
        }
    },
    onBatchSettingsOwnerChange:function(ev, el) {
        if($('#batchSettingsOwner').val() != ""){
            batchState.batchFile.config.owner = $('#batchSettingsOwner').val();
        }
    },
    displayBatchSettings: function(ev, el) {
         $("#batchCommandsTableContanier").hide();
         $("#settingsBatchModal1").show();
         $('#showModifyButton').show();
         $("#batchBuildCommandBackButton").hide();
    },

    // Actions for individual batch files
    buildAndTest: function(ev, el) {
        batchState.loading = true;
        var servers = document.getElementById('batchBuildServers'),
            options = servers.getElementsByTagName('option'),
            selectedServers = "";
            for (var i=options.length; i--;) {
                if (options[i].selected){
                   if(selectedServers == ""){
                       selectedServers = options[i].value;
                   }else{
                       selectedServers = selectedServers+","+options[i].value;
                   }
                }
            }
        if (selectedServers == ""){
            showAlert("Please select at least one build server!");
            batchState.loading = false;
            return false;
        }
        else{
            $.post("runBatchFile", {batchName: batchState.selectedBatchFile.filename,
                nodeCSV: selectedServers}, runBatchFileCallback, "json").fail(runBatchFileCallback);
        }
    },
    detail: function(ev, el) {
        if (batchState.selectedBatchFile.filename == undefined || batchState.selectedBatchFile.filename == ""){
            showAlert("Please select batch file");
            return false;
        }
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
    remove: function(ev, el) {
        if (confirm("Remove selected batch file(s)?") != true) {
            return false;
        }
        $.post("removeBatchFile", {filename: batchState.selectedBatchFile.filename,
               location: batchState.selectedBatchFile.location},
               removeBatchFileCallback, "json").fail(removeBatchFileCallback);
        var index = batchState.fileList.indexOf(batchState.selectedBatchFile);
        if (index > -1) {
            batchState.fileList.splice(index, 1);
        }
        $('#batchListSelectTable').bootstrapTable('load', batchState.fileList);
    },
    archive: function(ev, el) {
        if($('#batchListSelectTable').bootstrapTable('getSelections').length<1){
            showAlert("Please select one batch file to archive");
            return false;
        }
        batchState.loading = true;
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
            if (entry["useVersion"] != undefined) {              // Called from search/detail.  Input is repo
                packagesElement["tag"] = entry["useVersion"];
                packagesElement["name"] = entry["owner"] + "/" + entry["name"];
            } else {                                             // Called from batch.   Input is a batch File
                packagesElement["tag"] = entry["tag"];
                packagesElement["name"] = entry["name"];
            }
            if (entry["build"] && entry["build"]["userDefined"]) {
                packagesElement["build"] = {};
                packagesElement["build"]["artifacts"] = entry["build"]["artifacts"];
                packagesElement["build"]["selectedBuild"] = entry["build"]["selectedBuild"];
                packagesElement["build"]["selectedTest"] = entry["build"]["selectedTest"];
                packagesElement["build"]["selectedInstall"] = entry["build"]["selectedInstall"];
                packagesElement["build"]["selectedEnv"] = entry["build"]["selectedEnv"];
            }
            external["packages"].push(packagesElement);
        });

        return external;
    },
    updateIsUserDefined: function(evt, data){
        batchState.batchFile.packages[data.package.build.index].build.userDefined = "True";
    }
};

// Object for batch reporting
var batchReportState = {
    // member variables and methods
    prjCompareSingle: true,
    prjCompareReady: true,
    showListSelectTable: false, // Allow batch table display
    fileList: [], // Stores batch files found
    selectedBatchFile: {},
    testResultsPanel: false,
    batchReportFilter: "",
    showBatchReportsTable: false,
    currentBatchJobs: [],
    selectedBatchJob: {},
    batchReportTableReady: false,
    hasBuildLog: false,
    hasTestLog: false,
    batchReportLogRequested: false,
    batchFile: {},                          // content of batch file.  All fields resolved
    javaType: "",                           // Initial value in config section
    loading: false,                         // parsing batch file.  Size is variable
    showBatchFile: false,                   // draw batch file detail table
    saveBatchFileName: "",                  // user input to save button for new batch file name
    loading: false,
    listingRepo: "",
    comparison: false,
    listLocalBatch: function(ev) {
        // reset report state to initial state so that data reflected is correctly on fresh canvas.
        batchReportState.reset();
        batchReportState.showBatchReportsTable = false;
        batchReportState.showListSelectTable = false;
        batchReportState.loading = true;
        batchReportState.listingRepo = "local"
        // callback to render data to Batch Report table
        $.getJSON("listBatchReports/local", { filter: $("#batchReportFilter").val() },
            listBatchReportFilesCallback).fail(listBatchReportFilesCallback);
        $("#batch_report_archive").show();
    },
    listGSABatch: function(ev) {
        // reset report state to initial state so that data reflected is correctly on fresh canvas.
        batchReportState.reset();
        batchReportState.showBatchReportsTable = false;
        batchReportState.showListSelectTable = false;
        batchReportState.loading = true;
        batchReportState.listingRepo = "gsa"
        // callback to render data to Batch Report table
        $.getJSON("listBatchReports/gsa", { filter: $("#batchReportFilter").val() },
            listBatchReportFilesCallback).fail(listBatchReportFilesCallback);
        $("#batch_report_archive").hide();
    },
    listAllBatch: function(ev) {
        // reset report state to initial state so that data reflected is correctly on fresh canvas.
        batchReportState.reset();
        batchReportState.showBatchReportsTable = false;
        batchReportState.showListSelectTable = false;
        batchReportState.loading = true;
        batchReportState.listingRepo = "all"
        // callback to render data to Batch Report table
        $.getJSON("listBatchReports/all", { filter: $("#batchReportFilter").val() },
            listBatchReportFilesCallback).fail(listBatchReportFilesCallback);
        $("#batch_report_archive").show();
    },
    setTestResultsPanel: function(ev) {
        // Toggle show/hide batch report listing
        batchReportState.testResultsPanel = ! batchReportState.testResultsPanel;
    },
    backToBatchList: function(ev) {
        // For going back to displaying batch listing and hiding details.
        batchReportState.batchReportTableReady = false;
        batchReportState.showListSelectTable = true;
        batchReportState.hasBuildLog = false;
        batchReportState.hasTestLog = false;
        batchReportState.batchFile = {};
        batchReportState.batchReportLogRequested = false;
        batchReportState.loading = false;
        batchReportState.comparison = false;
    },
    backToBatchResultsCompare: function(ev) {
        if (batchReportState.comparison) {
            // For going back to displaying batch comparison and hiding details.
            batchReportState.batchReportTableReady = true;
            batchReportState.batchReportLogRequested = false;
        } else {
            batchReportState.backToBatchList(ev);
        }
        $('#testBatchLogResultsTable tr').remove();

        batchReportState.loading = false;
    },
    history: function() {
        batchReportState.loading = true;
        var selectedBatchJobs = $('#batchReportListSelectTable').bootstrapTable('getSelections');
        var notReadyJobList = [];
        if (selectedBatchJobs.length > 0){
            var query = {};
            for (var i = 0; i < selectedBatchJobs.length; i ++) {
                if (!checkIfBuildAndTestLogCreated()) {
                    notReadyJobList.push(selectedBatchJobs[i]);
                    continue;
                }
                if (query[selectedBatchJobs[i].repo] === undefined) {
                    query[selectedBatchJobs[i].repo] = [];
                }
                query[selectedBatchJobs[i].repo].push(selectedBatchJobs[i].filename);
            }

            if (selectedBatchJobs.length > notReadyJobList.length) {
                $.ajax({
                    type: "POST",
                    contentType: "application/json; charset=utf-8",
                    url: "getBatchTestDetails",
                    data: JSON.stringify({
                        batchList: query,
                        detailsType: 'history'
                    }),
                    success: function(data){
                        processBatchHistory(data, batchReportState);
                    },
                    dataType:'json'
                }).fail(function(data) {
                    processBatchHistory(data, batchReportState);
                });
            }
            else {
                showMessage("Info: ", "No build or test logs are presently available");
                batchReportState.loading = false;
            }
        }
        else {
              showMessage("Error: ", "At Least one Batch job needs to be selected.");
              batchReportState.loading = false;
        }
    },
    compareBatchBuildLog: function(){
        batchReportState.batchReportLogRequested = true;
        // fetch, render and display Report in table.
        batchReportState.loading = true;
        batchReportState.showBatchFile = false;
        batchReportState.batchReportTableReady = false;

        // Get list of all selected batch test runs for fetchinf details.
        var selectedBatchJobs = $('#batchReportListSelectTable').bootstrapTable('getSelections');
        if (selectedBatchJobs.length == 2 && !checkIfBuildAndTestLogCreated('build')) {
            showMessage("Info: ", "No build or test logs are presently available");
            batchReportState.loading = false;
            batchReportState.batchReportLogRequested = false;
        }
        else if (selectedBatchJobs.length == 2) {
            // fetch the Batch details and handle it appropriately.
            $.ajax({
                type: "POST",
                contentType: "application/json; charset=utf-8",
                url: "getDiffBatchLogResults",
                data: JSON.stringify({
                    leftbatch: selectedBatchJobs[0].filename,
                    rightbatch: selectedBatchJobs[1].filename,
                    leftrepo: selectedBatchJobs[0].repo,
                    rigthrepo: selectedBatchJobs[1].repo,
                    logfile: 'build_result.arti'
                }),
                success: function(data){
                    processBatchTestLogCompare(data, batchReportState, true);
                },
                dataType:'json'
            }).fail(function(data){
                processBatchTestLogCompare(data, batchReportState, true);
            });
        }
        else {
            showMessage("Error: ", "Two Batch job from the list needs to be selected.");
            batchReportState.loading = false;
            batchReportState.batchReportLogRequested = false;
        }
    },
    compareBatchTestLog: function(){
        batchReportState.batchReportLogRequested = true;
        // fetch, render and display Report in table.
        batchReportState.loading = true;
        batchReportState.showBatchFile = false;
        batchReportState.batchReportTableReady = false;

        // Get list of all selected batch test runs for fetchinf details.
        var selectedBatchJobs = $('#batchReportListSelectTable').bootstrapTable('getSelections');
        if (selectedBatchJobs.length == 2 && !checkIfBuildAndTestLogCreated('test')) {
            showMessage("Info: ", "No build or test logs are presently available");
            batchReportState.loading = false;
            batchReportState.batchReportLogRequested = false;
        }
        else if (selectedBatchJobs.length == 2) {
            // fetch the Batch details and handle it appropriately.
            $.ajax({
                type: "POST",
                contentType: "application/json; charset=utf-8",
                url: "getDiffBatchLogResults",
                data: JSON.stringify({
                    leftbatch: selectedBatchJobs[0].filename,
                    rightbatch: selectedBatchJobs[1].filename,
                    leftrepo: selectedBatchJobs[0].repo,
                    rigthrepo: selectedBatchJobs[1].repo,
                    logfile: 'test_result.arti'
                }),
                success: function(data){
                    processBatchTestLogCompare(data, batchReportState, false);
                },
                dataType:'json'
            }).fail(function(data){
                processBatchTestLogCompare(data, batchReportState, false);
            });
        }
        else {
            showMessage("Error: ", "Two Batch job from the list needs to be selected.");
            batchReportState.loading = false;
            batchReportState.batchReportLogRequested = false;
        }
    },
    compare: function(){
        // fetch, render and display Report in table.
        batchReportState.loading = true;
        batchReportState.comparison = true;
        batchReportState.showBatchFile = false;

        // Get list of all selected batch test runs for fetchinf details.
        var selectedBatchJobs = $('#batchReportListSelectTable').bootstrapTable('getSelections');
        if (selectedBatchJobs.length > 0 && !checkIfBuildAndTestLogCreated()) {
            showMessage("Info: ", "No build or test logs are presently available");
            batchReportState.loading = false;
        }
        else if (selectedBatchJobs.length == 2) {
            var query = {};
            // Generate key-value pair with batch name and repository location, repository being the key of dictionary
            for (var i = 0; i < selectedBatchJobs.length; i ++) {
                if (query[selectedBatchJobs[i].repo] === undefined){
                    query[selectedBatchJobs[i].repo] = [];
                }
                query[selectedBatchJobs[i].repo].push(selectedBatchJobs[i].filename);
                batchReportState.hasBuildLog = (selectedBatchJobs[i].build_log_count > 0)?true:false;
                batchReportState.hasTestLog = (selectedBatchJobs[i].test_log_count > 0)?true:false;
            }
            // fetch the Batch details and handle it appropriately.
            $.ajax({
                type: "POST",
                contentType: "application/json; charset=utf-8",
                url: "getBatchTestDetails",
                data: JSON.stringify({
                    batchList: query,
                    detailsType: 'compare'
                }),
                success: function(data){
                    processBatchCompare(data, batchReportState);
                },
                dataType:'json'
            }).fail(function(data){
                processBatchCompare(data, batchReportState);
            });
        }
        else {
            showMessage("Error: ", "Two Batch job from the list needs to be selected.");
            batchReportState.loading = false;
        }
    },
    compareLogs: function(ev,item) {
        var buttonID = ev.target.id;
        if(buttonID === "viewBatchBuildLogBtn")
             logFile = "build_result.arti"
        if(buttonID === "viewBatchTestLogBtn")
             logFile = "test_result.arti"

        var selectedBatchJobs = $('#batchReportListSelectTable').bootstrapTable('getSelections');
        var sel = [];
        var selectedIndex = 0;
        var selectedJobIndex = 0;
        batchReportState.modalHeader = "Log Results";
        $("#tree2 >li .active").removeClass("active");
        $(this).parent().addClass("active");
        $(this).addClass("active");
        for (var i = 0; i < selectedBatchJobs.length; i++){
              sel[i]={};
              selectedBatchJobs[i].logfile = logFile;
              for (var j=0;j<selectedBatchJobs[i].jobNames.length;j++){
                     sel[i][j] = selectedBatchJobs[i].jobNames[j];
                     if (item.batch && item.batchjobname ){
                        if (selectedBatchJobs[i].jobNames[j] == item.batchjobname) {
                            selectedIndex = i;
                            selectedJobIndex = j;
                            logFile = item.batch.logfile
                         }}
                 }
          }
        batchReportState.selectedBatchJobs = selectedBatchJobs;
        if (buttonID == "viewBatchBuildLogBtn" || buttonID == "viewBatchTestLogBtn")
              $('#tree2').treed();
        var leftProject = sel[selectedIndex][selectedJobIndex];
        var rightProject = sel[selectedIndex][selectedJobIndex];
        var leftRepo = selectedBatchJobs[selectedIndex].repo;
        var rightRepo = selectedBatchJobs[selectedIndex].repo;
        $.getJSON("getDiffLogResults",
                      {
                        logfile: logFile,
                        leftbuild: leftProject.replace(/\n/g, "").replace("/", ""),
                        rightbuild: rightProject.replace(/\n/g, "").replace("/", ""),
                        leftrepository: leftRepo,
                        rightrepository: rightRepo
                      },
                     processBatchBuildLogResults).fail(processBatchBuildLogResults);
    },
    reset: function() {
        // reset the Batch Report section to default values.
        batchReportState.backToBatchResultsCompare();
        batchReportState.backToBatchList();
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
        batchReportState.hasBuildLog = false;
        batchReportState.hasTestLog = false;
        batchReportState.saveBatchFileName = "";
        batchReportState.batchReportLogRequested = false;
        batchReportState.loading = false;
    },
    detail: function(ev, el) {
        // fetch, render and display Report in table.
        batchReportState.loading = true;
        batchReportState.showBatchFile = false;

        // Get list of all selected batch test runs for fetchinf details.
        var selectedBatchJobs = $('#batchReportListSelectTable').bootstrapTable('getSelections');
        if (!checkIfBuildAndTestLogCreated()) {
            showMessage("Info: ", "No build or test logs are presently available");
            batchReportState.loading = false;

        }
        else if (selectedBatchJobs.length > 0) {
            var query = {};
            var notReadyJobList = [];
            // Generate key-value pair with batch name and repository location, repository being the key of dictionary
            for (var i = 0; i < selectedBatchJobs.length; i ++) {
                if (!checkIfBuildAndTestLogCreated()){
                    notReadyJobList.push(selectedBatchJobs[i]);
                    continue;
                }
                if (query[selectedBatchJobs[i].repo] === undefined) {
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
                    batchList: query,
                    detailsType: 'details'
                }),
                success: function(data){
                    processBatchDetails(data, batchReportState);
                },
                dataType:'json'
            }).fail(function(data){
                processBatchDetails(data, batchReportState);
            });
        }
        else {
            showMessage("Error: ", "At Least one Batch job needs to be selected.");
            batchReportState.loading = false;
        }
    },
    archive: function(ev, el){
        var selectedBatchReports = $('#batchReportListSelectTable').bootstrapTable('getSelections');
        var sel = [];
        var query = {};
        for (var i = 0; i < selectedBatchReports.length; i ++) {
            if (selectedBatchReports[i].repo == 'local'){
                sel[i] = selectedBatchReports[i].filename;
                query[sel[i]] = selectedBatchReports[i].repo;
            }
        }
        batchReportState.loading = true;
        $.ajax({
            type: "POST",
            contentType: "application/json; charset=utf-8",
            url: "archiveBatchReports",
            data: JSON.stringify({
                      reports: query
            }),
            success: archiveBatchReportsCallback,
            dataType:'json'
        }).fail(archiveBatchReportsCallback);
    },
    remove: function(ev, el) {
        // Will fire remove batch job test/build result.
        $.post("removeBatchFile", {filename: batchReportState.selectedBatchFile.filename,
                location: batchReportState.selectedBatchFile.location},
                removeBatchFileCallback, "json").fail(removeBatchFileCallback);
        var index = batchReportState.fileList.indexOf(batchReportState.selectedBatchFile);
        if (index > -1) {
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
            if (entry["useVersion"] != undefined) {              // Called from search/detail.  Input is repo
                packagesElement["tag"] = entry["useVersion"];
                packagesElement["name"] = entry["owner"] + "/" + entry["name"];
            } else {                                             // Called from batch.   Input is a batch File
                packagesElement["tag"] = entry["tag"];
                packagesElement["name"] = entry["name"];
            }
            if (entry["build"] && entry["build"]["userDefined"]) {
                packagesElement["build"] = {};
                packagesElement["build"]["artifacts"] = entry["build"]["artifacts"];
                packagesElement["build"]["selectedBuild"] = entry["build"]["selectedBuild"];
                packagesElement["build"]["selectedTest"] = entry["build"]["selectedTest"];
                packagesElement["build"]["selectedInstall"] = entry["build"]["selectedInstall"];
                packagesElement["build"]["selectedEnv"] = entry["build"]["selectedEnv"];
            }
            external["packages"].push(packagesElement);
        });

        return external;
    },
    removeBatchReports: function(ev) {
        var selectedBatchResults = $('#batchReportListSelectTable').bootstrapTable('getSelections');
        var query = {};
        var sel = [];
        if (confirm("Remove selected batch report(s)?") != true) {
            return false;
        }
        batchReportState.loading = false;
        for (var i = 0; i < selectedBatchResults.length; i ++) {
            sel[i] = selectedBatchResults[i].filename;
            query[sel[i]] = selectedBatchResults[i].repo;
        }
        $.ajax({
            type: "POST",
            contentType: "application/json; charset=utf-8",
            url: "removeBatchReports",
            data: JSON.stringify({reports: query}),
            success: removeBatchReportsCallback,
            dataType:'json'
        }).fail(removeBatchReportsCallback);
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
    pie: null,                                      // Pie chart
    generatePie: null,
    supportedJavaList: [],
    supportedJavaListOptions: [],
    supportedJavaScriptList: [],
    supportedJavaScriptListOptions: [],
    //TODO - split single and generate out, this repetition is bad.  Pertains to two detail menus
    javaType: "openjdk 7",                            // OpenJDK or IBM Java
    javaTypeOptions: "",
    generateJavaScriptType: "nodejs",
    javaScriptType: "nodejs",                       // nodejs or IBM SDK for Node.js
    javaScriptTypeOptions: "",
    generateJavaScriptTypeOptions: "",
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
        detailState.javaType = $(ev.target).text();
        if ((selection.indexOf('java') > -1 && selection.indexOf('sdk') > -1)) {// asuming this naming convention for IBM Java.
            detailState.javaTypeOptions = "/etc/profile.d/ibm-java.sh";
        } else if (selection.indexOf('jdk') > -1) { // asuming this naming convention for openjdk.
            detailState.javaTypeOptions = "";
        }
    },
    // When the radio button is pressed update the server environment data
    selectJavaScriptType: function(ev) {
        var selection = $(ev.target).text().toLowerCase();
        detailState.javaScriptType = $(ev.target).text();
        detailState.javaScriptTypeOptions = '';
    },
    selectGenerateJavaScriptType: function(ev) {
        var selection = $(ev.target).text().toLowerCase();
        detailState.generateJavaScriptType = $(ev.target).text();
        detailState.generateJavaScriptTypeOptions = '';
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
        projectReportState.loadingState.diffLoading = true;
        $.getJSON("listTestResults/local", { filter: $("#projectFilter").val() }, processResultList).fail(processResultList);
        $("#resultArchiveBtn").show();
    },
    listGSAProjects: function(ev) {
        projectReportState.prjCompareReady = false;
        projectReportState.prjTableReady = false;

        projectReportState.compareType = "project";
        projectReportState.compareRepo = "archived";
        projectReportState.loadingState.diffLoading = true;
        $.getJSON("listTestResults/gsa", { filter: $("#projectFilter").val() }, processResultList).fail(processResultList);
        $("#resultArchiveBtn").hide();
    },
    listAllProjects: function(ev) {
        projectReportState.prjCompareReady = false;
        projectReportState.prjTableReady = false;

        projectReportState.compareType = "project";
        projectReportState.compareRepo = "all";
        projectReportState.loadingState.diffLoading = true;
        $.getJSON("listTestResults/all", { filter: $("#projectFilter").val() }, processResultList).fail(processResultList);
        $("#resultArchiveBtn").show();
    },
    removeProjects: function(ev) {
        var selectedProjects = $('#testCompareSelectPanel').bootstrapTable('getSelections');
        var query = {};
        var sel = [];
        if (confirm("Remove selected project(s)?") != true) {
            return false;
        }
        projectReportState.loadingState.diffLoading = true;
        for (var i = 0; i < selectedProjects.length; i ++) {
            sel[i] = selectedProjects[i].fullName;
            query[sel[i]] = selectedProjects[i].repository;
        }
        $.ajax({
            type: "POST",
            contentType: "application/json; charset=utf-8",
            url: "removeProjects",
            data: JSON.stringify({projects: query}),
            success: removeProjectsCallback,
            dataType:'json'
        }).fail(removeProjectsCallback);
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
    nodeCentOS: [],
    nodeDetails: [],
    nodeOSes: [],
    jenkinsPanel: false,
    jenkinsSlavePanel: false,
    manageSingleSlavePanel: false,
    manageMultipleSlavePanel: false,
    manageManageRebootSlave: false,
    manageManagePanelFilter: false,
    uploadPackagePanel: false,
    showPackageTypeSelector: false,
    showDebSelector: false,
    showRpmSelector: false,
    reBuildSlave: false,
    resizeModalDialog: false,
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
    setManageRebootSlave: function(ev) {
        jenkinsState.manageManageRebootSlave = (jenkinsState.manageManageRebootSlave) ? false : true;
        if (jenkinsState.manageManageRebootSlave) {
            //var nodeDetails = jenkinsState.nodeDetails;
            for (var i=0; i<jenkinsState.nodeDetails.length; i++){
                jenkinsState.nodeDetails[i]['os'] = jenkinsState.nodeDetails[i]['distro'] + ' ' +
                                                    jenkinsState.nodeDetails[i]['rel']    + ' ' +
                                                    jenkinsState.nodeDetails[i]['arch'];
                var displayName = jenkinsState.nodeNames[i]
                jenkinsState.nodeDetails[i]['jenkinsSlaveLink'] =
                    '<a target="_blank" href="' + globalState.jenkinsUrl + '/computer/' + displayName +'/">Click here</a>';
            }
            $("#rebootServerListTable").bootstrapTable('load', jenkinsState.nodeDetails);
        }
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
            jenkinsState.showDebSelector = false
            jenkinsState.showRpmSelector = false;
        } else if ($('#packageFile').val().indexOf('.deb') != -1){
            jenkinsState.showDebSelector = true;
            jenkinsState.showPackageTypeSelector = false;
            jenkinsState.showRpmSelector = false;
        } else if ($('#packageFile').val().indexOf('.rpm') != -1){
            jenkinsState.showRpmSelector = true;
            jenkinsState.showDebSelector = false;
            jenkinsState.showPackageTypeSelector = false;
        }
    },
    clearPackage: function(){
        $("#debSelector").multiselect("clearSelection");
        $("#debSelector").multiselect('refresh');
        $("#rpmSelector").multiselect("clearSelection");
        $("#rpmSelector").multiselect('refresh');
        $("#packageTypeOnPackageUpload").multiselect("clearSelection");
        $("#packageTypeOnPackageUpload").multiselect('refresh');
        jenkinsState.showPackageTypeSelector = false;
        jenkinsState.showDebSelector = false
        jenkinsState.showRpmSelector = false;
        $("#packageFile").val('');
        $("#uploadPackageName").val('');
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
        if (jenkinsState.buildServer == undefined || jenkinsState.buildServer == "") {
            showAlert("Please select a Build Server");
            return false;
        }
        jenkinsState.singleSlavePackageTableReady = false;
        jenkinsState.loadingState.packageListLoading = true;
        jenkinsState.selectedSingleSlavePackage = [];
        $("#singleSlaveListBtn").addClass("disabled");
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
        if (selectedPackageList.length > 1 && clickAction == "install") {
            var tempPackArray = [];
            for (var i in selectedPackageList) {
                var obj = selectedPackageList[i];
                if (!obj.updateAvailable){
                    continue;
                }
                var isUpdatedToTemp = false;
                for (var j in tempPackArray) {
                    var tempObj = tempPackArray[j];
                    if((tempObj.packageName == obj.packageName) && compareVersion(tempObj.updateVersion, obj.updateVersion)){
                        tempObj['updateVersion'] = tempObj['updateVersion'];
                        isUpdatedToTemp = true;
                    }
                }
                if (!isUpdatedToTemp) {
                    tempPackArray.push(obj);
                }
            }
            if (tempPackArray.length > 0) {
                selectedPackageList = tempPackArray;
            }
            var message = "The below packages are eligible for Install/Update \n";
            for (var k in selectedPackageList) {
                var o = selectedPackageList[k];
                message = message+o.packageName + ", Version - "+o.updateVersion;
            }
            if (message != "") {
               var confRes = confirm(message);
               if (!confRes) {
                   return false;
               }
            }
        }
        jenkinsState.pkgInstallRemoveResponseCounter = 0;
        jenkinsState.totalSelectedSingleSlavePkg = selectedPackageList.length;
        jenkinsState.pkgInstallRemoveStatusSingleSlave = [];
        var messageText = "Package cannot be installed or Removed";
        var responseCounter = 0;
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
            jenkinsState.singleSlavePackageTableReady = false;
            $.getJSON("managePackageForSingleSlave",
            {
                package_name: selectedPackageList [selectedPkg].packageName,
                package_version: selectedPackageList [selectedPkg].updateVersion,
                extension: selectedPackageList [selectedPkg].packageExt,
                action: clickAction,
                type: package_type,
                buildServer: jenkinsState.buildServer
            },
            function(data){
                managePackageForSingleSlaveCallback(data, selectedPackageList [responseCounter].packageName, clickAction);
                responseCounter++;
            }).fail(function(data){
                managePackageForSingleSlaveCallback(data, selectedPackageList [responseCounter].packageName, clickAction);
                responseCounter++;
            });
        }
        // If no packages are eligible for install / remove display the message
        if (jenkinsState.totalSelectedSingleSlavePkg == 0) {
            showAlert(messageText);
        }
    },
    installPackageForSingleSlave: function(ev) {
        jenkinsState.performActionOnSingleSlave('install');
        jenkinsState.resizeModalDialog = true;
    },
    removePackageForSingleSlave: function(ev) {
         jenkinsState.performActionOnSingleSlave('remove');
         jenkinsState.resizeModalDialog = true;
    },
    rebuildSync: function(ev) {
        console.log("rebootSync: Inside rebootSync");
        var selectedBuildServer = $('#rebootServerListTable').bootstrapTable('getSelections');
        var selectedBuildServerCsv = "";
        jenkinsState.reBuildSlave = true;
        $(selectedBuildServer).each(function(index, brand){
            selectedBuildServerCsv = $(this)[0].nodelabel;
            var nodeindex = jenkinsState.nodeLabels.indexOf($(this)[0].nodelabel);
            jenkinsState.nodeDetails[nodeindex]['status'] = "<span class='glyphicon glyphicon-refresh glyphicon-refresh-animate'></span><span class='text-danger'>Disconnected</span>";
            $("#rebootServerListTable").bootstrapTable('load', jenkinsState.nodeDetails);

            var syncPackages = function() {
             console.log("Start syncing..",  jenkinsState.nodeDetails[nodeindex].nodelabel);
             jenkinsState.nodeDetails[nodeindex]['status'] = "<span class='glyphicon glyphicon-refresh glyphicon-refresh-animate'></span><span class='text-warning'>Syncing</span>";
             $("#rebootServerListTable").bootstrapTable('load', jenkinsState.nodeDetails);

             $.ajax({
                     url:"synchManagedPackageList",
                     type: 'get',
                     data: {
                               serverNodeCSV: jenkinsState.nodeDetails[nodeindex].nodelabel
                           },
                     success: function(data) {
                                if (data.status === "ok") {
                                    var pollObj = new pollingState();
                                    if (data.jobList.length > 0){
                                        for (var i=0; i< data.jobList.length; i++) {
                                            var dataJob = data.jobList[i];
                                            pollObj.setData(dataJob);
                                            // Poll for sync status
                                            setTimeout(
                                                pollObj.poll(
                                                    function() {
                                                        jenkinsState.reBuildSlave = false;
                                                        jenkinsState.nodeDetails[nodeindex]['status'] =
                                                            "<span class='text-success'>Connected</span>";
                                                        $("#rebootServerListTable").bootstrapTable('load', jenkinsState.nodeDetails);
                                                }),
                                                5000);
                                        }
                                    }
                                } else {
                                    showAlert("Error!", data);
                                }
                            },
                     error: function() {
                              jenkinsState.reBuildSlave = false;
                              jenkinsState.nodeDetails[nodeindex]['status'] = "<span class='text-success'>Connected</span>";
                            }
                     });
            };
            var buttonID = $(ev.target).attr('id');
            if( buttonID == "reSync") {
                console.log("Sync only");
                syncPackages();
            }
            else
            {
                // Rebuild each slave
                $.getJSON("rebuildSlave", { serverNodeCSV: selectedBuildServerCsv, rebuildFlag : 1}, function(data){
                    if (data.status === "ok") {
                        // On completion of Rebuild, Sync Managed packages on the newly built slave..
                        // so that build slave is at the latest Managed version
                        if (data.rebuildStatus == 'ERROR'){
                             console.log("Rubuild entered ERROR state. Hence exiting!");
                             jenkinsState.nodeDetails[nodeindex]['status'] = "<span class='text-danger'>ERROR</span>";
                             $("#rebootServerListTable").bootstrapTable('load', jenkinsState.nodeDetails);
                             jenkinsState.reBuildSlave = false;
                             return false;
                        }
                        if (data.rebuildStatus == 'ACTIVE'){
                             setTimeout(syncPackages(), 20000);
                        }
                        if (data.rebuildStatus != 'ACTIVE'){
                            console.log("Slave has not come online. Keep polling for ACTIVE Status");
                            jenkinsState.nodeDetails[nodeindex]['status'] =
                                "<span class='glyphicon glyphicon-refresh glyphicon-refresh-animate'></span>"
                                "<span class='text-success'>Building</span>";
                            $("#rebootServerListTable").bootstrapTable('load', jenkinsState.nodeDetails);
                            var pollObjRebuild = new pollingState();
                            pollObjRebuild.setData({
                                                    serverNodeCSV: jenkinsState.nodeDetails[nodeindex].nodelabel,
                                                    rebuildFlag : 0
                                                   });
                            var checkRebuildStatus = function()
                            {
                                pollObjRebuild.poll(
                                    function(data) {
                                        if (data.status === "ok") {
                                            if (data.rebuildStatus == 'ACTIVE') {
                                                jenkinsState.nodeDetails[nodeindex]['status'] = "<span class='text-success'>Connected</span>";
                                                $("#rebootServerListTable").bootstrapTable('load', jenkinsState.nodeDetails);
                                                setTimeout(syncPackages(), 20000);
                                                return true;
                                            }
                                            else {
                                                checkRebuildStatus();
                                            }
                                        }
                                   });
                           };
                           checkRebuildStatus();
                        }
                    }
                },nodeindex)
                .fail(function(data){});
                }
        });
        if (selectedBuildServerCsv == undefined || selectedBuildServerCsv == "") {
            showAlert("Please select build server!");
            jenkinsState.reBuildSlave = false;
            return false;
        }
    },
    managedPackageTableReady: false,   // Draw managed package table if true
    managedPackageList: [],            // Managed Package list

    selectedMultiSlavePackage: [],     // Managed Packages selected by the user

    serverGroup: "",                   // Variable to be used during Synch operation.
    listManagedPackages: function(ev) {
        var id = $("#buildServersOSes").find(":selected").text();
        jenkinsState.selectedMultiSlavePackage = [];
        jenkinsState.serverGroup = "All";
        jenkinsState.managedPackageTableReady = false;
        $("#addToManagedList").addClass("disabled");
        $("#removeFromManagedList").addClass("disabled");
        buildServersToSync = [];
        if (id == undefined || id == "") {
           showAlert("Please select distribution");
           return false;
        }
        if (id === "RHEL") {
            jenkinsState.serverGroup = "RHEL";
            buildServersToSync = jenkinsState.nodeRHEL;
        } else if (id === "Ubuntu") {
            jenkinsState.serverGroup = "UBUNTU";
            buildServersToSync = jenkinsState.nodeUbuntu;
        } else if (id === "CentOS") {
            jenkinsState.serverGroup = "CentOS";
            buildServersToSync = jenkinsState.nodeCentOS;
        } else {
            jenkinsState.serverGroup = "All";
            buildServersToSync = jenkinsState.nodeLabels;
        }
        $("#managedListBtn").addClass("disabled");
        jenkinsState.managedPackageTableReady = false;
        $("#addToManagedList").addClass("disabled");
        $("#removeFromManagedList").addClass("disabled");
        jenkinsState.loadingState.managedPackageListLoading = true;
        buildServerJsonObj = [];
        for (var i = 0; i<buildServersToSync.length;i++) {
            var buildServObj = buildServersToSync[i];
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
         if(selectedPackageList.length > 0 && type.toLowerCase() == "add"){
            var tempPackArray = [];
            for (var i in selectedPackageList){
                var obj = selectedPackageList[i];
                var isUpdatedToTemp = false;
                for (var k in tempPackArray){
                    var tempObj = tempPackArray[k];
                    if ((tempObj.packageName == obj.packageName) && compareVersion(tempObj.updateVersion, obj.updateVersion)) {
                            tempObj['updateVersion'] = tempObj['updateVersion'];
                    }
                }
                if (!isUpdatedToTemp) {
                    tempPackArray.push(obj);
                }
            }
            if (tempPackArray.length > 0) {
                selectedPackageList = tempPackArray;
            }
        }
        var packageListObj = [];
        var message = "";
        for (var obj in selectedPackageList){
            if (type == "Add" && selectedPackageList[obj].isAddable) {
                if (message == "")  message = "The below packages are eligible for "+type+"\n"
                message = message + selectedPackageList[obj].packageName+", version - "+selectedPackageList[obj].updateVersion+"\n";
            } else if (type == "Remove" && selectedPackageList[obj].isRemovable){
                if (message == "")  message = "The below packages are eligible for "+type+"\n"
                message = message + selectedPackageList[obj].packageName+", version - "+selectedPackageList[obj].installedVersion+"\n";
            } else {
                continue;
            }
            packageListObj.push({
                'package_name': selectedPackageList[obj].packageName,
                'package_version': selectedPackageList[obj].updateVersion,
                'extension': selectedPackageList[obj].packageExt,
                'distro': selectedPackageList[obj].distro,
                'rel': selectedPackageList[obj].rel,
                'arch': selectedPackageList[obj].arch,
                'removable': selectedPackageList[obj].removablePackage,
                'package_type': selectedPackageList[obj].packageType,
                'installed_version': selectedPackageList[obj].installedVersion,
                'installableExt': selectedPackageList[obj].installableExt,
                'removableExt': selectedPackageList[obj].removableExt
            });
        }
        if (message != "") {
            var confRes = confirm(message);
            if (!confRes) {
                return "Cancelled";
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
        if (packageListObj == "[]") {
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
        $(selectedBuildServer).each(function(index, brand) {
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
        $("#manageRuntime").hide();
        $.getJSON("synchManagedPackageList", { serverNodeCSV: selectedBuildServerCsv },
             synchManagedPackageListCallback).fail(synchManagedPackageListCallback);
    },
    uploadPackage: function (ev) {
        var file = $('#packageFile')[0].files[0];
        var packageDetails = ""
        var packageType = $("#packageTypeOnPackageUpload").find(":selected").val();
        if ($('#packageFile').val()==''){
            showAlert("Please select a package to upload!");
            return false;
        }
        if ($('#packageFile').val().indexOf('.tar') != -1
            || $('#packageFile').val().indexOf('.zip') !=-1
            ||  $('#packageFile').val().indexOf('.bin') !=-1) {
            if (packageType == undefined || packageType == "") {
                alert("Please select Package Type");
                return false;
            } else {
                packageDetails = packageType
            }
        }
        var debDetails = $("#debSelector").find(":selected").val();
        if ($('#packageFile').val().indexOf('.deb') != -1) {
           if (debDetails == undefined || debDetails == "") {
               alert("Please select appropriate deb type");
               return false;
            } else {
                packageDetails = debDetails
            }
        }
        var rpmDetails = $("#rpmSelector").find(":selected").val();
        if ($('#packageFile').val().indexOf('.rpm') != -1) {
           if (rpmDetails == undefined || rpmDetails == "") {
               alert("Please select appropriate rpm type");
               return false;
            } else {
                packageDetails = rpmDetails
            }
        }
        jenkinsState.loadingState.packageUploadLoading = true
        var formData = new FormData();
        formData.append('packageFile', file);
        formData.append('packageDetails',packageDetails);

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
    stateFormatter: function(value, row, index){
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
    prjCompareSingle: false,
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
    compareLogs: function(ev,item) {
        var logFile = "test_result.arti"
        var buttonID = $(ev.target).attr('id');
        if (buttonID === "compareBuildLogsBtn" || buttonID === "viewBuildLogBtn")
            logFile = "build_result.arti"
        var selectedProjects = $('#testCompareSelectPanel').bootstrapTable('getSelections');
        projectReportState.selectedProjects = selectedProjects;
        projectReportState.modalHeader = "Log Compare Results";
        var sel = [];
        var selectedIndex = 0;
        var fireCall = false;
        var  searchByfullname = false;
        for (var i = 0; i < selectedProjects.length; i++){
            sel[i] = selectedProjects[i].fullName;
            selectedProjects[i].selected = false;
            if (buttonID === "viewBuildLogBtn" || buttonID === "viewTestLogBtn" )
                selectedProjects[i].logfile = logFile;
            if (item.project && item.project.fullName) {
                if (selectedProjects[i].fullName == item.project.fullName) {
                    selectedIndex = i;
                    searchByfullname = true;
                    item.project.selected = true;
                    logFile = item.project.logfile;
                }
            }
            else {
                selectedProjects[0].selected = true;
            }
        }
        if (buttonID === "viewBuildLogBtn" || buttonID === "viewTestLogBtn" || searchByfullname) {
            var leftProject = sel[selectedIndex];
            var rightProject = sel[selectedIndex];
            var leftRepo = selectedProjects[selectedIndex].repository;
            var rightRepo = selectedProjects[selectedIndex].repository;
            fireCall = true;
            projectReportState.prjCompareSingle = true;
            projectReportState.modalHeader = "Log Results";
        }
        else if (sel.length === 2) {
            if (selectedProjects[0].name != selectedProjects[1].name){
                fireCall = false
            }
            else{
                var leftProject = sel[0];
                var rightProject = sel[1];
                var leftRepo = selectedProjects[0].repository;
                var rightRepo = selectedProjects[1].repository;
                fireCall = true;
                projectReportState.prjCompareSingle = false;
                projectReportState.modalHeader = "Log Compare Results";
            }
        }
        if (fireCall) {
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
        var gsaSelections = 0;
        var query = {};
        for (var i = 0; i < selectedProjects.length; i++) {
            if (selectedProjects[i].repository != "gsa") {
                sel[i] = selectedProjects[i].fullName;
                query[sel[i]] = selectedProjects[i].repository;
            }
            else{
                gsaSelections = gsaSelections + 1;
            }
        }
        if (gsaSelections != selectedProjects.length) {
            showAlert("Local repositories chosen will be archived")
            projectReportState.loadingState.diffLoading = true;
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
        }
        else {
            showAlert("Please select local repository for archival");
        }
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
    if (typeof(autoselect) === 'undefined') autoselect = true;
    if (typeof(autoselect) !== 'boolean') autoselect = true;

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
$('#query').bind("keypress", keyPressed);
function keyPressed(e) {
    if (e.keyCode === 13) {
        doSearch();
    }
}

$('#batchFile').change(function () {
    $('#uploadFilename').val("File selected:  " + $('#batchFile').val());
});

$('#packageFile').change(function () {
    $('#uploadPackageName').val("File selected: " + $('#packageFile').val());
});

function showAlert(message, data) {
    var text = "";
    $("#apErrorDialogText").hide();
    if (typeof data !== 'undefined') {
        var msg = "";
        if (typeof data.responseJSON !== 'undefined' || typeof data.statusText !== 'undefined') {
            if (typeof data.responseJSON !== 'undefined' && data.responseJSON.error !== 'undefined') {
                msg = data.responseJSON.error;
            }
            else if (typeof data.readyState !== 'undefined' && data.readyState === 4) {
                msg = "Status: " + data.status.toString() + " Error: " + data.statusText;
            }
            else {
                msg = "Please ensure that the autoport driver / vm is running properly!";
            }
        }
        else if (data.status === "failure" && data.error !== 'undefined') {
            msg = data.error;
        }
        if (msg) {
            console.log("In showAlert, msg=", msg);
            text = "<br/>" + msg;
        }
        else {
            console.log("In showAlert, message=", message);
            console.log("showAlert: data=", data);
        }
    }
    $("#apErrorDialogText").show();
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
        if (searchState.single.loadingState.loading) {
            searchState.single.loadingState.loading = false;
        }
        showAlert("Bad response from /search!", data);
    } else if (data.type === "multiple") {
        detailState.ready = false;
        detailState.autoSelected = false;
        // Got multiple results
        // Add select function to each result
        data.results.forEach(function(result) {
            // Show detail view for repo upon selection
            result.select = function (ev) {
                var className = $(ev.target).attr('class');
                if (className === "generateDetailButton btn btn-primary") {
                    $.getJSON("detail/" + result.id, {panel: "generate", version: result.useVersion}, showDetail).fail(showDetail);
                    searchState.multiple.ready = false;
                    searchState.multiple.loadingState.loading = true;
                }
                else if (className === "singleDetailButton btn btn-primary") {
                    $.getJSON("detail/" + result.id, {panel: "single", version: result.useVersion}, showDetail).fail(showDetail);
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
    projectReportState.loadingState.diffLoading = false;
    $("#resultRemoveBtn").addClass("disabled");
    if (data === undefined || data.status === undefined || data.status != "ok") {
        showAlert("Error!", data);
    } else {
        projectReportState.projects = data.results;
        console.log("In processResultList, project list=", projectReportState.projects)
        detailState.autoSelected = false;
        projectReportState.prjCompareReady = true;

        $('#testCompareSelectPanel').bootstrapTable('load', projectReportState.projects);
    }
}

function removeProjectsCallback(data){
    projectReportState.loadingState.diffLoading = false;
    if (data.status != "ok") {
        showAlert("Error:", data);
    } else {
        showAlert("Deleted Successfully !");
        if (projectReportState.compareRepo == "local") {
            reportState.listLocalProjects();
        } else if (projectReportState.compareRepo == "archived") {
            reportState.listGSAProjects();
        } else {
            reportState.listAllProjects();
        }
    }
}

function removeBatchReportsCallback(data){
    console.log("In removeBatchReportsCallback, data=", data);
    if (data.status != "ok") {
        showAlert("Error:", data);
    } else {
        showAlert("Deleted Successfully !");
        if (batchReportState.listingRepo == "local") {
            batchReportState.listLocalBatch();
        } else if (batchReportState.listingRepo == "gsa") {
            batchReportState.listGSABatch();
        } else {
            batchReportState.listAllBatch();
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

function processBatchBuildLogResults(data) {
    if (data.status != "ok") {
         $("#batchLeftdiff").html("No Test Results Found");
    } else {
        var left = data.leftCol;
        var right = data.rightCol;

        var headerContent = "<table id=\"batchLogdiffHeader1\" >" +
                                 "<th style=\"border:none\">" +
                                      left['log'] + "<br />" +
                                      "[" + left['repo'] + "] " + left['job'] + "<br />" +
                                      left['pkgname'] + "-" + left['pkgver'] + "<br />" +
                                      left['distro'] +
                                 "</th>" ;
         headerContent+="</table>";
         $("#batchLogdiffHeader").html(headerContent);
         $("#batchLeftdiff").html(data.results['diff'][left['diffName']]);
         $('#batchLogdiffModal').on('show.bs.modal', function() {
         $('#batchLeftdiff span').each(function(index) {
            var elementID = "searchcontrol"+index;
               var html = '<div id="' + elementID + '"></div>';
               $('#batchLogdiffModal').append(html);
               $(this).qtip({
                 content: {
                             text: function(event, api) {
                                      try {
                                          var searchControl = new google.search.SearchControl();
                                          searchControl.addSearcher(new google.search.WebSearch());
                                          searchControl.draw(document.getElementById(elementID));
                                          var searchword = $(this).text();
                                          if (searchword.length > 40) {
                                               searchword = searchword.substring(searchword.length - 40);
                                          }
                                          searchControl.execute(searchword);
                                          return $("#"+elementID);
                                      }
                                      catch(err) {
                                      }
                                   },
                               title: 'From Google Search',
                               button: true
                               },
                   position: {
                       viewport: $(window)
                             },
                   hide: false
                   });
                  });
                });
           $('#batchLogdiffModal').on('hidden.bs.modal', function () {
             $('#batchLeftdiff span').each(function(index) {
                       if( $(this).data('qtip')) {
                             $(this).qtip('destroy', true);
                                }
                    });
                });

           $('#batchLogdiffModal').modal('show');
    }
    batchReportState.prjCompareReady = true;
    if($('.nav-pills li ul').find('.active').length ==0)
        $('.nav-pills li ul li:first').addClass("active");
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
                                 "</th>" ;
        if (!projectReportState.prjCompareSingle) {
            headerContent+= "<th style=\"border:none\">" +
                                      right['log'] + "<br />" +
                                      "[" + right['repo'] + "] " + right['job'] + "<br />" +
                                      right['pkgname'] + "-" + right['pkgver'] + "<br />" +
                                      right['distro'] +
                                 "</th>";
        }

        headerContent+="</table>";
        $("#logdiffHeader").html(headerContent);
        $("#leftdiff").html(data.results['diff'][left['diffName']]);
        if (!projectReportState.prjCompareSingle){
            $("#rightdiff").html(data.results['diff'][right['diffName']]);
        }
        projectReportState.diffClass = !projectReportState.prjCompareSingle;

        $('#logdiffModal').on('show.bs.modal', function() {
            $('#leftdiff span, #rightdiff span').each(function(index) {
                var elementID = "searchcontrol"+index;
                var html = '<div id="' + elementID + '"></div>';
                $('#logdiffModal').append(html);
                $(this).qtip({
                    content: {
                        text: function(event, api) {
                            try {
                                var searchControl = new google.search.SearchControl();
                                searchControl.addSearcher(new google.search.WebSearch());
                                searchControl.draw(document.getElementById(elementID));
                                var searchword = $(this).text();
                                if (searchword.length > 40) {
                                    searchword = searchword.substring(searchword.length - 40);
                                }
                                searchControl.execute(searchword);
                                return $("#"+elementID);
                            }
                            catch(err){}
                        },
                        title: 'From Google Search',
                        button: true
                    },
                    position: {
                        viewport: $(window)
                    },
                    hide: false
               });
           });
        });
        $('#logdiffModal').on('hidden.bs.modal', function () {
            $('#leftdiff span, #rightdiff span').each(function(index) {
                if( $(this).data('qtip')) {
                    $(this).qtip('destroy', true);
                }
            });
       });

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
        // Hide listing of Batch jobs before showing the batch details.
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

        batchNames = Object.keys(data.results);
        var all_jobs = [];

        for (var j = 0; j < batchNames.length; j++){
            if (batchNames[j] !== 'status'){
                all_jobs = all_jobs.concat(data.results[batchNames[j]]);
            }
        }

        // Populate Batch details in table.
        for (var i = 0; i < all_jobs.length; i++) {
            if (main_header_data !== null) {
                main_header_data += ', ' + all_jobs[i].job;
            } else {
                main_header_data = all_jobs[i].job;
            }

            data_table.appendChild(populate_batch_table_headers(all_jobs[i].pkg, all_jobs[i].ver));
            data_table.appendChild(populate_batch_table_data(all_jobs[i].pkg, all_jobs[i].results));
            var blank_text = document.createTextNode('');
            blank_cell.appendChild(blank_text);
            blank_row.appendChild(blank_cell);
            data_table.appendChild(blank_row);
        }

        // finally append the Batch details table to the placeholder table on UI.
        var tr = document.createElement('tr');
        tr.appendChild(data_table);
        main_table.appendChild(tr);

        $("#batchHeader").html(main_header_data); // Add code to generate headers data similar to existing logic for projects
        $("#batchHeaderPreText").html('Test results for Batch job(s): ');
        batchReportState.batchReportTableReady = true;
    }
    batchReportState.loading = false;
}

function processBatchHistory(data){
    ProjectRegExp = /(.*?)\.(.*?)\.(.*?)\.N-(.*?)\.(.*?)\.(\d\d\d\d-\d\d-\d\d-h\d\d-m\d\d-s\d\d)/i;
    if (data["results"]) {
        batchReportState.showListSelectTable = false;

        var batchNames = Object.keys(data["results"]);
        var batchReportTestHistory = [];
        var job_list = data["results"];
        var all_jobs = [];

        for (var j = 0; j < batchNames.length; j++){
            if (batchNames[j] !== 'status') {
                all_jobs = all_jobs.concat(data.results[batchNames[j]]);
            }
        }

        for (var j = 0; j < all_jobs.length; j++){
            var splitted_job_info = ProjectRegExp.exec(all_jobs[j]["job"]);
            var arch = splitted_job_info[3];
            var name = splitted_job_info[4];
            var version = splitted_job_info[5];
            var timestamp = splitted_job_info[6];
            var results = all_jobs[j]["results"];
            batchReportTestHistory[timestamp] = {"arch":arch, "name":name, "version":version,"results":results, "job":all_jobs[j]["job"]};
        }
        var keys = Object.keys(batchReportTestHistory);
        keys.sort(function(a,b){
            var date1 = a.replace("-h", "T");
            date1 = date1.replace("-m", ":");
            date1 = date1.replace("-s", ":");

            var date2 = b.replace("-h", "T");
            date2 = date2.replace("-m", ":");
            date2 = date2.replace("-s", ":");
            return new Date(date1) - new Date(date2);
        });
        var tempBatchReportResp = [];
        for (var i=0;i<keys.length;i++){
            tempBatchReportResp[keys[i]] = batchReportTestHistory[keys[i]];
        }
        batchReportTestHistory = [];
        batchReportTestHistory = tempBatchReportResp;
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
        batchNames = Object.keys(batchReportTestHistory);
        for (var i = 0; i < Object.keys(batchReportTestHistory).length; i++) {
            var report = batchReportTestHistory[batchNames[i]];
            if(main_header_data !== null){
                main_header_data += ', ' + report.job;
            }else{
                main_header_data = report.job;
            }
            data_table.appendChild(populate_batch_table_headers(report.name, report.version));
            data_table.appendChild(populate_batch_table_data(report.name, report.results));
            var blank_text = document.createTextNode('');
            blank_cell.appendChild(blank_text);
            blank_row.appendChild(blank_cell);
            data_table.appendChild(blank_row);
        }
        var tr = document.createElement('tr');
        tr.appendChild(data_table);
        main_table.appendChild(tr);
        $("#batchHeader").html(main_header_data); // Add code to generate headers data similar to existing logic for projects
        $("#batchHeaderPreText").html('Test history for Batch job(s): ');
        batchReportState.batchReportTableReady = true;
    } else {
         showAlert("Error:", data);
    }
    batchReportState.loading = false;
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
    projectReportState.loadingState.diffLoading = false;
    console.log("In archiveCallback, data.status=", data.status);
    if (data.status === "ok" ) {
        showAlert("Archived successfully");
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
        if (projectReportState.compareRepo == "local") {
            reportState.listLocalProjects();
        }
        else {
            reportState.listAllProjects();
        }
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

    for (var i=0, iLen=options.length; i<iLen; i++) {
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
                var javaType = detailState.javaType.split(' ')[0];
                var javaVersion = (detailState.supportedJavaList[detailState.javaType])?detailState.supportedJavaList[detailState.javaType]:7;
                var javaScriptType = detailState.javaScriptType.split(' ')[0];
                var javaScriptVersion = (detailState.supportedJavaScriptList[detailState.javaScriptType])?detailState.supportedJavaScriptList[detailState.javaScriptType]:0;
                var javaScriptTypeVersion = javaScriptType + ',' + javaScriptVersion;
                if (javaScriptType == 'nodejs'){
                    javaScriptTypeVersion = '';
                }
                for (var i=0; i < buildServers.length; i++) {
                    console.log(detailState.repo.useVersion + " version");
                    $.post("createJob", {id: detailState.repo.id, tag: detailState.repo.useVersion,
                           javaType: javaType+','+javaVersion, javaScriptType: javaScriptTypeVersion,
                           node: buildServers[i], selectedBuild: selectedBuild,
                           selectedTest: selectedTest, selectedEnv: selectedEnv,
                           artifacts: buildInfo.artifacts, primaryLang: buildInfo.primaryLang},
                           addToJenkinsCallback, "json").fail(addToJenkinsCallback);
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
            detailState.generateRepo.javaType = detailState.supportedJavaListOptions[0];

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
                var javaType = detailState.generateRepo.javaType.split(' ')[0];
                var javaVersion = (detailState.supportedJavaList[detailState.generateRepo.javaType])?detailState.supportedJavaList[detailState.generateRepo.javaType]:7;
                var javaScriptType = detailState.generateJavaScriptType.split(' ')[0];
                var javaScriptVersion = (detailState.supportedJavaScriptList[detailState.generateJavaScriptType])?detailState.supportedJavaScriptList[detailState.generateJavaScriptType]:0;
                var javaScriptTypeVersion = javaScriptType + ',' + javaScriptVersion;
                if (javaScriptType == 'nodejs'){
                    javaScriptTypeVersion = '';
                }
                for (var i=0; i < buildServers.length; i++) {
                    $.post("createJob", {id: detailState.generateRepo.id, tag: detailState.generateRepo.useVersion,
                            javaType: javaType+','+javaVersion, javaScriptType: javaScriptTypeVersion,
                            node: buildServers[i], selectedBuild: selectedBuild, selectedTest: selectedTest,
                            selectedEnv: selectedEnv, artifacts: buildInfo.artifacts, primaryLang: buildInfo.primaryLang},
                            addToJenkinsCallback, "json").fail(addToJenkinsCallback);
                }
            };
            detailState.generateRepo.updateVersion = function(e) {
                detailState.generateRepo.useVersion = e.target.innerHTML;
            };
            detailState.generateRepo.selectGenerateJavaType = function(ev) {
                var selection = $(ev.target).text().toLowerCase();
                detailState.generateRepo.javaType = $(ev.target).text();
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
    $('.dropMenuScroll').css('max-height',($('#singleDetailPanel').height()-140)+"px");
    $('.multiSearchDropMenuScroller').css('max-height',($('#generateBox').height()-110)+"px");
}

// assign variables in global state
function initCallback(data) {
    if (data.status !== "ok") {
        showAlert("Bad response from /init!", data);
    }
    console.log("In initCallBack, cloudNodeInfo=", data.cloudNodeInfo);
    globalState.hasInit = true;
    globalState.cloudNodeInfo = data.cloudNodeInfo;
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
    globalState.tempJenkinsUrl = data.jenkinsUrl;

    console.log("initCallBack: jenkinsUrl=" + globalState.jenkinsUrl);

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
        if (globalState.tempJenkinsUrl != $('#url').val()){
            jenkinsState.nodeNames = [];
            jenkinsState.nodeLabels = [];
            jenkinsState.nodeDetails = [];
            jenkinsState.nodeRHEL = [];
            jenkinsState.nodeCentOS = [];
            jenkinsState.nodeUbuntu = [];
            getJenkinsNodesCallback(data);
            showAlert("Updated successfully");
        }
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
    else {
        showAlert("Batch file uploaded successfully!");
    }

}

function uploadPackageCallback(data) {
    jenkinsState.loadingState.packageUploadLoading = false;
    jenkinsState.clearPackage();
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

function batchSaveCallback(data, batchStateObj) {
    console.log("In batchSaveCallback");
    if (data.status !== "ok") {
        showAlert("", data);
    } else {
        showAlert("Batch file saved successfully");
        batchState.fileList.push(batchState.batchFile);
        if (batchStateObj.batchListingRepo == "local"){
            batchStateObj.listLocalBatchFiles();
        } else if (batchStateObj.batchListingRepo == "gsa"){
             batchStateObj.listArchivedBatchFiles();
        } else {
            batchStateObj.listAllBatchFiles();
        }
    }
}

function runBatchFileCallback(data) {
    console.log("In runBatchFileCallback");
    batchState.loading = false;
    if (data.status !== "ok") {
        showAlert("", data);
    } else {
        showAlert("Batch job submitted");
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
        // If data is retrieved successfully continue preparations.
        // Get data and update batchReportState attributes.
        batch_obj.showListSelectTable = false;
        batch_obj.showBatchFile = true;
        batch_obj.batchFile = data.results;
        batch_obj.saveBatchFileName = data.results.config.name;
        batch_obj.javaType = data.results.config.java;
        batch_obj.javaScriptType = data.results.config.javascript;


        if (data.results.config.includeTestCmds === "True") {
            batch_obj.includeTestCmds = true;
        } else {
            batch_obj.includeTestCmds = false;
        }
        if (data.results.config.includeInstallCmds === "True") {
            batch_obj.includeInstallCmds = true;
        } else {
            batch_obj.includeInstallCmds = false;
        }

        console.log("In parseBatchFileCallback, batchFile.config=", data.results.config);

        var buildInstallTable = $('<table border="1" class="table panel panel-default table-hover"></table>').attr({ id: "buildInstallTable" });

        // Defined the behaviour for moving packages up/down/remove if batchState object
        var index = 0;
        data.results.packages.forEach(function(package) {
            package.build.index = index;
            index = index + 1

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
    batchState.loading = false;
    $("#batch_report_remove").addClass("disabled");
    if (data === undefined || data.status === undefined || data.status != "ok") {
        showAlert("Error!", data);
    } else {
        batchState.fileList = data.results;
        console.log(batchState.fileList);
        batchState.showListSelectTable = true;

        $('#batchListSelectTable').bootstrapTable('load', batchState.fileList);
    }
}

function listBatchReportFilesCallback(data) {
    batchReportState.loading = false;
    if (data.status === "ok") {
        batchReportState.fileList = data.results;
        batchReportState.showListSelectTable = true;

        $('#batchReportListSelectTable').bootstrapTable('load', batchReportState.fileList);
    } else {
        showAlert("Error!", data);
    }
}

function removeBatchFileCallback(data) {
    if (data.status === "ok") {
        showAlert("Removed successfully!");
    } else {
        showAlert("Error!", data);
    }
}

function archiveBatchFileCallback(data) {
    batchState.loading = false;
    if (data.status === "ok") {
        showAlert("Archived successfully");
    } else {
        showAlert("Error!", data);
    }
}

function archiveBatchReportsCallback(data) {
    batchReportState.loading = false;
    if (data.status === "ok") {
        showAlert("Archived Successfully!")
        if (batchReportState.listingRepo == "local"){
            batchReportState.listLocalBatch();
        } else if (batchReportState.listingRepo == "gsa"){
            batchReportState.listGSABatch();
        } else {
            batchReportState.listAllBatch();
        }
    } else {
        showAlert("Error!", data);
    }
}

function addToJenkinsCallback(data) {
    // TODO - need to take in a list of sjobUrls and hjobUrls and then iterate over the list
    batchState.loading = false;
    if (data.status === "ok") {
        // Open new windows with the jobs' home pages
        window.open(data.hjobUrl,'_blank');
        percentageState.updateProgressBar();
        showAlert("Build job submitted");
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

        var labels = JSON.stringify(data.nodeLabels);
        $.post("getJenkinsNodeDetails", {nodeLabels: labels},
             getJenkinsNodeDetailsCallback, "json").fail(getJenkinsNodeDetailsCallback);
    }
    else {
        showAlert("Could not get Jenkins slaves", data);
    }
}

function getJenkinsNodeDetailsCallback(data) {
    console.log("In getJenkinsNodeDetailsCallback");
    $('#toolContainer').removeClass('hide');
    $('#loading_screen').hide();
    if (data.status === "ok") {
        jenkinsState.nodeDetails = data.details;
        jenkinsState.nodeUbuntu = data.ubuntu;
        jenkinsState.nodeRHEL = data.rhel;
        jenkinsState.nodeCentOS = data.centos;
        if (jenkinsState.nodeUbuntu.length > 0) {
            jenkinsState.nodeOSes = ['Ubuntu'];
        }
        if (jenkinsState.nodeRHEL.length > 0){
            jenkinsState.nodeOSes.push('RHEL');
        }
        if (jenkinsState.nodeCentOS.length > 0){
            jenkinsState.nodeOSes.push('CentOS');
        }
        jenkinsState.nodeOSes.push('ALL')
        console.log("Ubuntu nodes: ", jenkinsState.nodeUbuntu);
        console.log("RHEL nodes: ", jenkinsState.nodeRHEL);
        console.log("CentOS nodes: ", jenkinsState.nodeCentOS);
        for (i = 0; i < jenkinsState.nodeDetails.length; i++) {
            console.log("Node details: ", jenkinsState.nodeDetails[i]);
        }
        updateDropdownsWithNodeDetails();
    }
    else {
        showAlert("Could not get Jenkins slaves", data);
    }
}

function updateDropdownsWithNodeDetails(){
    jenkinsState.buildServer = "";
    $('#singleJenkinsBuildServers').multiselect('refresh');
    $('#singleJenkinsBuildServers').multiselect('destroy');
    $('#singleJenkinsBuildServers').multiselect('deselect', jenkinsState.nodeLabels);
    $('#singleJenkinsBuildServers+div>button>span').text('Build Servers');
    $('#singleJenkinsBuildServers+div>button').addClass('btn btn-primary');

    $('#buildServersOSes').multiselect('refresh');
    $('#buildServersOSes').multiselect('destroy');
    $('#buildServersOSes').multiselect('deselect', jenkinsState.nodeOSes);
    $('#buildServersOSes+div>button>span').text('Select Distribution');
    $('#buildServersOSes+div>button').addClass('btn btn-primary');

    $('#singleBuildServers').multiselect('refresh');
    $('#singleBuildServers').multiselect('destroy');
    $('#singleBuildServers').multiselect('select', jenkinsState.nodeLabels);
    $('#singleBuildServers+div>button>span').text('Select Build Servers');
    $('#singleBuildServers+div>button').addClass('btn btn-primary');

    $('#generateBuildServers').multiselect('refresh');
    $('#generateBuildServers').multiselect('destroy');
    $('#generateBuildServers').multiselect('select', jenkinsState.nodeLabels);
    $('#generateBuildServers+div>button>span').text('Select Build Servers');
    $('#generateBuildServers+div>button').addClass('btn btn-primary');

    $('#batchBuildServers').multiselect('refresh');
    $('#batchBuildServers').multiselect('destroy');
    $('#batchBuildServers').multiselect('deselect', jenkinsState.nodeLabels);
    $('#batchBuildServers+div>button>span').text('Build Servers');
    $('#batchBuildServers+div>button').addClass('btn btn-primary');
}

function listPackageForSingleSlaveCallback(data) {
    jenkinsState.loadingState.packageListLoading = false;
    if (data.status === "ok") {
        jenkinsState.packageListSingleSlave = data.packageData
        jenkinsState.singleSlavePackageTableReady = true;

        $('#singleServerPackageListTable').bootstrapTable('load', jenkinsState.packageListSingleSlave);
    } else {
        if(data!=undefined && data.status!=undefined && data.status=="failure") {
            showAlert("Error!", data);
        }
    }
    $("#singleSlaveListBtn").removeClass("disabled");
}

function managePackageForSingleSlaveCallback(data, pkgName, action) {
    jenkinsState.pkgInstallRemoveResponseCounter++;
    if (data.status === "ok") {
        jenkinsState.singleSlavePackageTableReady = false;
        jenkinsState.pkgInstallRemoveStatusSingleSlave.push({'packageName':pkgName,
                            'packageAction':action, 'status': data.buildStatus});
    } else {
        var status = data.buildStatus;
        if (status == undefined)
            status = "Error";
        jenkinsState.pkgInstallRemoveStatusSingleSlave.push({'packageName':pkgName,
        'packageAction':action, 'status': status, 'logUrl': data.logUrl});
    }
    if ( jenkinsState.pkgInstallRemoveResponseCounter == jenkinsState.totalSelectedSingleSlavePkg ) {
        jenkinsState.loadingState.packageActionLoading = false;
        var text = '<table class="table table-condensed">';
        text += '<tr class="active"><td>Package Name</td><td>Action</td><td>Status</td></tr>';
        if (jenkinsState.pkgInstallRemoveStatusSingleSlave.length>0) {
            var activeclass = "active";
            for (var i in jenkinsState.pkgInstallRemoveStatusSingleSlave) {
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
                text += '<td>' + jenkinsState.pkgInstallRemoveStatusSingleSlave[i].packageAction + '/update</td>';
                if (jenkinsState.pkgInstallRemoveStatusSingleSlave[i].logUrl) {
                  text += '<td>' + "<a href='" +
                  jenkinsState.pkgInstallRemoveStatusSingleSlave[i].logUrl +
                  "' target='_blank'  style='text-decoration: underline' >" +
                  jenkinsState.pkgInstallRemoveStatusSingleSlave[i].status + "</a>" + '</td>';
                } else {
                  text += '<td>' + jenkinsState.pkgInstallRemoveStatusSingleSlave[i].status + '</td>';
                }
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
        $("#manageRuntime").show();
        if ($('#packageFilter_Multiple').val() == ""){
            $("#multiServerPackageListTable thead tr th:nth-child(5) div:nth-child(1)").text("Available Version");
        } else {
            $("#multiServerPackageListTable thead tr th:nth-child(5) div:nth-child(1)").text("Latest Version");
        }
        jenkinsState.managedPackageList = data.packages;
        jenkinsState.managedPackageTableReady = true;
        $("#multiServerPackageListTable").bootstrapTable('load', jenkinsState.managedPackageList);
    } else {
        if(data!=undefined && data.status!=undefined && data.status=="failure") {
            showAlert("Error!", data);
        }
    }
    $("#managedListBtn").removeClass("disabled");
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
   var pollmessage = "";
   var pollstatus = false;
   return {
       // function setData sets the data that needs to be passed to the server during polling
       setData: function(data) {
           dataJob = data;
       },
       // function setMessage:  sets the message
       setMessage: function(data) {
           pollmessage = data;
       },
       // function appendMessage: appends message to the previous message
       appendMessage: function(data) {
           pollmessage += data;
       },
       // function displayMessage:  displays message
       displayMessage: function(data) {
           showAlert(pollmessage);
       },
       // function poll: polls server using ajax
       poll: function(cb) {
           console.log("polling....."+JSON.stringify(dataJob));
           if (pollCounter < pollAttempts) {
               if (dataJob.jobName != undefined) {
                   jenkinsState.loadingState.managedPackageActionLoading = true;
                   $("#syncManagedPackageButton").addClass("disabled");

                   $.getJSON("monitorJob", dataJob, notificationCallback(this,cb)).fail(notificationCallback(this,cb));
                   pollCounter++;
               }
               if (dataJob.serverNodeCSV != undefined) {
                   $.getJSON("rebuildSlave", dataJob, cb).fail(cb);
                   pollCounter++;
               }
           }
           else{
               this.appendMessage("<br><span>Unable to fetch data from server.</span>");
               this.displayMessage();
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

function notificationCallback(obj, cb){
    var title = "", message = "",type="", classcss="";

    return function(data) {
        if (data.jobstatus) {
            title = (data.jobstatus) ? data.jobstatus : '';
            if (data.jobstatus == "SUCCESS") {
                type = "success";
                classcss = "text-success";
                message= "<br><span class='"+classcss+"'>Sync completed successfully on "+data.nodeLabel+"</span>";
            }
            if (data.jobstatus == "FAILURE") {
                type = "danger";
                classcss = "text-danger";
                message= "<br/><span class='"+classcss+"'>Sync completed with few errors on  " +
                data.nodeLabel+" .Please check the <a href='" +
                data.logUrl+"' target='_blank'  style='text-decoration: underline' >log</a> for details"+"</span>";
            }
            if (cb!= undefined)
                cb();
            /*$.notify({
                 title: "<strong>"+title+"</strong> ",
                 message: message
            },
            {
                type: type
            });*/
            obj.appendMessage(message);
            obj.displayMessage();
            //$("#notifyManagedPanel").append("<br><span class='"+classcss+"'><strong>"+title+"</strong> "+message+"</span>");
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
        var pollObj = new pollingState();
        pollObj.setMessage("<br>"+data.message);
        // Client server polling
        if (data.jobList.length > 0){
            for (var i=0; i< data.jobList.length; i++) {
                var dataJob = data.jobList[i];
                /*$("#notifyManagedPanel").append("<br>"+dataJob.install +" package(s) to be installed and "
                                               + dataJob.uninstalls + " package(s) to be uninstalled on "
                                               + dataJob.nodeLabel);*/
                pollObj.appendMessage("<br>"+dataJob.install +" package(s) to be installed and "
                               + dataJob.uninstalls + " package(s) to be uninstalled on "
                               + dataJob.nodeLabel);
                pollObj.setData(dataJob);
                setTimeout(pollObj.poll(),5000);
            }
        }
        pollObj.displayMessage();
    } else {
        showAlert("Error!", data);
    }
}

// Compares two versions
function compareVersion(version1, version2){
    var result = false;
    if (typeof version1 !== 'object') { version1 = version1.toString().split('.'); }
    if (typeof version2 !== 'object') { version2 = version2.toString().split('.'); }
    for (var i=0;i<(Math.max(version1.length,version2.length));i++){
        if (version1[i] == undefined) { version1[i] = 0; }
        if (version2[i] == undefined) { version2[i] = 0; }
        if (Number(version1[i]) < Number(version2[i])) {
            result = true;
            break;
        }
        if (version1[i] != version2[i]) {
            break;
        }
    }
    return(result);
}

function toggleBatchStateButtons() {
    var selectedBatchFiles = $('#batchListSelectTable').bootstrapTable('getSelections');
    console.log("In toggleBatchStateButtons, selectedBatchFiles=", selectedBatchFiles.length);
    if (selectedBatchFiles.length > 0) {
        $('#batch_file_remove').removeClass('disabled');
        $('#batch_file_archive').removeClass('disabled');
        $('#batch_build_test').removeClass('disabled');
        $('#batch_details').removeClass('disabled');
    }
    else {
        $('#batch_file_remove').addClass('disabled');
        $('#batch_file_archive').addClass('disabled');
        $('#batch_build_test').addClass('disabled');
        $('#batch_details').addClass('disabled');
    }
}


function toggleProjectReportButtons(){
    var selectedProjects = $('#testCompareSelectPanel').bootstrapTable('getSelections');
    console.log("In toggleProjectReportButtons, selectedProjects=", selectedProjects.length);
    if (selectedProjects.length === 2) {
        $("#compareResultsBtn").removeClass("disabled");
        $("#compareBuildLogsBtn").removeClass("disabled");
        $("#compareTestLogsBtn").removeClass("disabled");
    }
    else {
        $("#compareResultsBtn").addClass("disabled");
        $("#compareBuildLogsBtn").addClass("disabled");
        $("#compareTestLogsBtn").addClass("disabled");
    }
    if (selectedProjects.length === 0) {
        $("#testHistoryBtn").addClass("disabled");
        $("#testDetailBtn").addClass("disabled");
        $("#resultArchiveBtn").addClass("disabled");
        $("#resultRemoveBtn").addClass("disabled");
    }
    else {
        $("#testHistoryBtn").removeClass("disabled");
        $("#testDetailBtn").removeClass("disabled");
        $("#resultArchiveBtn").removeClass("disabled");
        $("#resultRemoveBtn").removeClass("disabled");
    }
}

function toggleBatchReportButtons(){
    var selectedBatchFiles = $('#batchReportListSelectTable').bootstrapTable('getSelections');
    console.log("In toggleBatchReportButtons, selectedBatchFiles=", selectedBatchFiles.length);
    if (selectedBatchFiles.length === 2) {
        $("#batch_report_compare").removeClass("disabled");
        $("#batch_report_compare_build_log").removeClass("disabled");
        $("#batch_report_compare_test_log").removeClass("disabled");
    } else {
        $("#batch_report_compare").addClass("disabled");
        $("#batch_report_compare_build_log").addClass("disabled");
        $("#batch_report_compare_test_log").addClass("disabled");
    }

    if (selectedBatchFiles.length > 0) {
        $("#batch_report_remove").removeClass("disabled");
        $("#batch_report_history").removeClass("disabled");
        $("#batch_report_detail").removeClass("disabled");
        $("#batch_report_history").removeClass("disabled");
        $("#batch_report_remove").removeClass("disabled");
    } else {
        $("#batch_report_remove").addClass("disabled");
        $("#batch_report_archive").addClass("disabled");
        $("#batch_report_history").addClass("disabled");
        $("#batch_report_detail").addClass("disabled");
        $("#batch_report_remove").addClass("disabled");
    }

    for (var i = 0; i < selectedBatchFiles.length; i++) {
        if (selectedBatchFiles[i].repo == 'local'){
            $("#batch_report_archive").removeClass("disabled");
            break;
        }
        $("#batch_report_archive").addClass("disabled");
    }
}

/**
 * This Function will generate Object with data in following
 * format which will be used for getting left and right tables.
 * {
    "MEAN-R.562595.2015-09-02-h16-m36-s30": {
        "local-desktop.562595.x86-64-rhel-7.1.N-node-v0.x-archive.current.2015-09-29-h14-m01-s57": {
            "node-v0": {
                "arch": "x86-64-rhel-7.1",
                "version": "x-archive.current",
                "timestamp": "2015-09-29-h14-m01-s57",
                "results": {}
            }
        },
        "local-desktop.562595.x86-64-rhel-7.1.N-redis.current.2015-09-29-h14-m01-s57": {
            "redis": {
                "arch": "x86-64-rhel-7.1",
                "version": "current",
                "timestamp": "2015-09-29-h14-m01-s57",
                "results": {
                    "duration": 0,
                    "errors": 0,
                    "failures": 0,
                    "results": {},
                    "skipped": 0,
                    "total": 0
                }
            }
        },
        "local-desktop.562595.x86-64-rhel-7.1.N-angularjs.current.2015-09-29-h14-m01-s57": {
            "angularjs": {
                "arch": "x86-64-rhel-7.1",
                "version": "current",
                "timestamp": "2015-09-29-h14-m01-s57",
                "results": {
                    "duration": 0,
                    "errors": 0,
                    "failures": 0,
                    "results": {},
                    "skipped": 0,
                    "total": 0
                }
            }
        }
    },
    "MEAN-R.734853.2015-09-02-h16-m36-s30": {
        "local-desktop.734853.ppcle-ubuntu-14.04.N-node-v0.x-archive.current.2015-09-29-h17-m03-s51": {
            "node-v0": {
                "arch": "ppcle-ubuntu-14.04",
                "version": "x-archive.current",
                "timestamp": "2015-09-29-h17-m03-s51",
                "results": {}
            }
        },
        "local-desktop.734853.ppcle-ubuntu-14.04.N-redis.current.2015-09-29-h17-m03-s51": {
            "redis": {
                "arch": "ppcle-ubuntu-14.04",
                "version": "current",
                "timestamp": "2015-09-29-h17-m03-s51",
                "results": {
                    "duration": 0,
                    "errors": 0,
                    "failures": 0,
                    "results": {},
                    "skipped": 0,
                    "total": 0
                }
            }
        },
        "local-desktop.734853.ppcle-ubuntu-14.04.N-angularjs.current.2015-09-29-h17-m03-s51": {
            "angularjs": {
                "arch": "ppcle-ubuntu-14.04",
                "version": "current",
                "timestamp": "2015-09-29-h17-m03-s51",
                "results": {}
            }
        }
    }
}
 * @param organizedData
 * @param data
 * @param elemPosition
 * @returns updated organizedData
 */
function generateOrganizedData(organizedData, data, batch_name, more_info, elemPosition){
    var arch = more_info[1];
    var name = more_info[0];
    var version = more_info[2];
    var timestamp = more_info[3];
    var results = more_info[4];
    var job_name = data[elemPosition]["job"];

    if (organizedData[batch_name] === undefined){
        organizedData[batch_name] = {};
    }

    if (organizedData[batch_name][job_name] === undefined){
        organizedData[batch_name][job_name] = {};
    }

    if (organizedData[batch_name][job_name][name] === undefined){
        organizedData[batch_name][job_name][name] = {};
    }

    organizedData[batch_name][job_name][name] = {
        "arch": arch,
        "version": version,
        "timestamp": timestamp,
        "results": data[elemPosition]["results"]
    };

    return organizedData;
}

/**
 * This function will organize the data in the format
 * which will allow us to show comparison based on following criteria
 * 1. Build slave architecture where job was executed.
 * 2. Project version which was executed on Build slave.
 * 3. Datetime when the job was submitted.
 * @param data
 */
function processBatchCompare(data) {
    if (data.status == "failure") {
        batchReportState.loading = false;
        showAlert(data.error);
        return;
    }
    ProjectRegExp = /(.*?)\.(.*?)\.(.*?)\.N-(.*?)\.(.*?)\.(\d\d\d\d-\d\d-\d\d-h\d\d-m\d\d-s\d\d)/i;
    organizedData = {};
    if (data["results"]) {
        // Hide listing of Batch jiobs before showing the batch details.
        batchReportState.showListSelectTable = false;

        batchNames = Object.keys(data["results"]);

        for (var j = 0; j < batchNames.length; j++) {
            if (batchNames[j] !== "status") {
                job_list = data["results"][batchNames[j]];
                for (var i = 0; i < job_list.length; i++) {
                    try {
                        splitted_job_info = ProjectRegExp.exec(job_list[i]["job"]);
                        arch = splitted_job_info[3];
                        name = splitted_job_info[4];
                        version = splitted_job_info[5];
                        timestamp = splitted_job_info[6].replace('-m', ':').replace('-s', ':').replace('-h', ' ');
                        results = job_list[i]["results"];
                        var more_info = [name, arch, version, timestamp, results];
                        // Prepare data for comparison between two batch jobs.
                        organizedData = generateOrganizedData(organizedData, job_list, batchNames[j], more_info, i);
                    } catch(e) {
                        console.log(e);
                    }
                }
            }
        }

        organizedDataKeys = Object.keys(organizedData);
        // Now the first key will be left table and second key will be used for right table.
        // Generate left table. All other info will be used for generating metadata info
        processBatchCompareData(organizedData);
        batchReportState.batchReportTableReady = true;
        batchReportState.loading = false;
    }
}

/**
 * This function will organize the data in the format
 * which will allow us to show comparison between Logs for given batch jobs.
 * @param data
 * @param batch_report_obj
 */
function processBatchTestLogCompare(data, batch_report_obj){
    if (data.status == "failure") {
        batch_report_obj.loading = false;
        batchReportState.batchReportLogRequested = false;
        showAlert(data.error);
        return;
    }
    if (data["results"]) {
        // Hide listing of Batch jiobs before showing the batch details.
        batch_report_obj.showListSelectTable = false;
        var keys = Object.keys(data["results"]);
        var left_parent_batch = null;
        var right_parent_batch = null
        var table_rows = [];

        if (keys.length === 3) {
            var main_table = document.getElementById("testBatchLogResultsTable");
            left_arch = '';
            right_arch = '';
            batchName = '';
            for (var i = 0; i < keys.length; i++) {
                if (keys[i] == 'left_arch'){
                    left_arch = data["results"][keys[i]];
                } else if (keys[i] == 'right_arch') {
                    right_arch = data["results"]["right_arch"];
                } else {
                    batchName = keys[i];
                }
            }

            // First generate all non-header data, once done generate header as the required info
            // about parent batch name will be available after traversing project data.
            for (project in data["results"][batchName]) {
                if (!left_parent_batch) {
                    left_parent_batch = data["results"][batchName][project]["left_parent_name"];
                }
                if (!right_parent_batch) {
                    right_parent_batch = data["results"][batchName][project]["right_parent_name"];
                }
                var new_row = generate_batch_log_compare_row(data["results"][batchName][project], project);
                if (new_row !== null) {
                    table_rows.push(new_row);
                }
            }

            main_table.appendChild(generate_batch_log_compare_header(left_parent_batch, right_parent_batch, left_arch, right_arch));
            for (var i = 0; i < table_rows.length; i++) {
                var blank_row = document.createElement('tr');
                var blank_cell = blank_row.insertCell(0);
                blank_cell.setAttribute('colspan', '12');
                blank_cell.innerHTML = "&nbsp;";
                main_table.appendChild(blank_row);
                main_table.appendChild(table_rows[i]);
            }
        }
        batch_report_obj.batchReportTableReady = false;
        batch_report_obj.batchReportLogRequested = true;
        batch_report_obj.loading = false;
    }
}

function generate_batch_log_compare_row(comparison_data, projectName, shouldColorCode){
    project_diff = comparison_data["diff"];
    var columns = [projectName];
    if (project_diff === undefined) {
        return null;
    }
    if (project_diff.error !== undefined) {
        columns.push("Logs not available");
        columns.push("Logs not available");
    } else {
        leftColDiffName = project_diff["leftCol"]["diffName"];
        rightColDiffName = project_diff["rightCol"]["diffName"];
        columns.push(project_diff["results"]["diff"][leftColDiffName]);
        columns.push(project_diff["results"]["diff"][rightColDiffName]);
    }

    var row = document.createElement('tr');
    for (var i = 0; i < columns.length; i++){
        var cell = document.createElement('td');
        cell.innerHTML = '<p>' + columns[i] + '</p>';
        if (i % 3 == 0) {
            cell.setAttribute('class', 'mainTitle');
        } else {
            class_names = 'batchCompareLogData';
            if (shouldColorCode &&
                columns[i].search("All tests passed without errors!") == -1 &&
                columns[i] !== 'Logs not available') {
                class_names = class_names + ' testErr';
            }
            cell.setAttribute('class', class_names);
        }
        cell.setAttribute('colspan', '4');
        cell.setAttribute('style', 'vertical-align:top;');

        row.appendChild(cell);
    }
    return row;
}

function generate_batch_log_compare_header(left_parent_batch, right_parent_batch, left_arch, right_arch) {
    var columns = ["Test/Build Project Name", left_parent_batch + '<br>' + left_arch, right_parent_batch + '<br>' + right_arch];

    var row = document.createElement('tr');
    for (var i = 0; i < columns.length; i++){
        var cell = document.createElement('th');
        cell.setAttribute('class', 'batchCompareLogHeader');
        cell.setAttribute('colspan', '4');
        cell.innerHTML = columns[i];
        row.appendChild(cell);
    }
    return row;
}

function populate_batch_compare_header(jobNames){
    var row = document.createElement('tr');
    for (var i = 0; i < jobNames.length; i++){
        var cell = document.createElement('th');
        cell.setAttribute('class', 'batchCompareHeader');
        cell.setAttribute('colspan', '4');
        var text = document.createTextNode(jobNames[i]);
        cell.appendChild(text);
        row.appendChild(cell);
    }
    return row;
}

function generateTableData(main_table, project_info, table_rows){

    var project_arch = document.createElement('td');
    project_arch.setAttribute('colspan', '2');
    var project_arch_text = document.createTextNode((project_info)?project_info.arch:"Not Available");
    project_arch.appendChild(project_arch_text);
    table_rows[0].appendChild(project_arch);

    var project_version = document.createElement('td');
    project_version.setAttribute('colspan', '2');
    var project_version_text = document.createTextNode((project_info)?project_info.version:"Not Available");
    project_version.appendChild(project_version_text);
    table_rows[0].appendChild(project_version);

    var project_timestamp = document.createElement('td');
    project_timestamp.setAttribute('colspan', '4');
    var project_timestamp_text = document.createTextNode((project_info)?project_info.timestamp:"Not Available");
    project_timestamp.appendChild(project_timestamp_text);
    table_rows[1].appendChild(project_timestamp);

    var project_result_t = document.createElement('td');
    var project_result_f = document.createElement('td');
    var project_result_s = document.createElement('td');
    var project_result_e = document.createElement('td');
    var project_result_t_text = document.createTextNode('T');
    var project_result_f_text = document.createTextNode('F');
    var project_result_e_text = document.createTextNode('E');
    var project_result_s_text = document.createTextNode('S');

    project_result_t.appendChild(project_result_t_text);
    project_result_f.appendChild(project_result_f_text);
    project_result_e.appendChild(project_result_e_text);
    project_result_s.appendChild(project_result_s_text);

    table_rows[2].appendChild(project_result_t);
    table_rows[2].appendChild(project_result_f);
    table_rows[2].appendChild(project_result_e);
    table_rows[2].appendChild(project_result_s);

    // Now Finally add Result data
    if (project_info && project_info.results){
        var project_result_data_t_value = project_info.results.total;
        var project_result_data_f_value = project_info.results.failures;
        var project_result_data_e_value = project_info.results.errors;
        var project_result_data_s_value = project_info.results.skipped;
    }

    var project_result_data_t = document.createElement('td');
    var project_result_data_f = document.createElement('td');
    var project_result_data_s = document.createElement('td');
    var project_result_data_e = document.createElement('td');

    var project_result_data_t_text = document.createTextNode((project_result_data_t_value !== undefined) ? project_result_data_t_value: 0);
    var project_result_data_f_text = document.createTextNode((project_result_data_t_value !== undefined) ? project_result_data_f_value: 0);
    var project_result_data_e_text = document.createTextNode((project_result_data_t_value !== undefined) ? project_result_data_e_value: 0);
    var project_result_data_s_text = document.createTextNode((project_result_data_t_value !== undefined) ? project_result_data_s_value: 0);

    project_result_data_t.appendChild(project_result_data_t_text);
    project_result_data_f.appendChild(project_result_data_f_text);
    project_result_data_e.appendChild(project_result_data_e_text);
    project_result_data_s.appendChild(project_result_data_s_text);

    table_rows[3].appendChild(project_result_data_t);
    table_rows[3].appendChild(project_result_data_f);
    table_rows[3].appendChild(project_result_data_e);
    table_rows[3].appendChild(project_result_data_s);

    main_table.appendChild(table_rows[0]);
    main_table.appendChild(table_rows[1]);
    main_table.appendChild(table_rows[2]);
    main_table.appendChild(table_rows[3]);
}

function populate_batch_compare_data(left_batch, right_batch, main_table){
    var left_job_names = Object.keys(left_batch);
    var right_job_names = Object.keys(right_batch);

    var left_jobs = [];
    var right_jobs = [];

    for (var i = 0; i < left_job_names.length; i++){
        left_jobs.push(left_batch[left_job_names[i]]);
    }

    for (var i = 0; i < left_job_names.length; i++){
        right_jobs.push(right_batch[right_job_names[i]]);
    }

    // Assuming that both batch for comparison should have same set of projects.
    // Hence count of project also will be same. Also every job will have one package.

    for (var i = 0; i < left_jobs.length; i++){
        var table_rows = [
            document.createElement('tr'),
            document.createElement('tr'),
            document.createElement('tr'),
            document.createElement('tr')
        ];

        // Add Project Name as first column.
        var project_name = document.createElement('td');
        project_name.setAttribute('rowspan', '4');
        project_name.setAttribute('colspan', '4');
        project_name.setAttribute('class', 'mainTitle');
        projectName = Object.keys(left_jobs[i]);
        var project_name_text = document.createTextNode(projectName);
        project_name.appendChild(project_name_text);
        table_rows[0].appendChild(project_name);

        generateTableData(main_table, left_jobs[i][projectName], table_rows);
        generateTableData(main_table, right_jobs[i][projectName], table_rows);

        var blank_row = document.createElement('tr');
        var blank_cell = blank_row.insertCell(0);
        blank_cell.setAttribute('colspan', '12');
        blank_cell.innerHTML = "&nbsp;";
        main_table.appendChild(blank_row);
    }
}

/*
 * This function will be called to render Batch job report data.
 */
function processBatchCompareData(data) {
    // Hide listing of Batch jiobs before showing the batch details.
    // Initialize a new blank table holding Batch report data
    var main_table = document.getElementById("testBatchResultsTable");
    main_table.innerHTML = '';
    var data_table = document.createElement('table');
    data_table.setAttribute('border', '1');
    var blank_row = document.createElement('tr');
    var blank_cell = document.createElement('td');
    blank_cell.setAttribute('colspan', '12');
    var blank_text = document.createTextNode('');
    blank_cell.appendChild(blank_text);
    blank_row.appendChild(blank_cell);
    main_table.appendChild(blank_row);
    main_header_data = null;

    // The API returning data should check if both selected Batch Jobs are 2 different runs,
    // of the same Batch else don't show comparison.
    var batchNames = Object.keys(data);

    if (batchNames.length == 2) {
        batchNames.unshift("Test");
        main_table.appendChild(populate_batch_compare_header(batchNames));
        // for each project generate row with data
        populate_batch_compare_data(data[batchNames[1]], data[batchNames[2]], main_table);
    } else {
        showAlert("Error:", "Please select two jobs for comparison");
    }

    // finally append the Batch details table to the placeholder table on UI.
    var tr = document.createElement('tr');
    tr.appendChild(data_table);
    main_table.appendChild(tr);
    var selectedProjects = $('#batchReportListSelectTable').bootstrapTable('getSelections');
    var batchName =  (selectedProjects.length > 0)?selectedProjects[0].batch_name:'';
    $("#batchHeaderPreText").html('Job comparison for Batch "'+ batchName + '": ');
}

function checkIfBuildAndTestLogCreated(log_comparison_type){
    var selectedBatchJobs = $('#batchReportListSelectTable').bootstrapTable('getSelections');
    show_button = true;
    for (var i = 0; i < selectedBatchJobs.length; i++) {
        if (log_comparison_type == 'test' &&
            selectedBatchJobs[i].test_log_count == "Not Available") {
            return false;
        }
        if (log_comparison_type == 'build' &&
            selectedBatchJobs[i].build_log_count == "Not Available") {
            return false;
        }
        if (log_comparison_type === undefined) {
            return !(selectedBatchJobs[i].build_log_count == "Not Available" &&
                     selectedBatchJobs[i].test_log_count == "Not Available");
        }
    }
    return true;
}

function CustomDateSorter(date1, date2){
    var dateObj1 = new Date(date1);
    var dateObj2 = new Date(date2);
    return dateObj1 - dateObj2
}

function populateDropDownsBasedOnLanguage(packageList){
    // wanted to use switch case loop, but not sure how to switch in case of regular expressions hence going
    // with traditional if/else.
    var langKey = '';
    var langVersion = '';
    var supportedLangTypes = {};

    for (var position = 0; position < packageList.length; position++){
        // Get package Tag/name
        if (packageList[position].tag !== undefined) {
            var packageName = packageList[position].tag.toLowerCase();
        } else {
            var packageName = packageList[position].name.toLowerCase();
        }

        if (packageName.startsWith('ibm-sdk-nodejs')) {
            langVersion = (packageList[position].version !== undefined) ? packageList[position].version : 0;
            langKey = 'ibm-sdk-nodejs ' + langVersion;
            detailState.supportedJavaScriptList[langKey] = langVersion;
            detailState.supportedJavaScriptListOptions = Object.keys(detailState.supportedJavaScriptList);
        } else if (packageName.startsWith('ibm-java-sdk') || packageName.startsWith('openjdk')) {
            langKey = 'openjdk';
            langVersion = (packageList[position].version !== undefined)?packageList[position].version.split('.')[0]:7;
            if (packageList[position].name.startsWith('ibm-java-sdk')) {
                langKey = 'ibm-java-sdk' + ' ' + langVersion;
            }else if(packageList[position].name.startsWith('openjdk')) {
                langKey = 'openjdk' + ' ' + langVersion;
            }
            detailState.supportedJavaList[langKey] = langVersion;
            detailState.supportedJavaListOptions = Object.keys(detailState.supportedJavaList);
        }
    }
}

function populateDropdown(data){
    // Assuming Ubuntu and RHEL will have same set of managed packages.
    var managedRuntimePackages = data.results.managedRuntime;
    var supportedLangTypes = {};
    if (managedRuntimePackages && managedRuntimePackages.length > 0) {
        var autoportChefPackages = managedRuntimePackages[0].autoportChefPackages;
        var autoportPackages = managedRuntimePackages[0].autoportPackages;
        detailState.supportedJavaScriptList['nodejs'] = 0; // while initializing of nodejs array set the default values.
        populateDropDownsBasedOnLanguage(autoportPackages);
        populateDropDownsBasedOnLanguage(autoportChefPackages);
    }
}

$(document).ready(function() {
    // NOTE - rivets does not play well with multiselect
    // Query Jenkins for list of build servers
    $.ajax({
        type: 'POST',
        contentType: "application/json; charset=utf-8",
        url: "getJenkinsNodes",
        data: {},
        success: getJenkinsNodesCallback,
        dataType: "json",
        async:true
    });
    //Call to fetch ManagedList.json data which will be used to populate dropdowns.
    $.ajax({
        type: 'GET',
        contentType: "application/json; charset=utf-8",
        url: "getManagedList",
        success: populateDropdown,
        dataType: "json",
        async:true
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
    $('#rpmSelector').multiselect({
        buttonClass: "btn btn-primary",
        buttonText: function(options, select) {
            return "Distro / Release";
        }
    });
    $('#debSelector').multiselect({
        buttonClass: "btn btn-primary",
        buttonText: function(options, select) {
            return "Distro / Release";
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
        toggleBatchStateButtons();
    });
    $('#batchListSelectTable').on('uncheck.bs.table', function (e, row) {
        batchState.selectedBatchFile={};
        toggleBatchStateButtons();
    });
    $('#batchListSelectTable').show(function () {
        toggleBatchStateButtons();
    });
    // Initializes an empty batch Report list/select table
    $('#batchReportListSelectTable').bootstrapTable({
        data: []
    });
    $('#batchReportListSelectTable').on('check.bs.table', function (e, row) {
        batchReportState.selectedBatchFile = row;
        toggleBatchReportButtons();
    });
    $('#batchReportListSelectTable').on('uncheck.bs.table', function (e, row) {
        toggleBatchReportButtons();
    });
    $('#batchReportListSelectTable').show(function () {
        toggleBatchReportButtons();
    });
    // Initializes an empty package list table on the single slave panel
    $('#singleServerPackageListTable').bootstrapTable({
        data: []
    });
    $('#singleServerPackageListTable').on('check.bs.table', function (e, row) {
        jenkinsState.selectedSingleSlavePackage = row;
        var selectedPackages = $('#singleServerPackageListTable').bootstrapTable('getSelections');
        if (selectedPackages.length === 0) {
            $("#singlePanelInstallBtn").addClass("disabled");
            $("#singlePanelRemoveBtn").addClass("disabled");
            jenkinsState.selectedSingleSlavePackage = [];
        }
        else {
            $("#singlePanelInstallBtn").removeClass("disabled");
            $("#singlePanelRemoveBtn").removeClass("disabled");
        }
    });
    $('#singleServerPackageListTable').on('uncheck.bs.table', function (e, row) {
        jenkinsState.selectedSingleSlavePackage = row;
        var selectedPackages = $('#singleServerPackageListTable').bootstrapTable('getSelections');
        if (selectedPackages.length === 0) {
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
        if (selectedPackages.length === 0) {
            $("#singlePanelInstallBtn").addClass("disabled");
            $("#singlePanelRemoveBtn").addClass("disabled");
        }
    });
    // Initializes an empty package list table on the Managed Slave panel
    $('#multiServerPackageListTable').bootstrapTable({
        data: []
    });
    $('#rebootServerListTable').bootstrapTable({
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
        if (selectedPackages.length === 0) {
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
        toggleProjectReportButtons();
    });
    $('#testCompareSelectPanel').on('uncheck.bs.table', function (e, row) {
        toggleProjectReportButtons();
    });
    $('#testCompareSelectPanel').show(function() {
        toggleProjectReportButtons();
    });
});

$.fn.extend({
    treed: function (o) {

        var openedClass = 'glyphicon-minus-sign';
        var closedClass = 'glyphicon-plus-sign';
        if (typeof o != 'undefined') {
            if (typeof o.openedClass != 'undefined') {
                openedClass = o.openedClass;
            }
            if (typeof o.closedClass != 'undefined') {
                closedClass = o.closedClass;
            }
        };

        //initialize each of the top levels
        var tree = $(this);
        tree.addClass("tree");
        tree.find('i').remove();

        tree.find('li').has("ul").each(function () {
            var branch = $(this); //li with children ul
            branch.prepend("<i class='indicator glyphicon " + closedClass + "'></i>");
            branch.addClass('branch');
            branch.unbind( "click" );
            branch.on('click', function (e) {
                if (this == e.target) {
                    var icon = $(this).children('i:first');
                    icon.toggleClass(openedClass + " " + closedClass);
                    $(this).children().children().toggle();
                }
            });
            branch.children().children().hide();
        });

        // fire event from the dynamically added icon
        tree.find('.branch .indicator').each(function(){
            $(this).on('click', function () {
                $(this).closest('li').click();
            });
        });

        // fire event to open branch if the li contains an anchor instead of text
        tree.find('.branch>a').each(function () {
            $(this).on('click', function (e) {
                $(this).closest('li').click();
                e.preventDefault();
            });
        });

        // fire event to open branch if the li contains a button instead of text
        tree.find('.branch>button').each(function () {
            $(this).on('click', function (e) {
                $(this).closest('li').click();
                e.preventDefault();
            });
        });
    }
});

