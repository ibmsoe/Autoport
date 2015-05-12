#!/usr/bin/env python

# Importing globals and initializing them is the top priority
import globals
globals.init()

# Imports
import xml.etree.ElementTree as ET
import requests
import argparse
import datetime
import os
import re
import threading
import paramiko
from threadpool import makeRequests
from time import gmtime, strftime, sleep
from flask import Flask, request, render_template, json
from classifiers import classify
from buildAnalyzer import inferBuildSteps
from status import determineProgress
from tags import getTags
from catalog import Catalog
from resultParser import ResultParser
from urlparse import urlparse
from batch import Batch
from random import randint

app = Flask(__name__)

maxResults = 10
resParser = ResultParser()

catalog = Catalog(globals.hostname, urlparse(globals.jenkinsUrl).hostname)
batch = Batch()

# Be sure to update main.js also.
#
# job result sample "hostname.181259.x86-ubuntu-14.04.junit.current.2015-04-24-h12-m23-s15/"
# job result sample "hostname.887140.229_x86_ubuntu14.junit.current.2015-04-24-h12-m23-s12/"
# job result sample "hostname.984127.ppcle-ubuntu-14.04.junit.current.2015-04-24-h12-m23-s05/"
# pattern           "hostname.uid   .node              .name .tag    .time stamp
#                                    ^                  ^     ^
#                                    |                  +-----+-- may have - or _
#                                    +-- may have a - or _ or .
#
# We delimit with . and we prefix project name with N-.  This becomes :
#
# job result sample "hostname.984127.ppcle-ubuntu-14.04.N-junit.current.2015-04-24_12-23-05/"
#
resultPattern = re.compile('(.*?)\.(.*?)\.(.*?)\.N-(.*?)\.(.*?)\.(\d\d\d\d-\d\d-\d\d-h\d\d-m\d\d-s\d\d)')

# Main page - just serve up main.html
@app.route("/")
def main():
    return render_template("main.html")

@app.route("/init", methods=['POST'])
def init():
    return json.jsonify(status="ok", jenkinsUrl=globals.jenkinsUrl, localPathForTestResults=globals.localPathForTestResults, pathForTestResults=globals.pathForTestResults, localPathForBatchFiles=globals.localPathForBatchFiles, pathForBatchFiles=globals.pathForBatchFiles, githubToken=globals.githubToken, configUsername=globals.configUsername, configPassword=globals.configPassword)

#TODO - add error checking
@app.route("/getJenkinsNodes", methods=["POST"])
def getJenkinsNodes():
    nodesUrl = globals.jenkinsUrl + "/computer/api/json?pretty=true"

    try:
        nodesResults = json.loads(requests.get(nodesUrl).text)
        nodes = nodesResults['computer']
    except ValueError:
        return json.jsonify(status="failure", error="Jenkins nodes url or authentication error"), 400

    nodeNames = []
    nodeLabels = []

    for node in nodes:
        if not node['offline']:
            name = node['displayName']
            if name != "master":
                nodeNames.append(name)
                root = ET.fromstring(requests.get(globals.jenkinsUrl +
                    "/computer/" + name + "/config.xml").text)
                nodeLabels.append(root.find("./label").text)

    return json.jsonify(status="ok", nodeNames=nodeNames, nodeLabels=nodeLabels)

