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
import ntpath
from sharedData import SharedData
from chefData import ChefData
from threadpool import makeRequests
from time import localtime, strftime, sleep
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
from github import GithubException
from distutils.version import LooseVersion

app = Flask(__name__)

maxResults = 10
resParser = ResultParser()

catalog = Catalog(globals.hostname, urlparse(globals.jenkinsUrl).hostname)
sharedData = SharedData(urlparse(globals.jenkinsUrl).hostname)
chefData = ChefData(urlparse(globals.jenkinsUrl).hostname)
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

    # Empty the global lists
    del globals.nodeNames[:]
    del globals.nodeLabels[:]

    try:
        nodesResults = json.loads(requests.get(nodesUrl).text)
        nodes = nodesResults['computer']
    except ValueError:
        return json.jsonify(status="failure", error="Jenkins nodes url or authentication error"), 400

    for node in nodes:
        if not node['offline']:
            name = node['displayName']
            if name != "master":
                globals.nodeNames.append(name)
                root = ET.fromstring(requests.get(globals.jenkinsUrl +
                    "/computer/" + name + "/config.xml").text)
                globals.nodeLabels.append(root.find("./label").text)

    return json.jsonify(status="ok", nodeNames=globals.nodeNames, nodeLabels=globals.nodeLabels)

# Get O/S details for build servers including distribution, release, version, hostname, ...
# Don't fail as a lot of func is still possible.  Nodes may go offline at any time.
# TODO - Run with threads in parallel synchronously as caller requires data

@app.route("/getJenkinsNodeDetails", methods=["POST"])
def getJenkinsNodeDetails():
    action = "query-os"

    # Empty the global lists
    del globals.nodeDetails[:]
    del globals.nodeUbuntu[:]
    del globals.nodeRHEL[:]

    for node in globals.nodeLabels:
        results = queryNode(node, action)
        try:
            detail = results['detail']
            globals.nodeDetails.append(detail)
            nodeLabel = detail['nodelabel']
            if detail['distro'] == "UBUNTU":
                globals.nodeUbuntu.append(nodeLabel)
            elif detail['distro'] == "RHEL":
                globals.nodeRHEL.append(nodeLabel)
        except KeyError:
            print "No O/S information for node " + node
            pass

    print "All nodes: ", globals.nodeLabels
    print "Ubuntu nodes: ", globals.nodeUbuntu
    print "RHEL nodes: ", globals.nodeRHEL

    return json.jsonify(status="ok", details=globals.nodeDetails, ubuntu=globals.nodeUbuntu, rhel=globals.nodeRHEL)

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
    try:
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
    except GithubException as e:
        return json.jsonify(status="failure",
                 error="GithubException ({0}): {1}".format(e.status, e.data['message'])), 400

