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

app = Flask(__name__)
maxResults = 10
resParser = ResultParser()

catalog = Catalog(globals.hostname, urlparse(globals.jenkinsUrl).hostname)
batch = Batch()
#test AutoPortTool - x86 - jsoup-current.2014-10-24 15:01:45
resultPattern = re.compile('(.*)_(.*)_(.*)_.*\.\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d')

# Main page - just serve up main.html
@app.route("/")
def main():
    return render_template("main.html")

@app.route("/init", methods=['POST'])
def init():
    return json.jsonify(status="ok", jenkinsUrl=globals.jenkinsUrl, localPathForTestResults=globals.localPathForTestResults, pathForTestResults=globals.pathForTestResults, localPathForBatchFiles=globals.localPathForBatchFiles, pathForBatchFiles=globals.pathForBatchFiles, githubToken=globals.githubToken, configUsername=globals.configUsername, configPassword=globals.configPassword)

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
    if sort in ['stars', 'forks', 'updated']:
        searchArgs = {'sort': sort}
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
        "tags": tags
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

    # TODO: debug-log parameters

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
        fileStr = request.form["file"]
    except KeyError:
        return json.jsonify(status="failure", error="missing file"), 400

    if not os.path.exists(globals.localPathForBatchFiles):
        os.makedirs(globals.localPathForBatchFiles)

    name = "batch_file." + str(datetime.datetime.today()) 
    openPath = globals.localPathForBatchFiles + name

    f = open(openPath, "w")
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

# Create Job - takes a repo id, repo tag, and arch and creates a Jenkins job for it
# Opens a new tab with a new jenkins job URL on the client side on success,
# while the current tab stays in the same place.
@app.route("/createJob", methods=['GET', 'POST'])
def createJob(i_id = None, i_tag = None, i_arch = None, i_javaType = None):
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

    # Ensure we have a valid architecture as a post argument
    try:
        arch = request.form["arch"]
    except KeyError:
        if i_arch != None:
            arch = i_arch
        else:
            return json.jsonify(status="failure", error="missing arch"), 400

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
    
    # Get repository
    repo = globals.cache.getRepo(id)

    # Infer build steps if possible
    build = inferBuildSteps(globals.cache.getDir(repo), repo)

    # TODO: Conditionally continue based on a user interface selection to create
    # job on Jenkins w/o a build command.  User must manually enter command on Jenkins.
    # Helps automate porting environment

    if not build['success']:
        errorstr = "Programming language not supported - " + build['primary lang']
        return json.jsonify(status="failure", error=errorstr)

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
    archName = ""
    if arch == "x86":
        xml_node.text = globals.nodes['x86']
        archName = "x86"

    elif arch == "ppcle":
        xml_node.text = globals.nodes['ppcle']
        archName = "ppcle"

    xml_github_url.text = repo.html_url
    xml_git_url.text = "https" + repo.git_url[3:]

    jobName = globals.jobNamePrefix + '_' + archName + '_' + repo.name

    if (tag == "") or (tag == "Current"):
        xml_default_branch.text = "*/" + repo.default_branch
        jobName += "_current"
    else:
        xml_default_branch.text = "tags/" + tag
        jobName += "_" + tag

    # Time job is created
    time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

    # Name of new Folder
    jobFolder = jobName + "." + time

    xml_build_command.text = build['build']
    xml_test_command.text = build['test']
    xml_env_command.text = build['env']

    # In addition to whatever other environmental variables I need to inject
    # I should add whether to pick IBM Java or Open JDK
    xml_env_command.text += javaType + "\n"
    path_env = "PATH=" + globals.mavenPath + ":$PATH\n"
    xml_env_command.text += path_env
    xml_artifacts.text = build['artifacts']

    # Job metadata as passed to jenkins
    jobMetadataName = "meta.arti"
    jobMetadata = "{ \"Package\": \"" + jobName + "\", \"Version\": \"" + tag + "\", \"Build System\":\"" + build['build system'] + "\", \"Architecture\": \"" + arch + "\", \"Environment\": \"" + xml_env_command.text + "\", \"Date\": \"" + time + "\"}"

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
        return json.jsonify(status="ok", sjobUrl=startJobUrl, hjobUrl=homeJobUrl)

    # TODO : delete job and retry 
    if r.status_code == 400:
        return json.jsonify(status="failure", error='jenkins HTTP error job exists : ' + jobName), r.status_code

    return json.jsonify(status="failure", error='jenkins HTTP error '+str(r.status_code)), r.status_code

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
        globals.ftpClient.chdir(artifactsPath)
        flist = globals.ftpClient.listdir()
       
        if "lastSuccessfulBuild" in flist:
            artifactsPath = artifactsPath + "lastSuccessfulBuild/"
            globals.ftpClient.chdir(artifactsPath)
            flist = globals.ftpClient.listdir()

            if "archive" in flist:
                artifactsPath = artifactsPath + "archive/"
                globals.ftpClient.chdir(artifactsPath)
            
                localArtifactsPath = globals.localPathForTestResults + jobName + "." + \
                    str(datetime.datetime.today()) + "/"
                os.mkdir(localArtifactsPath)
                
                flist = globals.ftpClient.listdir()
 
                for f in flist:
                    globals.ftpClient.get(f, localArtifactsPath + f)

            else:
                print "archive folder missing" + jobName

    except IOError as e:
        print "archive move FTP failure" + jobName + " error: " + e

# Run Batch File - takes a batch file name and runs it
@app.route("/runBatchFile", methods=["GET", "POST"])
def runBatchFile ():
    # Get the batch file name from POST
    try:
        batchName = request.form["batchName"]
    except KeyError:
        return json.jsonify(status="failure", error="missing batch file name"), 400
  
    if batchName != "":
        # Read in the file and store as JSON
        f = open(batchName)
        fileBuf = json.load(f)
        f.close()

        javaType = ""

        if fileBuf['config']['java'] == "ibm":
            javaType = "JAVA_HOME=/opt/ibm/java"

        for package in fileBuf['packages']:            
            p_repo = globals.github.get_repo(package['id'])
            tag = package['tag']
            createJob(package['id'], package['tag'], "x86", javaType)
            createJob(package['id'], package['tag'], "ppcle", javaType)

    else:
        return json.jsonify(status="failure", error="could not find file"), 404

    return json.jsonify(status="ok")

# List available batch files
@app.route("/listBatchFiles/<repositoryType>")
def listBatchFiles(repositoryType):
    filt = request.args.get("filter", "")
    if repositoryType != "gsa" and repositoryType != "local" and repositoryType != "all":
        return json.jsonify(status="failure", error="Invalid repository type"), 400
    return json.jsonify(status="ok", results=batch.listBatchFiles(repositoryType, filt.lower()))

# List all results available on catalog
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
                    prjRes = resParser.MavenBuildSummary(resultDir+"/test_result.arti")
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
            res = resParser.MavenBuildSummary(resultDir+"/test_result.arti")
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
    p.add_argument("-n", "--jenkinsJobNamePrefix",                      help="specifies a string to prefix to the Jenkins job name, defaults to '" + globals.jobNamePrefix + "'")
    args = p.parse_args()

    if args.jenkinsURL:
        globals.jenkinsUrl = args.jenkinsURL
    if args.jenkinsJobNamePrefix:
        globals.jobNamePrefix = args.jenkinsJobNamePrefix

    if args.public:
        app.run(debug = True, host='0.0.0.0')
    else:
        app.run(debug = True)