# Settings function
@app.route("/settings", methods=['POST'])
def settings():
    try:
        globals.jenkinsUrl = request.form["url"]
    except ValueError:
        return json.jsonify(status="failure", error="bad url"), 400

    try:
        globals.localPathForTestResults = request.form["ltest_results"]
    except ValueError:
        return json.jsonify(status="failure", error="bad local_test_results path"), 400

    try:
        globals.pathForTestResults = request.form["gtest_results"]
    except ValueError:
        return json.jsonify(status="failure", error="bad test_results path"), 400

    try:
        globals.localPathForBatchFiles = request.form["lbatch_files"]
    except ValueError:
        return json.jsonify(status="failure", error="bad local_batch_files path"), 400

    try:
        globals.pathForBatchFiles = request.form["gbatch_files"]
    except ValueError:
        return json.jsonify(status="failure", error="bad batch_files path"), 400

    try:
        # change githubToken from default, doesn't actually work right now
        globals.githubToken = request.form["github"]
        # globals.github = Github(githubToken)
        # globals.cache = Cache(github)
    except ValueError:
        return json.jsonify(status="failure", error="bad github token"), 400

    try:
        globals.configUsername = request.form["username"]
    except ValueError:
        return json.jsonify(status="failure", error="bad configuration username"), 400

    try:
        globals.configPassword = request.form["password"]
    except ValueError:
        return json.jsonify(status="failure", error="bad configuration password"), 400

    return json.jsonify(status="ok")

@app.route("/progress")
def progress():
    results = determineProgress()
    return json.jsonify(status="ok", results=results)

# Search - return a JSON file with search results or the matched
# repo if there's a solid candidate
@app.route("/search")
def search():
    # Get and validate arguments
    query = request.args.get("q", "")
    panel = request.args.get("panel", "")

    if query == "":
        return json.jsonify(status="failure", error="missing query"), 400
    
    if panel == "":
        return json.jsonify(status="failure", error="missing panel"), 400

    searchArgs = None # Used to pass in sort argument to pygithub
    sort = request.args.get("sort", "") # Check for optional sort argument
    if sort in ['forks', 'updated']:
        searchArgs = {'sort': sort}
    elif sort == 'popularity stars':
        searchArgs = {'sort': "stars"}
    elif sort == 'relevance' or sort == '':
        # Must pass no argument if we want to sort by relevance
        searchArgs = {}
    else:
        return json.jsonify(status="failure", error="bad sort type"), 400

    autoselect = request.args.get("auto", "")
    if autoselect != "false":
        autoselect = True
    else:
        autoselect = False

    # Query Github and return a JSON file with results
    results = []
    isFirst = True
    numResults = maxResults
    repos = None

    try:
        repos = globals.github.search_repositories(query, **searchArgs)
    except IOError as e:
        return json.jsonify(status="failure", error="Could not contact github: " + str(e)), 503

    if repos.totalCount == 0:
        # TODO - return no results page
        return json.jsonify(status="failure", error="no results"), 418
    elif repos.totalCount <= maxResults:
        numResults = repos.totalCount

    for repo in repos[:numResults]: 
        globals.cache.cacheRepo(repo)
        # If this is the top hit, and the name matches exactly, and
        # it has greater than 500 stars, then just assume that's the
        # repo the user is looking for
        if autoselect and isFirst and repo.name == query and repo.stargazers_count > 500:
            return detail(repo.id, repo)
        isFirst = False
        # Otherwise add the repo to the list of results and move on
        results.append({
            "id": repo.id,
            "name": repo.name,
            "owner": repo.owner.login,
            "owner_url": repo.owner.html_url,
            "stars": repo.stargazers_count,
            "forks": repo.forks_count,
            "url": repo.html_url,
            "size_kb": repo.size,
            "last_update": str(repo.updated_at),
            "language": repo.language,
            "description": repo.description,
            "classifications": classify(repo)
        })
    return json.jsonify(status="ok", results=results, type="multiple", panel=panel)