# Upload Batch File - takes a file and uploads it to a permanent location (TBD)
@app.route("/uploadBatchFile", methods=['GET', 'POST'])
def uploadBatchFile():
    try:
        name = request.form["name"]
    except KeyError:
        return json.jsonify(status="failure", error="missing file name"), 400

    try:
        fileStr = request.form["file"]
    except KeyError:
        return json.jsonify(status="failure", error="missing file"), 404

    if not os.path.exists(globals.localPathForBatchFiles):
        os.makedirs(globals.localPathForBatchFiles)

    # Contruct time so that it works on windows.  No colons allowed
    time = strftime("%Y-%m-%d-h%H-m%M-s%S", localtime())

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
# TODO - added buildSystem = "NA" for batch jobs, need to add buildSystem to batch files
def createJob_common(time, uid, id, tag, node, javaType,
                     selectedBuild, selectedTest, selectedEnv, artifacts, buildSystem = "NA"):

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

    # Time job is created.  Parameter to Jenkins.  Blanks allowed
    timestr = strftime("%Y-%m-%d %H:%M:%S", time)

    # Name of jenkins new Folder
    jobFolder = jobName + "." + timestr

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
    jobMetadata = "{ \"Package\": \"" + jobName + "\", \"Version\": \"" + tag + "\", \"Build System\":\"" + buildSystem + "\", \"Architecture\": \"" + node + "\", \"Environment\": \"" + xml_env_command.text + "\", \"Date\": \"" + timestr + "\"}"

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

        # local directory for build artifacts.  No colons allowed for windows compatibility
        timestr = strftime("%Y-%m-%d-h%H-m%M-s%S", time)
        artifactFolder = jobName + "." + timestr

        # Split off a thread to query for build completion and move artifacts to local machine
        args = [((jobName, globals.localPathForTestResults, timestr), {})]
        threadRequests = makeRequests(moveArtifacts, args)
        [globals.threadPool.putRequest(req) for req in threadRequests]

        # Stays on the same page, after creating a new jenkins job.
        return { 'status':"ok", 'sjobUrl':startJobUrl, 'hjobUrl':homeJobUrl,
                 'jobFolder':jobFolder, 'artifactFolder': artifactFolder }

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
              i_artifacts = None,
              i_buildSystem = None):

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

    # Get artifacts info
    try:
        buildSystem = request.form["buildSystem"]
    except KeyError:
        if i_buildSystem != None:
            buildSystem = i_buildSystem
        else:
            return json.jsonify(status="failure", error="missing build system"), 400

    rc = createJob_common(localtime(), uid, id, tag, node, javaType, selectedBuild,
                          selectedTest, selectedEnv, artifacts, buildSystem)

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
def moveArtifacts(jobName, localBaseDir, time):

    outDir = ""
    checkBuildUrl = globals.jenkinsUrl + "/job/" + jobName + "/lastBuild/api/json"

    # poll until job stops building
    building = True
    while building:
        try:
            buildInfo = json.loads(requests.get(checkBuildUrl).text)
            building = buildInfo['building']
            if building:
                sleep(3)
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
            if count == 20:
                return outDir
            building = False

    # grab the build artifacts through ftp if build was successful
    artifactsPath = globals.artifactsPathPrefix + jobName + "/builds/"

    try:
        # create an FTP connection to Jenkins
        sshClient = paramiko.SSHClient()
        sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        sshClient.connect(urlparse(globals.jenkinsUrl).hostname,
                          username=globals.configJenkinsUsername,
                          key_filename=globals.configJenkinsKey)
        ftpClient = sshClient.open_sftp()
        ftpClient.chdir(artifactsPath)

        # Probably does not need to be in a loop as the build number
        # is created as part of starting the job which occurred a
        # a few instructions earlier but better safe than sorry.
        for i in range(4):
            flist = ftpClient.listdir()

            # 1 is a sym link to the first build for that job.
            # If we delete each job after each run, we only care about
            # this first build.  Else we need to parse nextBuildNumber
            # in the parent directory to get build number.
            #
            # TODO - Delete Job.  At present, we are producing a unique
            # name so it is always build 1
            if "1" in flist:
                artifactsPath = artifactsPath + "1/"
                ftpClient.chdir(artifactsPath)
                break
            else:
                sleep(5)

        # Now loop trying to get the build artifacts.  Artifact files
        # appear to be written after the artifact parent directory and
        # the artifact directory up to ten seconds after its parent.
        # There we will place the sleep at the end of the loop as opposed
        # to the top of the loop.  If artifacts are not copied, then we
        # can move the sleep upfront but preliminary testing indicates
        # that this will work.
        for i in range(4):
            flist = ftpClient.listdir()

            if "archive" in flist:
                artifactsPath = artifactsPath + "archive/"
                ftpClient.chdir(artifactsPath)

                localArtifactsPath = localBaseDir + jobName + "." + time + "/"
                os.mkdir(localArtifactsPath)

                # Set output parm.  Only needed for synchronous call from List Package
                outDir = localArtifactsPath

                flist = ftpClient.listdir()
                for f in flist:
                    ftpClient.get(f, localArtifactsPath + f)
                break
            else:
                sleep(10)
    except IOError as e:
        print "archive move FTP failure" + jobName + " error: " + e

    return outDir

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
        return json.jsonify(status="failure", error="missing buildServer argument"), 400

    if batchName != "":
        results = batch.parseBatchFile(batchName)
        try:
            fileBuf = results['fileBuf']
        except KeyError:
            return json.jsonify(status="failure", error=fileBuf['error']), 400

        time = localtime()

        # Randomly generate a batch job UID to append to the job name to provide a grouping
        # for all jobs in the batch file for reporting purposes.
        uid = randint(globals.minRandom, globals.maxRandom)

        # Parse config data
        javaType = ""
        if fileBuf['config']['java'] == "IBM Java":
            javaType = "JAVA_HOME=/opt/ibm/java"

        # Create batch results template, stores list of job names associated with batch file
        f = open(globals.localPathForBatchTestResults + ntpath.basename(batchName), 'a+')

        # Parse package data
        submittedJob = False
        for package in fileBuf['packages']:

            # if a project can't be built, skip it. Top N may not be buildable - documentation
            selectedBuild = package['build']['selectedBuild']
            if selectedBuild == "":
                continue

            createJob_results = createJob_common(time,
                      uid,
                      package['id'],
                      package['tag'],
                      node,
                      javaType,
                      package['build']['selectedBuild'],
                      package['build']['selectedTest'],
                      package['build']['selectedEnv'],
                      package['build']['artifacts'])
            submittedJob = True

            f.write(createJob_results['artifactFolder'] + "\n")
        f.close()
    else:
        return json.jsonify(status="failure", error="could not find batch file"), 404

    if submittedJob:
        return json.jsonify(status="ok")
    return json.jsonify(status="failure", error="batch file no project is buildable"), 404

@app.route("/getBatchResults", methods=["GET", "POST"])
def getBatchResults():
    try:
        batchName = request.form["batchName"]
    except KeyError:
        return json.jsonify(status="failure", error="missing batchName POST argument"), 400

    results = []
    try:
        f = open(globals.localPathForTestResults + ntpath.basename(batchName), 'r')

        for line in f:
            jobName = line[:-1]

            if os.path.exists(globals.localPathForTestResults + jobName):
                status = "Completed"
            else:
                status = "Not Completed"

            results.append({"name":jobName, "status":status})

        f.close()
        return json.jsonify(status="ok", results=results)
    except IOError as e:
        return json.jsonify(status="ok", results=results)

@app.route("/removeBatchFile", methods=["GET", "POST"])
def removeBatchFile():
    try:
        filename = request.form["filename"]
    except KeyError:
        return json.jsonify(status="failure", error="missing filename POST argument"), 400

    try:
        location = request.form["location"]
    except KeyError:
        return json.jsonify(status="failure", error="missing location POST argument"), 400

    res = batch.removeBatchFile(filename, location)

    if res != None:
        return json.jsonify(status="failure", error=res['error'])
    return json.jsonify(status="ok")

# List available batch files
@app.route("/listBatchFiles/<repositoryType>")
def listBatchFiles(repositoryType):
    filt = request.args.get("filter", "")
    if repositoryType != "gsa" and repositoryType != "local" and repositoryType != "all":
        return json.jsonify(status="failure", error="Invalid repository type"), 400
    return json.jsonify(status="ok", results=batch.listBatchFiles(repositoryType, filt.lower()))

# List information about packages on a build server by creating and triggering a Jenkins job on it
@app.route("/listPackageForSingleSlave")
def listPackageForSingleSlave():
    packageFilter = request.args.get("packageFilter", "")
    selectedBuildServer = request.args.get("buildServer", "")

    if selectedBuildServer == "":
        return json.jsonify(status="failure", error="Build server not selected"), 400

    # If packageFilter is not provided, get info only about installed packages. Else get info about packages matching the filter
    if packageFilter == "":
        configXmlFilePath="./config_template_query_installed_packages_single_slave.xml"
        jobNameSuffix = "listAllInstalledPackagesSingleSlave"
    else:
        configXmlFilePath = "./config_template_search_packages_single_slave.xml"
        jobNameSuffix = "listAllPackagesSingleSlave"

    results = createJob_SingleSlavePanel_Common(selectedBuildServer, packageFilter, configXmlFilePath, jobNameSuffix)

    try :
        return json.jsonify(status="ok", packageData=results['packageData'])

    except KeyError:
        return json.jsonify(status="failure", error=results['error']), 404

def createJob_SingleSlavePanel_Common(selectedBuildServer, packageFilter, configXmlFilePath, jobNameSuffix):
# Read template XML file
    tree = ET.parse(configXmlFilePath)
    root = tree.getroot()

    # Assign the node where we want to run the Jenkins job
    xml_node = root.find("./assignedNode")
    xml_node.text = selectedBuildServer

    # Add the values for the Jenkins Job parameters
    xml_parameters = root.findall("./properties/hudson.model.ParametersDefinitionProperty/parameterDefinitions/hudson.model.StringParameterDefinition/defaultValue")
    buildServerDistribution, buildServerDistroRel, buildServerDistroVers = sharedData.getDistro(selectedBuildServer)
    # add parameters information
    job_input_param_number = 1
    for param in xml_parameters:
        if job_input_param_number == 1:
            param.text = buildServerDistribution
        elif job_input_param_number == 2:
            param.text = packageFilter
        job_input_param_number += 1

    # Set Job name
    uid = randint(globals.minRandom, globals.maxRandom)
    jobName = globals.localHostName + '.' + str(uid) + '.' + selectedBuildServer + '.' + jobNameSuffix

    # Add header to the config
    configXml = "<?xml version='1.0' encoding='UTF-8'?>\n" + ET.tostring(root)

    # Send to Jenkins
    NO_PROXY = {
        'no': 'pass',
    }

    r = requests.post(
        globals.jenkinsUrl + "/createItem",
        headers = {
            'Content-Type': 'application/xml'
        },
        params = {
            'name': jobName
        },
        data = configXml,
        proxies = NO_PROXY
    )

    if r.status_code == 200:
        # Success, send the jenkins job and start it right away.
        startJobUrl = globals.jenkinsUrl + "/job/" + jobName + "/buildWithParameters?" + "delay=0sec"

        # Start Jenkins job
        requests.get(startJobUrl, proxies=NO_PROXY)

        # Move artifacts.  Wait for completion as we need to return content of file
        time = strftime("%Y-%m-%d-h%H-m%M-s%S", localtime())
        outDir = moveArtifacts(jobName, globals.localPathForListResults, time)

        # If present, read the json file and then delete it and its containing folder
        if outDir != "":
            localArtifactsFilePath = outDir + "packageListSingleSlave.json"
            packageJsonFile = open(localArtifactsFilePath)
            try:
                packageData = json.load(packageJsonFile)
            except ValueError, ex:
                packageData = []
            packageJsonFile.close()

            # Delete the json file and its containing folder
            os.remove(localArtifactsFilePath)
            os.rmdir(outDir)

            # In case we were not able to generate the package data due to absence of apt-show-versions package on Ubuntu server, the json file has contents: {"Failure_reason": "Could not generate the package data"}.
            key = "Failure_reason"
            if key in packageData:
                failure_reason = packageData[key]
                return { 'status': "failure", 'error': failure_reason }
            else:
                return { 'status': "ok", 'packageData': packageData }

        return { 'status': "failure", 'error': "Did not transfer package file" }

    if r.status_code == 400:
        return { 'status': "failure", 'error': "Could not create/trigger the Jenkins job" }