# Detail - returns a JSON file with detailed information about the repo
@app.route("/detail/<int:id>")
def detail(id, repo=None):
    panel = request.args.get("panel", "")

    if panel == "":
        return json.jsonify(status="failure", error="missing panel"), 400

    # Get the repo if it wasn't passed in (from Search auto picking one)
    if repo is None:
        try:
            idInt = int(id)
        except ValueError:
            return json.jsonify(status="failure", error="bad id"), 400
        repo = globals.cache.getRepo(id)
    # Get language data
    languages = globals.cache.getLang(repo)
    # Transform so it's ready to graph on client side
    colorDataFile = open('language_colors.json')
    colorData = json.load(colorDataFile)
    colorDataFile.close()
    transformed_languages = []
    for label, value in languages.items():
        color = "#DDDDDD" # default color
        if label in colorData:
            color = colorData[label]
        transformed_languages.append({
            'title': label, # Language name (e.g. C++)
            'value': value, # Size in bytes
            'color': color  # Hexadecimal color value
        })

    # Look for certain files to figure out how to build
    build = inferBuildSteps(globals.cache.getDir(repo), repo) # buildAnalyzer.py

    # Ignore errors related to build commands.  Need to show detailed project info
    
    # Collect data

    # Get tag-related data
    tags, recentTag = getTags(repo)

    repoData = {
        "id": repo.id,
        "name": repo.name,
        "owner": repo.owner.login,
        "owner_url": repo.owner.html_url,
        "stars": repo.stargazers_count,
        "forks": repo.forks_count,
        "url": repo.html_url,
        "size_kb": repo.size,
        "last_update": str(repo.updated_at),
        "language": repo.language,
        "languages": transformed_languages,
        "description": repo.description,
        "classifications": classify(repo),
        "build": build,
        "recentTag": recentTag,
        "tags": tags,
        "useVersion": "Current"
    }
    # Send
    return json.jsonify(status="ok", repo=repoData, type="detail", panel=panel)

# Search repositories - return JSON search results for the GitHub
# /search/repositories API call. See the following for details:
#   https://developer.github.com/v3/search/
@app.route("/search/repositories")
def search_repositories():
    # GitHub API parameters
    q     = request.args.get("q",     "")
    sort  = request.args.get("sort",  "stars")
    order = request.args.get("order", "desc")

    # AutoPort parameters
    limit = int(request.args.get("limit", "25"))
    panel = request.args.get("panel", "")

    if panel == "":
        return json.jsonify(status="failure", error="missing panel"), 400

    # This algorithm must be fast as it is used to collect information on potentially
    # thousands of projects.  Number of projects is a user specified field.  Don't look
    # detailed information as this search is used to perform discovery of popular
    # projects for research purposes, not necessarily to build.  We defer the build
    # lookup to when the batch file is submitted for build and test.   This is also
    # as the build information for current may change over time.  ie. ant to maven
    results = []
    for repo in globals.github.search_repositories(q, sort=sort, order=order)[:limit]:
        globals.cache.cacheRepo(repo)
        results.append({
            "id": repo.id,
            "name": repo.name,
            "owner": repo.owner.login,
            "owner_url": repo.owner.html_url,
            "stars": repo.stargazers_count,
            "forks": repo.forks_count,
            "url": repo.html_url,
            "size_kb": repo.size,
            "last_update": str(repo.updated_at),
            "language": repo.language,
            "description": repo.description,
            "classifications": classify(repo)
        })

    return json.jsonify(status="ok", results=results, type="multiple", panel=panel)

# Upload Batch File - takes a file and uploads it to a permanent location (TBD)
@app.route("/uploadBatchFile", methods=['GET', 'POST'])
def uploadBatchFile():
    try:
        name = request.form["name"]
    except KeyError:
        return json.jsonify(status="failure", error="missing file"), 400

    try:
        fileStr = request.form["file"]
    except KeyError:
        return json.jsonify(status="failure", error="missing file"), 400

    if not os.path.exists(globals.localPathForBatchFiles):
        os.makedirs(globals.localPathForBatchFiles)

    # TODO - Fix timestamp.  Format wrong
    # Contruct time so that it works on windows.  No colons allowed
    time = strftime("%Y-%m-%d-h%H-m%M-s%S", gmtime())

    if name == "":
        name = "batch_file"

    name = name + "." + time 
    openPath = globals.localPathForBatchFiles + name

    f = open(openPath, "wb")
    f.write(fileStr)
    f.close()

    # We don't want to automatically be uploading to remote location, this code needs
    # to be moved into the batch table as an action for each individual batch file
    '''
    # Copy batch file to a predetermined spot in the GSA 
    # This portion of code requires paramiko installed.
    port = 22
    localpath = os.getcwd() + "/data/batch_files/" + name
    
    # Unfortunately, this will not create a folder that is not already in the gsa.
    # Having stfp trying to create a folder with the same name everytime does not work either.
    remotepath = globals.pathForBatchFiles + name

    transport = None
    try:
        transport = paramiko.Transport((globals.hostname, port))
        transport.connect(username=globals.configUsername, password=globals.configPassword)
    except paramiko.AuthenticationException:
        return json.jsonify(status="failure", error="Authentication Failed")

    sftp = paramiko.SFTPClient.from_transport(transport)
    sftp.put(localpath, remotepath)
    sftp.close()
    transport.close()
    '''

    return json.jsonify(status="ok")