# Query detailed Jenkin node state for managed lists
def queryNode(node, action):

    # Read template XML file
    tree = ET.parse("./config_template_query_slave.xml")
    root = tree.getroot()
    # Find elements we want to modify
    xml_node = root.find("./assignedNode")
    xml_parameters = root.findall("./properties/hudson.model.ParametersDefinitionProperty/parameterDefinitions/hudson.model.StringParameterDefinition/defaultValue")

    # Modify selected elements
    xml_node.text = node

    # add parameters information
    i = 1
    for param in xml_parameters:
        if i == 1:
            param.text = node
        elif i == 2:
            param.text = action
        i += 1

    # Set Job name
    uid = randint(globals.minRandom, globals.maxRandom)
    jobName = globals.localHostName + '.' + str(uid) + '.' + node + '.' + "querySingleSlave"

    # Add header to the config
    configXml = "<?xml version='1.0' encoding='UTF-8'?>\n" + ET.tostring(root)

    # Send to Jenkins
    NO_PROXY = {
        'no': 'pass',
    }

    r = requests.post(
        globals.jenkinsUrl + "/createItem",
        headers = {
            'Content-Type': 'application/xml'
        },
        params = {
            'name': jobName
        },
        data = configXml,
        proxies = NO_PROXY
    )

    if r.status_code == 200:
        # Success, send the jenkins job and start it right away.
        startJobUrl = globals.jenkinsUrl + "/job/" + jobName + "/buildWithParameters?" + "delay=0sec"

        # Start Jenkins job
        requests.get(startJobUrl, proxies=NO_PROXY)

        # This is a synchronous call.  Wait for job to complete
        time = strftime("%Y-%m-%d-h%H-m%M-s%S", localtime())
        outDir = moveArtifacts(jobName, globals.localPathForListResults, time)

        # If present, read the json file.  Let's not treat this as a fatal error
        jsonData = {}
        if outDir:
            localArtifactsFilePath = outDir + action + ".json"
            try:
                jsonFile = open(localArtifactsFilePath)
                jsonData = json.load(jsonFile)
                jsonFile.close()
            except KeyError:
                pass
            # Delete the json file and its containing folder
            os.remove(localArtifactsFilePath)
            os.rmdir(outDir)

        return { 'status': "success", 'detail': jsonData }

    if r.status_code == 400:
        return { 'status': "failure", 'error': "Could not create/trigger the Jenkins Node Query job" }

    return { 'status': "failure", 'error': "Unknown failure"  }


def listPackageForSingleSlave_common(packageName, selectedBuildServer):


    # Read template XML file
    tree = ET.parse("./config_template_package_list_single_slave.xml")
    root = tree.getroot()

    # Find elements we want to modify
    xml_node = root.find("./assignedNode")
    xml_parameters = root.findall("./properties/hudson.model.ParametersDefinitionProperty/parameterDefinitions/hudson.model.StringParameterDefinition/defaultValue")

    # Modify selected elements
    xml_node.text = selectedBuildServer

    buildServerDistribution, buildServerDistroRel, buildServerDistroVers = sharedData.getDistro(selectedBuildServer)

    # add parameters information
    i = 1
    for param in xml_parameters:
        if i == 1:
            param.text = buildServerDistribution
        elif i == 2:
            param.text = packageName
        i += 1

    # Set Job name
    uid = randint(globals.minRandom, globals.maxRandom)
    jobName = globals.localHostName + '.' + str(uid) + '.' + selectedBuildServer + '.' + "listPackageSingleSlave"

    # Add header to the config
    configXml = "<?xml version='1.0' encoding='UTF-8'?>\n" + ET.tostring(root)

    # Send to Jenkins
    NO_PROXY = {
        'no': 'pass',
    }

    r = requests.post(
        globals.jenkinsUrl + "/createItem",
        headers = {
            'Content-Type': 'application/xml'
        },
        params = {
            'name': jobName
        },
        data = configXml,
        proxies = NO_PROXY
    )

    if r.status_code == 200:
        # Success, send the jenkins job and start it right away.
        startJobUrl = globals.jenkinsUrl + "/job/" + jobName + "/buildWithParameters?" + "delay=0sec"

        # Start Jenkins job
        requests.get(startJobUrl, proxies=NO_PROXY)

        # Move artifacts.  Wait for completion as we need to return content of file
        time = strftime("%Y-%m-%d-h%H-m%M-s%S", localtime())
        outDir = moveArtifacts(jobName, globals.localPathForListResults, time)

        # If present, read the json file and then delete it and its containing folder
        if outDir != "":
            localArtifactsFilePath = outDir + "packageListSingleSlave.json"
            packageJsonFile = open(localArtifactsFilePath)
            packageData = json.load(packageJsonFile)
            packageJsonFile.close()

            # Delete the json file and its containing folder
            os.remove(localArtifactsFilePath)
            os.rmdir(outDir)
            return { 'status': "ok", 'packageData': packageData }

        return { 'status': "failure", 'error': "Did not transfer package file" }

    if r.status_code == 400:
        return { 'status': "failure", 'error': "Could not create/trigger the Jenkins job" }

# Query detailed Jenkin node state for managed lists
def queryNode(node, action):

    # Read template XML file
    tree = ET.parse("./config_template_query_slave.xml")
    root = tree.getroot()
    # Find elements we want to modify
    xml_node = root.find("./assignedNode")
    xml_parameters = root.findall("./properties/hudson.model.ParametersDefinitionProperty/parameterDefinitions/hudson.model.StringParameterDefinition/defaultValue")

    # Modify selected elements
    xml_node.text = node

    # add parameters information
    i = 1
    for param in xml_parameters:
        if i == 1:
            param.text = node
        elif i == 2:
            param.text = action
        i += 1

    # Set Job name
    uid = randint(globals.minRandom, globals.maxRandom)
    jobName = globals.localHostName + '.' + str(uid) + '.' + node + '.' + "querySingleSlave"

    # Add header to the config
    configXml = "<?xml version='1.0' encoding='UTF-8'?>\n" + ET.tostring(root)

    # Send to Jenkins
    NO_PROXY = {
        'no': 'pass',
    }

    r = requests.post(
        globals.jenkinsUrl + "/createItem",
        headers = {
            'Content-Type': 'application/xml'
        },
        params = {
            'name': jobName
        },
        data = configXml,
        proxies = NO_PROXY
    )

    if r.status_code == 200:
        # Success, send the jenkins job and start it right away.
        startJobUrl = globals.jenkinsUrl + "/job/" + jobName + "/buildWithParameters?" + "delay=0sec"

        # Start Jenkins job
        requests.get(startJobUrl, proxies=NO_PROXY)

        # This is a synchronous call.  Wait for job to complete
        time = strftime("%Y-%m-%d-h%H-m%M-s%S", localtime())
        outDir = moveArtifacts(jobName, globals.localPathForListResults, time)

        # If present, read the json file.  Let's not treat this as a fatal error
        jsonData = {}
        if outDir:
            localArtifactsFilePath = outDir + action + ".json"
            try:
                jsonFile = open(localArtifactsFilePath)
                jsonData = json.load(jsonFile)
                jsonFile.close()
            except KeyError:
                pass
            # Delete the json file and its containing folder
            os.remove(localArtifactsFilePath)
            os.rmdir(outDir)

        return { 'status': "success", 'detail': jsonData }

    if r.status_code == 400:
        return { 'status': "failure", 'error': "Could not create/trigger the Jenkins Node Query job" }

    return { 'status': "failure", 'error': "Unknown failure"  }

# Install/Delete/Update package on selected build server/slave via a Jenkins job
@app.route("/managePackageForSingleSlave")
def managePackageForSingleSlave():
    packageName = request.args.get("package_name", "")
    packageVersion = request.args.get("package_version", "")
    packageAction = request.args.get("action", "")
    selectedBuildServer = request.args.get("buildServer", "")
    packageType = request.args.get("type", "")
    host = ''

    # If there is a pacakgeType available , it indicates that this is a source install
    # and chef job needs to be created for it.
    if packageType:
       for node in globals.nodeDetails:
          if node['nodelabel'] == selectedBuildServer:
              host = node['hostname']
       chefAttr, runList = chefData.setChefDataForPackage(packageName, packageVersion, packageType)
       job = createChefJob(host, chefAttr, runList)
       buildStatus = ""
       try:
           if job['status'] == "success":
               buildStatus = monitorChefJobs(job['jobName'], sync = True)
       except KeyError as e:
           print str(e)
           assert(False)
       if buildStatus == "SUCCESS":
           return json.jsonify(status="ok", packageName=packageName, packageAction=packageAction,
                               buildStatus=buildStatus)
       else:
           return json.jsonify(status="failure", error="Could not perform the action specified"), 400
    else:
        # Read template XML file
        tree = ET.parse("./config_template_package_actions_single_slave.xml")
        root = tree.getroot()

        # Find elements we want to modify
        xml_node = root.find("./assignedNode")
        xml_parameters = root.findall("./properties/hudson.model.ParametersDefinitionProperty/parameterDefinitions/hudson.model.StringParameterDefinition/defaultValue")

        # Modify selected elements
        xml_node.text = selectedBuildServer

        buildServerDistribution, buildServerDistroRel, buildServerDistroVers = sharedData.getDistro(selectedBuildServer)

        # add parameters information
        i = 1
        for param in xml_parameters:
            if i == 1:
                param.text = buildServerDistribution
            elif i == 2:
                param.text = packageName
            elif i == 3:
                param.text = packageVersion
            elif i == 4:
                param.text = packageAction
            i += 1

        # Set Job name
        uid = randint(globals.minRandom, globals.maxRandom)
        jobName = globals.localHostName + '.' + str(uid) + '.' + selectedBuildServer + '.' + "managePackageSingleSlave"

        # Add header to the config
        configXml = "<?xml version='1.0' encoding='UTF-8'?>\n" + ET.tostring(root)

        # Send to Jenkins
        NO_PROXY = {
            'no': 'pass',
        }
        r = requests.post(
            globals.jenkinsUrl + "/createItem",
            headers = {
                'Content-Type': 'application/xml'
            },
            params = {
                'name': jobName
            },
            data = configXml,
            proxies = NO_PROXY
        )

        if r.status_code == 200:
            # Success, send the jenkins job and start it right away.
            startJobUrl = globals.jenkinsUrl + "/job/" + jobName + "/buildWithParameters?" + "delay=0sec"

            # Start Jenkins job
            requests.get(startJobUrl, proxies=NO_PROXY)

            # Check the status of the Jenkins job
            checkBuildUrl = globals.jenkinsUrl + "/job/" + jobName + "/lastBuild/api/json"
            building = True

            # Poll until job stops building
            while building:
                sleep(10)
                try:
                    buildInfo = json.loads(requests.get(checkBuildUrl).text)
                    building = buildInfo['building']
                # Check to make sure build isn't queued, if it is wait for it to dequeue
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

            # TODO: grab log file from build server.  Needed for problem determination if it fails
            # /home/jenkins/jenkins_home/jobs/<jobName>/builds/1/log

            # Grab the status of the last build
            buildInfo = json.loads(requests.get(checkBuildUrl).text)
            buildStatus = buildInfo['result']

            if buildStatus == "SUCCESS":
                return json.jsonify(status="ok", packageName=packageName, packageAction=packageAction, buildStatus=buildStatus)
            else:
                return json.jsonify(status="failure", error="Could not perform the action specified"), 400

        if r.status_code == 400:
            return json.jsonify(status="failure", error="Could not create/trigger the Jenkins job to perform the action requested"), 400