# Common routine for createJob and runBatchJob
def createJob_common(uid, id, tag, node, javaType,
                     selectedBuild, selectedTest, selectedEnv, artifacts):

    # Get repository
    repo = globals.cache.getRepo(id)

    # TODO: Conditionally continue based on a user interface selection to create
    # job on Jenkins w/o a build command.  User must manually enter command on Jenkins.
    # Helps automate porting environment

    if not selectedBuild:
        errorstr = "Programming language not supported - " + repo.language
        return { 'status': "failure", 'error': errorstr }

    # Read template XML file
    tree = ET.parse("config_template.xml")
    root = tree.getroot()
    # Find elements we want to modify
    xml_github_url = root.find("./properties/com.coravy.hudson.plugins.github.GithubProjectProperty/projectUrl")
    xml_git_url = root.find("./scm/userRemoteConfigs/hudson.plugins.git.UserRemoteConfig/url")
    xml_default_branch = root.find("./scm/branches/hudson.plugins.git.BranchSpec/name")
    xml_build_command = root.find("./builders/hudson.tasks.Shell/command")
    xml_test_command = root.find("./builders/org.jenkinsci.plugins.conditionalbuildstep.singlestep.SingleConditionalBuilder/buildStep/command")
    xml_env_command = root.find("./buildWrappers/EnvInjectBuildWrapper/info/propertiesContent")
    xml_artifacts = root.find("./publishers/hudson.tasks.ArtifactArchiver/artifacts")
    xml_node = root.find("./assignedNode")
    xml_parameters = root.findall("./properties/hudson.model.ParametersDefinitionProperty/parameterDefinitions/hudson.model.StringParameterDefinition/defaultValue")

    # Modify selected elements
    xml_node.text = node

    xml_github_url.text = repo.html_url
    xml_git_url.text = "https" + repo.git_url[3:]

    jobName = globals.localHostName + '.' + str(uid) + '.' + node + '.N-' + repo.name

    if (tag == "") or (tag == "Current"):
        xml_default_branch.text = "*/" + repo.default_branch
        jobName += ".current"
    else:
        xml_default_branch.text = "tags/" + tag
        jobName += "." + tag

    # Time job is created
    time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

    # Name of new Folder
    jobFolder = jobName + "." + time

    xml_build_command.text = selectedBuild
    xml_test_command.text = selectedTest
    xml_env_command.text = selectedEnv

    # In addition to whatever other environmental variables I need to inject
    # I should add whether to pick IBM Java or Open JDK
    xml_env_command.text += javaType + "\n"
    path_env = "PATH=" + globals.mavenPath + ":$PATH\n"
    xml_env_command.text += path_env
    xml_artifacts.text = artifacts

    # Job metadata as passed to jenkins
    jobMetadataName = "meta.arti"
    jobMetadata = "{ \"Package\": \"" + jobName + "\", \"Version\": \"" + tag + "\", \"Architecture\": \"" + node + "\", \"Environment\": \"" + xml_env_command.text + "\", \"Date\": \"" + time + "\"}"

    # add parameters information
    i = 1
    for param in xml_parameters:
        if i == 1:
            param.text = jobMetadataName
        elif i == 2:
            param.text = jobMetadata
        i += 1

    # Add header to the config
    configXml = "<?xml version='1.0' encoding='UTF-8'?>\n" + ET.tostring(root)

    # Send to Jenkins
    NO_PROXY = {
        'no': 'pass',
    }

    r = requests.post(
        globals.jenkinsUrl + "/createItem",
        headers={
            'Content-Type': 'application/xml'
        },
        params={
            'name': jobName
        },
        data=configXml,
        proxies=NO_PROXY
    )

    if r.status_code == 200:

        # Success, send the jenkins job and start it right away.
        startJobUrl = globals.jenkinsUrl + "/job/" + jobName + "/buildWithParameters?" + "delay=0sec"

        # But then redirect to job home to monitor job progress.
        homeJobUrl = globals.jenkinsUrl + "/job/" + jobName + "/"

        # Start Jenkins job
        requests.get(startJobUrl, proxies=NO_PROXY)

        # Split off a thread to query for build completion and move artifacts to local machine
        threadRequests = makeRequests(moveArtifacts, (jobName, ))
        [globals.threadPool.putRequest(req) for req in threadRequests]

        # Stays on the same page, after creating a new jenkins job.
        return { 'status':"ok", 'sjobUrl':startJobUrl, 'hjobUrl':homeJobUrl }

    if r.status_code == 400:
        return { 'status':"failure", 'error':"jenkins HTTP error job exists : " + jobName, 'rstatus':r.status_code }

    return { 'status':"failure", 'error':"jenkins HTTP error " + str(r.status_code), 'rstatus':r.status_code }


# Create Job - takes a repo id, repo tag, and build node and creates a Jenkins job for it
# Opens a new tab with a new jenkins job URL on the client side on success,
# while the current tab stays in the same place.
# TODO - If job is started through batch file can't select options currently
@app.route("/createJob", methods=['GET', 'POST'])
def createJob(i_id = None,
              i_tag = None,
              i_node = None,
              i_javaType = None,
              i_selectedBuild = None,
              i_selectedTest = None,
              i_selectedEnv = None,
              i_artifacts = None):

    # Randomly generate a job UID to append to the job name to guarantee uniqueness across jobs.
    # If a job already has the same hostname and UID, we will keep regenerating UIDs until a unique one 
    # is found. This should be an extremely rare occurence.
    # TODO - check to see if job already exists
    uid = randint(globals.minRandom, globals.maxRandom)

    # Ensure we have a valid id number as a post argument
    try:
        idStr = request.form["id"]
        try:
            id = int(idStr)
        except ValueError:
            return json.jsonify(status="failure", error="invalid id number"), 400

    except KeyError:
        if i_id != None:
            id = i_id
        else:
            return json.jsonify(status="failure", error="missing repo id"), 400

    # Ensure we have a valid build node as a post argument
    try:
        node = request.form["node"]
    except KeyError:
        if i_node != None:
            node = i_node
        else:
            return json.jsonify(status="failure", error="missing build node"), 400

    # Check to see if we have a valid tag number as a post argument    
    try:
        tag = request.form["tag"]
    except KeyError:
        if i_tag != None:
            tag = i_tag
        else:
            tag = "Current"
        
    # Get javaType
    try:
        javaType = request.form["javaType"]
    # defaults to open JDK
    except KeyError:
        if i_javaType != None:
            javaType = i_javaType
        else:
            return json.jsonify(status="failure", error="missing java type"), 400

    # Get build info
    try:
        selectedBuild = request.form["selectedBuild"]
    except KeyError:
        if i_selectedBuild != None:
            selectedBuild = i_selectedBuild
        else:
            return json.jsonify(status="failure", error="missing selected build command"), 400
    
    # Get test info
    try:
        selectedTest = request.form["selectedTest"]
    except KeyError:
        if i_selectedTest != None:
            selectedTest = i_selectedTest
        else:
            return json.jsonify(status="failure", error="missing selected test command"), 400
    
    # Get environment info
    try:
        selectedEnv = request.form["selectedEnv"]
    except KeyError:
        if i_selectedEnv != None:
            selectedEnv = i_selectedEnv
        else:
            return json.jsonify(status="failure", error="missing selected env command"), 400

    # Get artifacts info
    try:
        artifacts = request.form["artifacts"]
    except KeyError:
        if i_artifacts != None:
            artifacts = i_artifacts
        else:
            return json.jsonify(status="failure", error="missing artifacts"), 400

    rc = createJob_common(uid, id, tag, node, javaType, selectedBuild, selectedTest, selectedEnv, artifacts)

    try:
        rcstatus = rc['status']
        rcerror = rc['error']
        try:
            return json.jsonify(status=rcstatus, error=rcerror), rc['rstatus']
        except KeyError:
            return json.jsonify(status=rcstatus, error=rcerror)
    except KeyError:
        # Stays on the same page, after creating a new jenkins job.
        # return json.jsonify(status="ok", rc.sjobUrl=startJobUrl, rc.hjobUrl=homeJobUrl)
        return json.jsonify(status="ok", sjobUrl=rc['sjobUrl'], hjobUrl=rc['hjobUrl'])