# List installed and available status of the package in packageName by creating and triggering a Jenkins job
@app.route("/listManagedPackages", methods=["GET"])
def listManagedPackages():
    try:
        distro = request.args.get("distro", "")
    except KeyError:
        return json.jsonify(status="failure", error="missing distro argument"), 400

    try:
        package = request.args.get("package", "")
    except KeyError:
        return json.jsonify(status="failure", error="missing package argument"), 400

    # Get managed list
    ml = sharedData.getManagedList()
    if not ml:
        return json.jsonify(status="failure", error="Could not get managed list.  Try again." )

    # Create node list for query
    nodes = []
    if distro == "UBUNTU":
        nodes = globals.nodeUbuntu
    elif distro == "RHEL":
        nodes = globals.nodeRHEL
    else:
        nodes = globals.nodeLabels

    # If no packages in query string parameters then retrieving the packages CSV from ManagedList.json
    if package == "":
        distroType = distro if distro=="UBUNTU" or distro=="RHEL" else 'All'
        packageNames = getPackagesCSVFromManagedList(distroType, ml);
    else:
        configXmlFilePath = "./config_template_search_packages_single_slave.xml"
        jobNameSuffix = "listAllManagePackageByFilter"
    packageList = []
    for node in nodes:
        i = globals.nodeLabels.index(node)

        if  package == "":
            results = listPackageForSingleSlave_common(packageNames, node)
        else:
            results = createJob_SingleSlavePanel_Common(node, package, configXmlFilePath, jobNameSuffix)
        try:
            for pkg in results['packageData']:
                pkg['nodeLabel'] = node
                pkg['distro'] = globals.nodeDetails[i]['distro']
                pkg['osversion'] = globals.nodeDetails[i]['version']
                pkg['arch'] = globals.nodeDetails[i]['arch']
                pkg['os'] = pkg['distro']+"-"+pkg['osversion']
                showAddButton = False
                showRemoveButton = False
                removablePackage = 'No'

                managedP, managedV, userAddedVersion = sharedData.getManagedPackage(ml, pkg, node)
                # User will be shown ADD button if "Managed Version" is less than "Latest Version" or "Installed Version"
                # is less than the "Latest Version"
                # User will be show Delete button if a installed version is available on the slave node
                pkg['managedPackageVersion'] = managedV
                if managedP:
                    if "updateVersion" in pkg and pkg["updateVersion"] and pkg["updateVersion"]!="N/A":
                        if managedV and managedV!="N/A":
                            if LooseVersion(pkg["updateVersion"]) > LooseVersion(managedV):
                                showAddButton = True
                        if not showAddButton:
                            if "installedVersion" in pkg and pkg["installedVersion"] and pkg["installedVersion"]!="N/A":
                                if LooseVersion(pkg["updateVersion"]) > LooseVersion(pkg["installedVersion"]):
                                    showAddButton = True
                    pkg['userAddedVersion'] = userAddedVersion
                    if userAddedVersion != "No":
                        showRemoveButton = True
                        removablePackage = 'Yes'
                        if pkg['userAddedVersion'] == pkg['updateVersion']:
                            showAddButton = False
                    if managedV and managedV=="N/A" and "updateVersion" in  pkg and pkg["updateVersion"]!="N/A":
                        removablePackage = 'Yes'
                else:
                    removablePackage = 'Yes'
                    if pkg['updateVersion'] != "N/A":
                        showAddButton = True
                if not showAddButton and pkg['updateAvailable']:
                    showAddButton = True
                pkg['showAddButton'] = showAddButton
                pkg['showRemoveButton'] = showRemoveButton
                pkg['removablePackage'] = removablePackage
                packageList.append(pkg)
        except KeyError:
            return json.jsonify(status="failure", error=results['error'] ), 404

    return json.jsonify(status="ok", packages=packageList)