# Polls the Jenkins master to see when a job has completed and moves artifacts over to local
# storage once/if they are available
def moveArtifacts (jobName):
    checkBuildUrl = globals.jenkinsUrl + "/job/" + jobName + "/lastBuild/api/json"
    building = True

    # poll until job stops building
    while building:
        sleep(10)
        try:
            buildInfo = json.loads(requests.get(checkBuildUrl).text)
            building = buildInfo['building']
        # check to make sure build isn't queued, if it is wait for it to dequeue
        except ValueError:
            checkQueueUrl = globals.jenkinsUrl + "/job/" + jobName + "/api/json"
            queued = True

            count = 0;
            while queued and count < 20:
                sleep(10)
                try:
                    r = requests.get(checkQueueUrl).text
                    projectInfo = json.loads(r)
                    inQueue = projectInfo['inQueue']
                # if it's not in the queue and not building something went wrong
                except ValueError:
                    print "project failed to start building/queuing" + jobName
                count += 1
            building = False

    # grab the build artifacts through ftp if build was successful
    artifactsPath = globals.artifactsPathPrefix + jobName + "/builds/"

    try:
        # just incase build finished but artifacts haven't moved over yet due to network
        sleep(10)

        # create an FTP connection to Jenkins
        sshClient = paramiko.SSHClient()
        sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        sshClient.connect(urlparse(globals.jenkinsUrl).hostname, username=globals.configJenkinsUsername, key_filename=globals.configJenkinsKey)
        ftpClient = sshClient.open_sftp()

        ftpClient.chdir(artifactsPath)
        flist = ftpClient.listdir()

        # 1 is a sym link to the first build for that job.
        # If we delete each job after each run, we only care about this first build.
        # Else we need to parse nextBuildNumber in the parent directory to get build number.
        if "1" in flist:
            artifactsPath = artifactsPath + "1/"
            ftpClient.chdir(artifactsPath)
            flist = ftpClient.listdir()

            if "archive" in flist:
                artifactsPath = artifactsPath + "archive/"
                ftpClient.chdir(artifactsPath)
            
                # Contruct time so that it works on windows.  No colons allowed
                time = strftime("%Y-%m-%d-h%H-m%M-s%S", gmtime())

                localArtifactsPath = globals.localPathForTestResults + jobName + "." + time + "/"
                os.mkdir(localArtifactsPath)
                
                flist = ftpClient.listdir()
 
                for f in flist:
                    ftpClient.get(f, localArtifactsPath + f)

            else:
                print "archive folder missing " + jobName

    except IOError as e:
        print "archive move FTP failure" + jobName + " error: " + e

# Run Batch File - takes a batch file name and runs it
# TODO - fix to provide support for multiple build servers instead of just x86 vs ppcle
@app.route("/runBatchFile", methods=["GET", "POST"])
def runBatchFile ():
    # Get the batch file name from POST
    try:
        batchName = request.form["batchName"]
    except KeyError:
        return json.jsonify(status="failure", error="missing batchName POST argument"), 400

    # Get the batch file name from POST
    try:
        node = request.form["node"]
    except KeyError:
        return json.jsonify(status="failure", error="run batch file missing node argument"), 400

    if batchName != "":
        results = batch.parseBatchFile(batchName)
        try:
            fileBuf = results['fileBuf']
        except KeyError:
            return json.jsonify(status="failure", error=fileBuf['error']), 400

        # Randomly generate a batch job UID to append to the job name to provide a grouping
        # for all jobs in the batch file for reporting purposes.
        uid = randint(globals.minRandom, globals.maxRandom)

        # Parse config data
        javaType = ""
        if fileBuf['config']['java'] == "ibm":
            javaType = "JAVA_HOME=/opt/ibm/java"

        # Parse package data
        submittedJob = False
        for package in fileBuf['packages']:

            # if a project can't be built, skip it. Top N may not be buildable - documentation
            selectedBuild = package['build']['selectedBuild']
            if selectedBuild == "":
                continue

            createJob_common(uid,
                      package['id'],
                      package['tag'],
                      node,
                      javaType,
                      package['build']['selectedBuild'],
                      package['build']['selectedTest'],
                      package['build']['selectedEnv'],
                      package['build']['artifacts'])
            submittedJob = True
    else:
        return json.jsonify(status="failure", error="could not find batch file"), 404

    if submittedJob:
        return json.jsonify(status="ok")
    return json.jsonify(status="failure", error="batch file no project is buildable"), 404


# List available batch files
@app.route("/listBatchFiles/<repositoryType>")
def listBatchFiles(repositoryType):
    filt = request.args.get("filter", "")
    if repositoryType != "gsa" and repositoryType != "local" and repositoryType != "all":
        return json.jsonify(status="failure", error="Invalid repository type"), 400
    return json.jsonify(status="ok", results=batch.listBatchFiles(repositoryType, filt.lower()))

# Read and sanitize the contents of the named batch file
@app.route("/parseBatchFile")
def parseBatchFile():
    batchName  = request.args.get("batchName", "")
    if batchName == "":
        return json.jsonify(status="failure", error="missing batch file name"), 400
    results = batch.parseBatchFile(batchName)
    try:
        return json.jsonify(status="failure", error=results['error']), 404
    except KeyError:
        return json.jsonify(status="ok", results=results['fileBuf'])

# List all results available on catalog
#TODO - list builds as failed and disable test detail
@app.route("/listTestResults/<repositoryType>")
def listTestResults(repositoryType):
    filt = request.args.get("filter", "")
    if repositoryType != "gsa" and repositoryType != "local" and repositoryType != "all":
        return json.jsonify(status="failure", error="Invalid repository type"), 400
    return json.jsonify(status="ok", results=catalog.listJobResults(repositoryType, filt.lower()))