# Add package selected by user to the local Managed List
@app.route("/addToManagedList", methods=["POST"])
def addToManagedList():

    try:
        requestData = request.form;
        action = requestData['action']
        try:
           packageDataString = requestData['packageDataList']
           packageDataList = json.loads(packageDataString)
           sharedData.addToManagedList(packageDataList, action)
        except KeyError as e:
           return json.jsonify(status="failure", error="missing packageDataList argument"), 400
    except KeyError:
        return json.jsonify(status="failure", error="missing action argument"), 400

    return json.jsonify(status="ok")

# Remove package selected by user from the local Managed List
@app.route("/removeFromManagedList", methods=["POST"])
def removeFromManagedList():
    try:
        requestData = request.form;
        action = requestData['action']
        packageDataString = requestData['packageDataList']
        packageDataList = json.loads(packageDataString)
        sharedData.removeFromManagedList(packageDataList, action)
    except KeyError:
        return json.jsonify(status="failure", error="missing packageDataList argument"), 400
    return json.jsonify(status="ok", details = {'action' : action})

# Synch the local managed package file with the one on Jenkins master.
@app.route("/synchManagedPackageList")
def synchManagedPackageList():
    try:
        serverGroup = request.args.get("serverGroup", "")
    except KeyError:
        return json.jsonify(status="failure", error="missing serverGroup argument"), 400

    if serverGroup == "":
        return json.jsonify(status="failure", error="serverGroup not available"), 400

    path = sharedData.synchManagedPackageList()

    if not path:
        return json.jsonify(status="failure", error="Could not synch the managed list.  Try again." )

    jobs = createSynchJobParameters(serverGroup)

    return json.jsonify(status="ok",
           message= str(len(jobs)) + " installation jobs are initiated in the backgroud.")

def createSynchJobParameters(serverGroup):
    # dict to hold job names of all the chef jobs to be monitored
    jobs = []

    # Dictionary to hold hosts,chefAttr,RunList per distro
    # and release wise.
    distroDetails = {}

    try:
        # Creating a dictionary holding all the distro and their respective
        # release versions
        for entry in globals.nodeDetails:
            distro = entry['distro']
            if distro not in distroDetails:
                distroDetails[distro] = {}
            if entry['rel'] not in distroDetails[distro]:
                distroDetails[distro].update({entry['rel']:{'hosts':[]}})

        # Updating the above created dictionary with list of hosts belonging
        # to a specific distro and release
        for node in globals.nodeDetails:
            for distro, releases in distroDetails.iteritems():
                if node['distro'] == distro and node['rel'] in releases:
                    rel = node['rel']
                    distroDetails[distro][rel]['hosts'].append(node['hostname'])

        # Getting chefAttributes and Chef runList per distro and release
        # and updating above created dictionary.
        for distro in distroDetails:
            for rel in distroDetails[distro]:
                chefAttr = {}
                runList = {}
                chefAttr, runList = chefData.setChefDataForSynch(distro, rel)
                distroDetails[distro][rel]['chefAttr'] = chefAttr
                distroDetails[distro][rel]['runList'] = runList
    except KeyError as e:
            print str(e)
            assert(False)

    # Invoking chef job creation with appropriate build parameters
    # for each node under given serverGroup.
    if serverGroup != 'All' and serverGroup in distroDetails:
        for rel in distroDetails[serverGroup]:
            for host in distroDetails[serverGroup][rel]['hosts']:
                job = createChefJob(host, distroDetails[serverGroup][rel]['chefAttr'],
                               distroDetails[serverGroup][rel]['runList'], "managed-pacakge")
                try:
                   if job['status'] == "success":
                      jobs.append(job['jobName'])
                except KeyError as e:
                   print str(e)
                   assert(False)

    elif serverGroup == 'All':
        for distro in distroDetails.values():
            for rel in distro.values():
                for host in rel['hosts']:
                    job = createChefJob(host, rel['chefAttr'], rel['runList'], "managed-pacakge")
                    try:
                       if job['status'] == "success":
                           jobs.append(job['jobName'])
                    except KeyError as e:
                        print str(e)
                        assert(False)

    threadRequests = makeRequests(monitorChefJobs, jobs)
    [globals.threadPool.putRequest(req) for req in threadRequests]

    return jobs

def createChefJob(host, chefAttr, runList, jobType="single-pacakge"):
    tree = ET.parse("./config_template_knife_bootstrap.xml")
    root = tree.getroot()

    # Job is always triggered on the chef-workstation , and hence assigned node is always master.
    xml_node = root.find("./assignedNode")
    xml_node.text = "master"

    xml_parameters = root.findall("./properties/hudson.model.ParametersDefinitionProperty/parameterDefinitions/hudson.model.StringParameterDefinition/defaultValue")

    i = 1
    for param in xml_parameters:
        if i == 1:
            param.text = host
        elif i == 2:
            param.text = json.dumps(chefAttr)
        elif i == 3:
            param.text = json.dumps(runList)
        i += 1

    uid = randint(globals.minRandom, globals.maxRandom)
    jobName = globals.localHostName + '.' + str(uid) + '.'+ host + '.' + "KnifeBootstrap-" + jobType + "-install"
    configXml = "<?xml version='1.0' encoding='UTF-8'?>\n" + ET.tostring(root)
    NO_PROXY = {
        'no': 'pass',
    }

    r = requests.post(
        globals.jenkinsUrl + "/createItem",
        headers = {
            'Content-Type': 'application/xml'
        },
        params = {
            'name': jobName
        },
        data = configXml,
        proxies = NO_PROXY
    )

    if r.status_code == 200:
        # Success, send the jenkins job and start it right away.
        startJobUrl = globals.jenkinsUrl + "/job/" + jobName + "/buildWithParameters?" + "delay=0sec"
        # Start Jenkins job
        requests.get(startJobUrl, proxies=NO_PROXY)
        return { 'status':"success", 'jobName':jobName }
    else:
        return { 'status':"failure", 'error':"job creation failed for: " + jobName, 'rstatus':r.status_code }