# Get the jenkins build output
# /getBuildResults?left=x&right=y
@app.route("/getTestResults")
def getTestResults():
    leftbuild  = request.args.get("leftbuild", "")
    rightbuild = request.args.get("rightbuild", "")
    leftrepo = request.args.get("leftrepository", "local")
    rightrepo = request.args.get("rightrepository", "local")
    
    if (leftbuild == "" or rightbuild == ""):
        return json.jsonify(status="failure", error="invalid argument"), 400
    
    leftdir = catalog.getResults(leftbuild, leftrepo)
    rightdir = catalog.getResults(rightbuild, rightrepo)
    
    if (leftdir == None or rightdir == None):
        return json.jsonify(status="failure", error="result not found"), 404
    
    leftname = resultPattern.match(leftbuild).group(2)
    rightname = resultPattern.match(rightbuild).group(2)

    try:
        res = resParser.MavenBuildCompare(leftname, leftdir+"/test_result.arti",
                                          rightname, rightdir+"/test_result.arti")
    except BaseException as e:
        return json.jsonify(status="failure", error=str(e)), 500

    lf = open(leftdir+"/meta.arti")
    rf = open(rightdir+"/meta.arti")
    leftmeta = json.load(lf)
    rightmeta = json.load(rf)
    lf.close()
    rf.close()

    catalog.cleanTmp()
    return json.jsonify(status = "ok",
                        leftCol = leftname,
                        rightCol = rightname,
                        leftProject = leftmeta,
                        rightProject = rightmeta,
                        results = res)

@app.route("/getTestHistory", methods=["POST"])
def getTestHistory():
    projects = request.json['projects']
    out = []
    repoType = ""
    projectNames = []
    for name in projects.keys():
        if repoType == "":
            repoType = projects[name]
        elif repoType == "all":
            pass
        elif repoType != projects[name]:
            repoType = "all"
        # remove time and platform from the project name
        pres = resultPattern.match(name)
        if not [pres.group(1),pres.group(3)] in projectNames:
            projectNames.append([pres.group(1),pres.group(3)])

    jobRes = catalog.listJobResults(repoType, "")
    for projectName in projectNames:
        prjOut = []
        for prj in jobRes:
            if projectName[0] in prj[0] and projectName[1] in prj[0]:
                resultDir = catalog.getResults(prj[0], prj[1])
                try:
                    if(os.path.isfile(resultDir+"/test_result.arti")):
                        prjRes = resParser.MavenBuildSummary(resultDir+"/test_result.arti")
                    else:
                        return json.jsonify(status="failure", error="build failed, no test results"), 500
                except BaseException as e:
                    return json.jsonify(status="failure", error=str(e)), 500
                f = open(resultDir+"/meta.arti")
                meta = json.load(f)
                f.close()
                prjOut.append({
                    "name": prj[0],
                    "repository": prj[1],
                    "project": meta,
                    "results": prjRes})
        out.append({
            "name": projectName[0]+" - "+projectName[1],
            "results": prjOut
        })
    return json.jsonify(status = "ok", results = out)

@app.route("/getTestDetail", methods=["POST"])
def getTestDetail():
    projects = request.json['projects']
    out = []
    for projectName in projects:
        repo = projects[projectName]
        resultDir = catalog.getResults(projectName, repo)
        try:
            if(os.path.isfile(resultDir+"/test_result.arti")):
                res = resParser.MavenBuildSummary(resultDir+"/test_result.arti")
            else:
                return json.jsonify(status="failure", error="build failed, no test results"), 500
        except BaseException as e:
            return json.jsonify(status="failure", error=str(e)), 500
        f = open(resultDir+"/meta.arti")
        meta = json.load(f)
        f.close()
        out.append({ "results": res, "project": meta, "repository": repo })
    return json.jsonify(status = "ok", results = out)

@app.route("/archiveProjects", methods=["POST"])
def archiveProjects():
    projects = request.json['projects']
    errors, alreadyThere = catalog.archiveResults(projects)
    return json.jsonify(status="ok", errors=errors, alreadyThere=alreadyThere)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("-p", "--public",               action="store_true", help="specifies for the web server to listen over the public network, defaults to only listening on private localhost")
    p.add_argument("-u", "--jenkinsURL",                                help="specifies the URL for the Jenkins server, defaults to '" + globals.jenkinsUrl + "'")
    args = p.parse_args()

    if args.jenkinsURL:
        globals.jenkinsUrl = args.jenkinsURL

    if args.public:
        app.run(debug = True, host='0.0.0.0')
    else:
        app.run(debug = True)