def monitorChefJobs(jobName, sync=False):
    # Monitor each job in chefJobs
    building = True
    checkBuildUrl = globals.jenkinsUrl + "/job/" + jobName + "/lastBuild/api/json"
    while building:
        sleep(10)
        try:
            buildInfo = json.loads(requests.get(checkBuildUrl).text)
            building = buildInfo['building']
            if not building:
                jobStatus = buildInfo['result']
            # Check to make sure build isn't queued, if it is wait for it to dequeue
        except ValueError:
            checkQueueUrl = globals.jenkinsUrl + "/job/" + jobName + "/api/json"
            queued = True
            count = 0;
            while queued and count < 20:
                sleep(60)
                try:
                    r = requests.get(checkQueueUrl).text
                    projectInfo = json.loads(r)
                    inQueue = projectInfo['inQueue']
                # if it's not in the queue and not building something went wrong
                except ValueError:
                    print "project failed to start building/queuing" + jobName
                count += 1
            building = False

    consoleLog = globals.jenkinsUrl + "/job/" + jobName + "/lastBuild/consoleText"
    log = str(requests.get(consoleLog).text)
    logfile = open(globals.localPathForChefLogs + jobName, 'w')
    logfile.write(log)
    logfile.close()

    if jobStatus == 'SUCCESS':
        print "TODO: Delete the build"
        if sync == True:
            return "SUCCESS"
    else:
        if sync == True:
            return "FAILURE"

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
        res = resParser.ResBuildCompare(leftname, leftdir,
                                          rightname, rightdir)
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

# Get diff log output
@app.route("/getDiffLogResults")
def getDiffLogResults():
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
        res = resParser.ResLogCompare(leftname, leftdir,
                                          rightname, rightdir)
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

@app.route("/archiveBatchFile", methods=["POST"])
def archiveBatchFile():
    try:
        filename = request.form["filename"]
    except KeyError:
        return json.jsonify(status="failure", error="missing filename POST argument"), 400

    res = batch.archiveBatchFile(filename)

    if res != None:
        return json.jsonify(status="failure", error=res['error'])
    return json.jsonify(status="ok")

@app.route("/archiveProjects", methods=["POST"])
def archiveProjects():
    projects = request.json['projects']
    errors, alreadyThere = catalog.archiveResults(projects)
    return json.jsonify(status="ok", errors=errors, alreadyThere=alreadyThere)

# Returns a comma separated list of package names from the Managed List json file
def getPackagesCSVFromManagedList(slaveNodeDistro, mljson):
    uniquePackages = set()
    for runtime in mljson['managedRuntime']:
        if runtime['distro'] == slaveNodeDistro or slaveNodeDistro == "All":
            for package in runtime['autoportPackages']:
                uniquePackages.add(package['name']);
            for package in runtime['autoportChefPackages']:
                uniquePackages.add(package['name']);
            for package in runtime['userPackages']:
                uniquePackages.add(package['name']);
    packagesCSV = ",".join(list(uniquePackages))
    return packagesCSV;

#Upload rpms debs and archives to custom repository
@app.route('/uploadToRepo', methods=['GET','POST'])
def uploadToRepo():
    postedFile = dict(request.files)
    # sourceType input from combobox
    sourceType = request.form["packageType"]
    try:
        file = postedFile['packageFile'][0]
    except KeyError:
        return json.jsonify(status="failure",
                    error="No File selected for upload"), 400

    # Checking package extension before uploading
    if file and sharedData.allowedRepoPkgExtensions(file.filename):
        status_msg = sharedData.uploadPackage(file, sourceType)
        if status_msg:
           return json.jsonify(status="failure",
                error=status_msg), 400
        else:
            return json.jsonify(status="ok")
    else:
        return json.jsonify(status="failure",
                error="Inappropriate file-type"), 400

def autoportInitialisation():
    # This is the method which would be called in main , even before
    # starting the flask application. This would be responsibe for doing
    # intial setup which is required for autoport application.

    # Uploading chef data to chef-server as part of intial setup.

    console_out = sharedData.uploadChefData()
    if console_out:
        # Even if chef-data upload fails we allow the application to start up
        # but reason of failure is displayed on the stdout.
        print "Applcation intialisation failed.\n"
        print "Failure Reason: %s" %console_out

if __name__ == "__main__":

    autoportInitialisation()

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
