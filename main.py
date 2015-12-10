#!ns/usr/bin/env python

# Importing globals and initializing them is the top priority
import globals
globals.init()

# Next setting up logging
import log
logger = log.init()

# Next create thread pool for Jenkins Master
from mover import Mover
mover = Mover()

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
import shutil
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
from github import Github
from cache import Cache
from requests.exceptions import MissingSchema
from project import Project

# Constants
maxResults = 10

# Initialize autoport framework
catalog = Catalog()
batch = Batch(catalog)
project = Project(catalog)
chefData = ChefData()
sharedData = SharedData()
chefData = ChefData()
resParser = ResultParser()

# Initialize web application framework
app = Flask(__name__, static_url_path='/autoport')

# Be sure to update project.py, batch.py, and catalog.py also
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
@app.route("/autoport/")
def main():
    return render_template("main.html")

@app.route("/autoport/init", methods=['POST'])
def init():
    return json.jsonify(status="ok", jenkinsUrl=globals.jenkinsUrl,
                        localPathForTestResults=globals.localPathForTestResults,
                        pathForTestResults=globals.pathForTestResults,
                        localPathForBatchFiles=globals.localPathForBatchFiles,
                        pathForBatchFiles=globals.pathForBatchFiles,
                        githubToken=globals.githubToken,
                        configUsername=globals.configUsername,
                        configPassword=globals.configPassword,
                        useTextAnalytics=globals.useTextAnalytics,
                        logLevel=globals.logLevel,
                        gsaConnected=globals.gsaConnected)

def getJenkinsNodes_init():
    nodeNames = []
    nodeLabels = []

    nodesUrl = globals.jenkinsUrl + "/computer/api/json?pretty=true"
    try:
        nodesResults = json.loads(requests.get(nodesUrl).text)
        nodes = nodesResults['computer']
    except ValueError:
        return json.jsonify(status="failure", error="Jenkins nodes url or authentication error"), 400

    for node in nodes:
        if not node['offline']:
            name = node['displayName']
            if name != "master":
                nodeNames.append(name)
                root = ET.fromstring(requests.get(globals.jenkinsUrl +
                    "/computer/" + name + "/config.xml").text)
                nodeLabels.append(root.find("./label").text)

    return nodeNames, nodeLabels

@app.route("/autoport/getJenkinsNodes", methods=["POST"])
def getJenkinsNodes():
    # Query online build slaves when client attaches
    nodeNames, nodeLabels = getJenkinsNodes_init()
    return json.jsonify(status="ok", nodeNames=nodeNames, nodeLabels=nodeLabels)

# Get O/S details for build servers including distribution, release, version, hostname, ...
# Don't fail as a lot of func is still possible.  Nodes may go offline at any time.

def getJenkinsNodeDetails_init():

    if not globals.nodeLabels:
        return

    # Empty the global lists
    del globals.nodeDetails[:]
    del globals.nodeUbuntu[:]
    del globals.nodeRHEL[:]
    del globals.nodeOSes[:]
    del globals.nodeHosts[:]
    del globals.nodeIPs[:]

    action = "query-os"
    for node in globals.nodeLabels:
        results = queryNode(node, action)
        try:
            detail = results['detail']
            if detail:
                globals.nodeDetails.append(detail)
            nodeLabel = detail['nodelabel']
            if detail['distro'] == "UBUNTU":
                globals.nodeUbuntu.append(nodeLabel)
                osName = "Ubuntu"
            elif detail['distro'] == "RHEL":
                globals.nodeRHEL.append(nodeLabel)
                osName = "RHEL"
            globals.nodeOSes.append(osName + ' ' + detail['version'] + ' ' + detail['arch'].upper())
            globals.nodeHosts.append(detail['hostname'])
            globals.nodeIPs.append(detail['ipaddress'])
        except KeyError as e:
            if e.args[0] == 'distro':
                logger.warning("No O/S information for node " + node)
            elif e.args[0] == 'ipaddress':
                logger.warning("No IP address information for node " + node)
            elif e.args[0] == 'hostname':
                logger.warning("No hostname information for node " + node)
            else:
                logger.warning(e.message)
            pass

    logger.info("All nodes: " + str(globals.nodeLabels))
    logger.info("All OSes: " + str(globals.nodeOSes))
    logger.info("All hostnames: " + str(globals.nodeHosts))
    logger.info("All IPs: " + str(globals.nodeIPs))
    logger.info("Ubuntu nodes: " + str(globals.nodeUbuntu))
    logger.info("RHEL nodes: " + str(globals.nodeRHEL))

@app.route("/autoport/getJenkinsNodeDetails", methods=["POST"])
def getJenkinsNodeDetails():

    if not globals.nodeLabels:
        return json.jsonify(status="ok", details=[], ubuntu=[], rhel=[])

    try:
        nodeLabels = request.json['nodeLabels']
    except KeyError:
        return json.jsonify(status="failure", error="missing nodeLabels argument"), 400

    if not nodeLabels:
        return json.jsonify(status="failure", error="There are no online Jenkins build slaves"), 404

    logger.debug("In getJenkinsNodeDetails, nodeLabels=%s" % nodeLabels)

    # Utilize cached data to avoid long connect times or connect failures when a build slave is busy or hung
    nodeDetails = []
    nodeUbuntu = []
    nodeRHEL = []
    for node in nodeLabels:
        if not node in globals.nodeLabels:
            logger.info("getJenkinsNodeDetails, new node=%s" % node)
            msg = "Unknown Jenkins Server: %s.  Refresh build server configuration on Build Server tab" % node
            return json.jsonify(status="failure", error=msg), 408

        if node in globals.nodeUbuntu:
            nodeUbuntu.append(node)
        elif node in globals.nodeRHEL:
            nodeRHEL.append(node)

        i = globals.nodeLabels.index(node)
        nodeDetails.append(globals.nodeDetails[i])

    logger.info("All nodes: " + str(nodeLabels))
    logger.info("Ubuntu nodes: " + str(nodeUbuntu))
    logger.info("RHEL nodes: " + str(nodeRHEL))

    return json.jsonify(status="ok", details=nodeDetails, ubuntu=nodeUbuntu, rhel=nodeRHEL)

# Settings function
@app.route("/autoport/settings", methods=['POST'])
def settings():

    githubToken = globals.githubToken
    jenkinsUrl = globals.jenkinsUrl
    hostname = globals.hostname
    configUsername = globals.configUsername
    configPassword = globals.configPassword

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
        globals.githubToken = request.form["github"]
        if githubToken != globals.githubToken:
            globals.github = Github(globals.githubToken)
            globals.cache = Cache(globals.github)
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

    try:
        globals.useTextAnalytics = request.form["usetextanalytics"] == 'true'
    except ValueError:
        return json.jsonify(status="failure", error="bad value for useTextAnalytics"), 400

    try:
        log.chgLevel(request.form["loglevel"])
    except ValueError:
        return json.jsonify(status="failure", error="bad value for logLevel"), 400

    try:
        if jenkinsUrl != globals.jenkinsUrl:
            logger.info("Stopping threads[] connected to old Jenkins master")

            # Drain thread queue to ensure that old requests are completed first
            mover.resetConnection()

            # Initialize globals, mover threads, and Chef master
            autoportJenkinsInit(globals.jenkinsUrl, globals.configJenkinsUsername, globals.configJenkinsKey)

            # Initialize catalog
            # XXX Why is this accessing Jenkins?
            catalog.connect(globals.hostname, urlparse(globals.jenkinsUrl).hostname)

            chefData.setRepoHost(urlparse(globals.jenkinsUrl).hostname)

            jenkinsUrlSubStringLength =  globals.jenkinsUrl.rfind(':')
            if jenkinsUrlSubStringLength > 4:
                jenkinsUrlNoPort = globals.jenkinsUrl[:globals.jenkinsUrl.rfind(':')]
            else:
                jenkinsUrlNoPort = globals.jenkinsUrl
            globals.jenkinsRepoUrl = '%s:%s/autoport_repo/archives' % (jenkinsUrlNoPort, '90')

    except Exception as e :
        logger.warning("settings: Jenkins=%s Error=%s" % (urlparse(globals.jenkinsUrl).hostname, str(e)))
        msg = "Invalid Jenkins URL or networking issue.\nHostname: %s\nError: %s" % (urlparse(globals.jenkinsUrl).hostname, str(e))
        return json.jsonify(status="failure", gsaConnected=globals.gsaConnected, error=msg)

    try:
        if hostname != globals.hostname or configUsername != globals.configUsername or configPassword != globals.configPassword:
            logger.info("Applying user parameters")
            autoportUserInit(globals.hostname,globals.jenkinsUrl,globals.configUsername,globals.configPassword)

    except Exception as e :
        logger.warning("settings: Archive parameters Error=%s" % (str(e)))
        msg = "Invalid Archive Parameters (hostname, username, or password) %s\nError: %s" % (str(e))
        batch.disconnect()
        return json.jsonify(status="failure", gsaConnected=globals.gsaConnected, error=msg)

    return json.jsonify(status="ok", gsaConnected=globals.gsaConnected,
                        nodeNames=globals.nodeNames, nodeLabels=globals.nodeLabels,
                        details=globals.nodeDetails, ubuntu=globals.nodeUbuntu,
                        rhel=globals.nodeRHEL)

@app.route("/autoport/progress")
def progress():
    try:
        results = determineProgress()
        return json.jsonify(status="ok", results=results)
    except Exception as e:
        return json.jsonify(status="failure", error=str(e)), 401

# Search - return a JSON file with search results or the matched
# repo if there's a solid candidate
@app.route("/autoport/search")
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

    try:
        q = "fork:true " + query
        repos = globals.github.search_repositories(q, **searchArgs)
        try:
            numResults = repos.totalCount
        except:
            numResults = 0
        logger.debug('In search, query="%s", numResults=%d' % (q, numResults))
        if numResults == 0:
            q = query.strip().split("/")
            if len(q) == 1 or q[1] == "":       # if '/' not present or last character in string
                q = "fork:true user:%s" % q[0]
            else:
                q = "fork:true repo:%s" % "/".join(q)
            repos = globals.github.search_repositories(q, **searchArgs)
            try:
                numResults = repos.totalCount
            except:
                numResults = 0
            logger.debug('search: retry query="%s", numResults=%d' % (q, numResults))
    except Exception as e:
        return json.jsonify(status="failure", error="Could not contact github: " + str(e)), 503

    if numResults == 0:
        return json.jsonify(status="failure", error="No projects found!<br /><br />Either the project "
                   "does not exist or you don't have access rights to view it.&nbsp;&nbsp;&nbsp;You "
                   "may specify a different github token via the Settings Menu"), 418

    if numResults > maxResults:
        numResults = maxResults

    for repo in repos[:numResults]:
        globals.cache.cacheRepo(repo)
        # If this is the top hit, and the name matches exactly, and
        # it has greater than 500 stars, then just assume that's the
        # repo the user is looking for
        if autoselect and isFirst and repo.name == query.strip() and repo.stargazers_count > 500:
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
            "language": repo.language if repo.language else "N/A",
            "description": repo.description,
            "classifications": classify(repo)
        })
    return json.jsonify(status="ok", results=results, type="multiple", panel=panel)

# Detail - returns a JSON file with detailed information about the repo
@app.route("/autoport/detail/<int:id>")
def detail(id, repo=None):
    panel = request.args.get("panel", "")
    version = request.args.get("version", "")
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
    if version == "recent" and recentTag:
        useVersion = recentTag
    else:
        useVersion = "current"

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
        "language": repo.language if repo.language else "N/A",
        "languages": transformed_languages,
        "description": repo.description,
        "classifications": classify(repo),
        "build": build,
        "recentTag": recentTag,
        "tags": tags,
        "useVersion": useVersion
    }
    # Send
    return json.jsonify(status="ok", repo=repoData, type="detail", panel=panel)



# This function recomputes the search criteria for multi-project search
def changeQuery(q, key, newval):
    newq = []
    list = q.split()
    for ele in list:
        keylist = ele.split(':>')
        if len(keylist) == 1:
            keylist = ele.split(':0..')
        if key in keylist:
            newval = '0..' + str(newval)
            keylist[1] = newval
            keylist=':'.join(keylist)
        else:
            keylist=':>'.join(keylist)
        newq.append(keylist)
    newq = ' '.join(newq)
    return newq


# Search repositories - return JSON search results for the GitHub
# /search/repositories API call. See the following for details:
#   https://developer.github.com/v3/search/
@app.route("/autoport/search/repositories")
def search_repositories():

    # GitHub API parameters
    q     = request.args.get("q",     "")
    sort  = request.args.get("sort",  "stars")
    order = request.args.get("order", "desc")
    versiontag = request.args.get("version", "")
    if not versiontag:
        versiontag = "current"
    logger.debug('Search repository: query=' + str(q) + " version="+ str(versiontag))
    # AutoPort parameters
    limit = int(request.args.get("limit", "25"))
    panel = request.args.get("panel", "")

    if panel == "":
        return json.jsonify(status="failure", error="missing panel"), 400

    # This algorithm must be fast as it is used to collect information on potentially
    # thousands of projects.  Number of projects is a user specified field.  Don't look
    # for detailed information as this search is used to perform discovery, not
    # necessarily to build.  We collect detailed information when batch files are
    # submitted for build and test as build information may change. ie. ant to maven

    remaining = limit
    githubLimit = 300
    if limit < githubLimit:
        githubLimit = limit
    results = []

    try:
        while remaining:
            cnt = 0;
            logger.debug(q)
            repos = globals.github.search_repositories(q, sort=sort, order=order)[:githubLimit]
            for repo in repos:
                globals.cache.cacheRepo(repo)
                remaining -= 1
                cnt += 1

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
                    "language": repo.language if repo.language else "N/A",
                    "description": repo.description,
                    "classifications": classify(repo),
                    "useVersion": versiontag
                })
                if not remaining:
                    break

            # Github documents a max of 1000 search results per query.  We limit the
            # search to a fraction of that with githubLimit (300) to avoid the search
            # rate limit.  We assume fewer results than githubLimit means there is no
            # more data to be had.
            if cnt < githubLimit or remaining <= 0:
                break

            logger.debug("queued = " + str(limit-remaining) + " remaining = " + str(remaining))

            # We are going to search again up to the fork or star count of the last
            # entry.  There may be more of these entries that we haven't discovered
            # yet, so we remove them.  We will collect them in the next loop.
            if sort == "stars":
                trailingCnt = results[-1]['stars']
            else:
                trailingCnt = results[-1]['forks']

            logger.debug("name =" + str(results[-1]['name']))

            while results:
                if sort == "stars":
                    currentCnt = results[-1]['stars']
                else:
                    currentCnt = results[-1]['forks']

                if trailingCnt == currentCnt:
                    results.pop()
                    remaining += 1
                else:
                    break

            # Change the query from sort:0 to sort:0..TrailingCnt
            q = changeQuery(q, sort, trailingCnt)

            # Pace queries.  Avoid rate limit exception
            sleep(15)

    except GithubException as e:
        # This rate limit applies to the core apis, not search according to the
        # github documentation, but I couldn't figure out how to get the search limit
        # data.  I don't think github has implemented it yet.
        logger.warning("Github search rateLimit exceeded")
        rateLimit = globals.github.get_rate_limit()
        logger.warning("rateLimit.limit = " + str(rateLimit.rate.limit))
        logger.warning("rateLimit.remaining = " + str(rateLimit.rate.remaining))
        logger.warning("rateLimit.reset = " + str(rateLimit.rate.reset))

    # Return search results if we have any.  The user specified Limit is a maximum.
    # There is no guarantee that there are that many entries.  Some data is better
    # than no data.  The user can always try again if he wants more.
    if results:
        cnt = limit - remaining
        logger.debug("/search/repositories Requested = " + str(limit) + " Returned = " + str(cnt))
        return json.jsonify(status="ok", results=results, type="multiple", panel=panel)

    return json.jsonify(status="failure",
            error="GithubException ({0}): {1}".format(e.status, e.data['message'])), 400

# Upload Batch File - takes a file and uploads it to a permanent location (TBD)
@app.route("/autoport/uploadBatchFile", methods=['GET', 'POST'])
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

    try:
        f = open(openPath, 'wb')
        f.write(fileStr)
        f.close()
    except Exception as ex:
        print "Error: ", str(ex)

    # Open Batch details file and update the owner to Logged in GSA user or Anonymous.
    batch_data_file, batch_detail_file = None, None
    try:
        batch_data_file = open(openPath, 'r')
        batch_info = json.load(batch_data_file)
        # Update owner to GSA user id if available else Anonymous
        if batch_info.has_key("config"):
            batch_info['config']['owner'] = globals.configUsername or 'Anonymous'
            batch_detail_file = open(openPath, 'w')
            batch_detail_file.write(json.dumps(batch_info, indent=4, sort_keys=True))
    except Exception as ex:
        print "Error: ", str(ex)
    finally:
        # Close the files if the were opened in try block
        if isinstance(batch_data_file, file):
            batch_data_file.close()

        if isinstance(batch_detail_file, file):
            batch_detail_file.close()

    # We don't want to automatically be uploading to remote location, this code needs
    # to be moved into the batch table as an action for each individual batch file
    '''
    # Copy batch file to a predetermined spot in a shared file system or external object storage
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

@app.route("/autoport/updateBatchFile", methods=['GET', 'POST'])
def updateBatchFile():

    # Batch name
    try:
        openPath = request.form["name"]
    except KeyError:
        return json.jsonify(status="failure", error="missing file path"), 400

    # Batch name
    try:
        location = request.form["location"]
    except KeyError:
        return json.jsonify(status="failure", error="missing file location"), 400

    # Batch File content
    try:
        fileStr = request.form["file"]
    except KeyError:
        return json.jsonify(status="failure", error="missing file data"), 404

    try:
        batch.updateBatchFile(openPath, fileStr, location)
    except Exception as e:
        logger.debug("UpdateBatchFile : error = %s," %str(e))
        return json.jsonify(status="failure", error=str(e)), 400

    return json.jsonify(status="ok")

def convertEnvJenkins(repo, selectedEnv):
    '''
    Method to convert environment variables into a format that is accepted by the jenkins
    plugin EnvInject.  The plugin utilizes a dictionary format "K"="Y" so the environment
    variable cannot be expressed with double quotes.  Environment variables are expressed
    one per line in the form Name=Value does not need a double quote to deliniate Value.
    This is not documented by the plugin, but it is evident in the plugin's url output of
    injected environment variables of a failed job - spark.  Input variables of the form
    N=X, N="X", or N='-dX -dy="cr"' are converted on output to N=X, N=X, and N='-dX -dy=cr'.
    '''

    if not selectedEnv:
        return selectedEnv

    # Split by all whitespace, blanks, tabs, and newlines
    selectedEnv = selectedEnv.split()

    # Splits too much.  We don't want to split by embedded blanks and tabs if var is quoted
    quoteType = ""
    combine = ""
    new=[]
    for subString in selectedEnv:
        if '="' in subString:                                   # Start of quoted variable
            quoteType = '"'
        elif "='" in subString:                                 # Start of quoted variable
            quoteType = "'"

        if quoteType and quoteType in subString[-1]:            # Ends in quoted variable
            if quoteType == "'":
                subString = subString.replace('"', "'")
            else:
                subString = subString.replace('"', "")
            if combine:
                combine = combine + ' ' + subString
            else:
                combine = subString
            new.append(combine)
            quoteType = ""
            combine = ""
        elif quoteType:                                         # Mid of quoted variable
            if quoteType == "'":
                subString = subString.replace('"', "'")
            else:
                subString = subString.replace('"', "")
            if combine:
                combine = combine + ' ' + subString
            else:
                combine = subString
        else:                                                   # not a quoted variable
            new.append(subString)

    new = "\n".join(new)

    logger.debug("convertEnvJenkins: proj=%s, env=%s" % (repo.name, new))

    return new

def convertbuildInfoJson(env, buildCmd, testCmd, installCmd):
    '''
    Method to convert parameters to "key": "value" pairs
    Embedded double quotes have to be converted to single quotes.
    This information only.
    '''

    if env:
        # Env has already been reformated for jenkins and includes newlines between
        # individual environment variables.  Substitute newline character for comma, blank
        # so that one can tell where each environment variable is supposed to end.
        # "K"="MAVEN_OPTS=-Xmx2g -XX:MaxPermSize=512M, JAVA_TOOL_OPTIONS=-Dos.arch=ppc64le"
        env = env.replace('\n', ', ')

    if buildCmd:
        buildCmd = buildCmd.replace('"', "'")

    if testCmd:
        testCmd = testCmd.replace('"', "'")

    if installCmd:
        installCmd = installCmd.replace('"', "'")

    return env, buildCmd, testCmd, installCmd

# Common routine for createJob and runBatchJob
def createJob_common(time, uid, id, tag, node, javaType, javaScriptType, selectedBuild,
                     selectedTest, selectedInstall, selectedEnv, artifacts, primaryLang):

    # Get repository
    repo = globals.cache.getRepo(id)

    if not selectedBuild and not selectedTest:
        errorstr = "Project %s cannot be built.\n\nReason: primary programming language (%s) is not supported!" % (repo.name, repo.language)
        return { 'status': "failure", 'error': errorstr }

    try:
        i = globals.nodeLabels.index(node)
    except:
        return { 'status': "failure", 'error': "Invalid build server" }

    hostname = ""
    ipAddr = ""
    osDesc = ""
    try:
        hostName = globals.nodeDetails[i]['hostname']
        ipAddr = globals.nodeDetails[i]['ipaddress']
        osDesc = globals.nodeOSes[i]         # This is formatted O/S Version Platform for UI
    except:
        pass

    logger.debug("In createJob_common, name=%s, tag=%s, javaType=%s, jsType=%s" % (repo.name, tag, javaType, javaScriptType))

    # Read template XML file
    tree = ET.parse("config_template.xml")
    root = tree.getroot()
    # Find elements we want to modify
    xml_github_url = root.find("./properties/com.coravy.hudson.plugins.github.GithubProjectProperty/projectUrl")
    xml_git_url = root.find("./scm/userRemoteConfigs/hudson.plugins.git.UserRemoteConfig/url")
    xml_default_branch = root.find("./scm/branches/hudson.plugins.git.BranchSpec/name")
    xml_env_command = root.find("./buildWrappers/EnvInjectBuildWrapper/info/propertiesContent")
    xml_node = root.find("./assignedNode")
    xml_parameters = root.findall("./properties/hudson.model.ParametersDefinitionProperty/parameterDefinitions/hudson.model.StringParameterDefinition/defaultValue")

    # Modify selected elements
    xml_node.text = node

    xml_github_url.text = repo.html_url
    xml_git_url.text = "https" + repo.git_url[3:]

    jobName = globals.localHostName + '.' + str(uid) + '.' + node + '.N-' + repo.name

    logger.debug("createJob_common: jobName=%s" % jobName)

    if tag == "" or tag == "current" or tag == "Current":                     # Current is legacy
        xml_default_branch.text = "*/" + repo.default_branch
        jobName += ".current"
    else:
        tags, recentTag = getTags(repo)
        if tag == "recent" and recentTag:
            xml_default_branch.text = "tags/" + recentTag
            jobName += "." + recentTag
        elif tag in tags:
            xml_default_branch.text = "tags/" + tag
            jobName += "." + tag
        else:
            logger.debug("createJob_common: Error invalid proj=%s, tag=%s" % (repo.name, tag))
            msg = "Invalid project %s build tag %s" % (repo.name, tag)
            return { 'status': "failure", 'error': msg }

    # Time job is created.  Parameter to Jenkins.  Blanks allowed
    timestr = strftime("%Y-%m-%d %H:%M:%S", time)

    # Name of jenkins new Folder
    jobFolder = jobName + "." + timestr

    # This is the build shell script that is invoked on the build slave
    buildCmd = selectedBuild

    # This is the test shell script that is invoked on the build slave
    testCmd = selectedTest

    # This is the install shell script that is invoked on the build slave
    installCmd = selectedInstall

    # Format environment variables deduced from readme files or provided by user
    selectedEnv = convertEnvJenkins(repo, selectedEnv)
    xml_env_command.text = selectedEnv

    # Format commands and environment variables for json files
    selectedEnv, buildCmd, testCmd, installCmd = convertbuildInfoJson(
                   selectedEnv, buildCmd, testCmd, installCmd)

    # Job metadata provides information for reporting purposes
    jobMetadataName = "meta.arti"
    jobMetadata = "{ \"Package\": \"" + jobName + "\",\
        \"Version\": \"" + tag + "\",\
        \"Primary Language\": \"" + primaryLang + "\",\
        \"Environment\": \"" + selectedEnv + "\",\
        \"Build Command\": \"" + buildCmd + "\",\
        \"Test Command\": \"" + testCmd + "\",\
        \"Install Command\": \"" + installCmd + "\",\
        \"Architecture\": \"" + node + "\",\
        \"Hostname\": \"" + hostName + "\",\
        \"Ipaddr\": \"" + ipAddr + "\",\
        \"OS\": \"" + osDesc + "\",\
        \"Date\": \"" + timestr + "\" }"

    # add parameters information
    i = 1
    for param in xml_parameters:
        if i == 1:
            param.text = jobMetadataName
        elif i == 2:
            param.text = jobMetadata
        elif i == 3:
            param.text = hostName
        elif i == 4:
            param.text = ipAddr
        elif i == 5:
            param.text = osDesc
        elif i == 6:
            param.text = javaType
        elif i == 7:
            param.text = javaScriptType
        elif i == 8:
            param.text = repo.html_url
        elif i == 9:
            param.text = tag
        elif i == 10:
            param.text = selectedEnv
        elif i == 11:
            param.text = buildCmd
        elif i == 12:
            param.text = testCmd
        elif i == 13:
            param.text = installCmd
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

    logger.debug("createJob_common: jenkins job post proj=%s, rc=%d" % (repo.name, r.status_code))

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

        logger.debug("createJob_common: moveArtifacts queue proj=%s" % repo.name)

        # Split off a thread to transfer job results upon job completion to localDir
        localDir = globals.localPathForTestResults + jobName + "." + timestr + "/"
        args = [((jobName, localDir), {})]
        threadRequests = makeRequests(moveArtifacts, args)
        [globals.threadPool.putRequest(req) for req in threadRequests]

        # Stays on the same page, after creating a new jenkins job.
        return { 'status': "ok", 'sjobUrl': startJobUrl, 'hjobUrl': homeJobUrl,
                 'jobFolder': jobFolder, 'artifactFolder': artifactFolder }

    if r.status_code == 400:
        return { 'status': "failure", 'error': "jenkins HTTP error job exists : " + jobName, 'rstatus': r.status_code }

    return { 'status': "failure", 'error': "jenkins HTTP error " + str(r.status_code), 'rstatus': r.status_code }


# Create Job - takes a repo id, repo tag, and build node and creates a Jenkins job for it
# Opens a new tab with a new jenkins job URL on the client side on success,
# while the current tab stays in the same place.
@app.route("/autoport/createJob", methods=['GET', 'POST'])
def createJob(i_id = None,
              i_tag = None,
              i_node = None,
              i_javaType = None,
              i_javaScriptType = None,
              i_selectedBuild = None,
              i_selectedTest = None,
              i_selectedInstall = None,
              i_selectedEnv = None,
              i_artifacts = None,
              i_primaryLang = None,
              i_isBatchJob = False):

    # Randomly generate a job UID to append to the job name to guarantee uniqueness across jobs.
    # If a job already has the same hostname and UID, we will keep regenerating UIDs until a unique one
    # is found. This should be an extremely rare occurence.
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
            tag = "current"

    # Get javaType
    try:
        javaType = request.form["javaType"]
    # defaults to open JDK
    except KeyError:
        if i_javaType != None:
            javaType = i_javaType
        else:
            return json.jsonify(status="failure", error="missing java type"), 400

    # Get javaScriptType
    try:
        javaScriptType = request.form["javaScriptType"]
    # defaults to nodejs
    except KeyError:
        if i_javaScriptType != None:
            javaScriptType = i_javaScriptType
        else:
            return json.jsonify(status="failure", error="missing javaScript type"), 400

    # Get build info
    try:
        selectedBuild = request.form["selectedBuild"]
        if selectedBuild.strip().startswith('[TextAnalytics]'): #Remove the [TextAnalytics] tag from build command
            selectedBuild = selectedBuild[15:]
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
    try:
        selectedInstall =  request.form["selectedInstall"]
    except KeyError:
        if i_selectedInstall != None:
            selectedInstall = i_selectedInstall
        else:
            selectedInstall = ""

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
        primaryLang = request.form["primaryLang"]
    except KeyError:
        if i_primaryLang != None:
            primaryLang = i_primaryLang
        else:
            return json.jsonify(status="failure", error="missing primary language"), 400

    rc = createJob_common(localtime(), uid, id, tag, node, javaType, javaScriptType, selectedBuild,
                          selectedTest, selectedInstall, selectedEnv, artifacts, primaryLang)

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
def moveArtifacts(jobName, localDir, moverCv=None):
    logger.debug("In moveArtifacts, jobName=%s localDir=%s" % (jobName, localDir))
    outDir = ""
    checkBuildUrl = globals.jenkinsUrl + "/job/" + jobName + "/lastBuild/api/json"

    # poll until job stops building
    building = True
    while building:
        try:
            requestInfo = requests.get(checkBuildUrl)
            if requestInfo.status_code == 200:
                buildInfo = json.loads(requestInfo.text)
                building = buildInfo['building']
            if building:
                sleep(3)
        # check to make sure build isn't queued, if it is wait for it to dequeue
        except ValueError:
            checkQueueUrl = globals.jenkinsUrl + "/job/" + jobName + "/api/json"
            queued = True

            count = 0;
            while queued and count < 20:
                logger.debug("moveArtifacts: sleep 10 build is queued - not started")
                sleep(10)
                try:
                    r = requests.get(checkQueueUrl).text
                    projectInfo = json.loads(r)
                    inQueue = projectInfo['inQueue']
                # if it's not in the queue and not building something went wrong
                except ValueError:
                    logger.debug("moveArtifacts: project failed to start building/queuing" + jobName)
                count += 1
            if count == 20:
                return outDir
            building = False

    # grab the build artifacts through ftp if build was successful
    artifactsPath = globals.artifactsPathPrefix + jobName + "/builds/"
    try:
        mover.chdir(artifactsPath)

        # Probably does not need to be in a loop as the build number
        # is created as part of starting the job which occurred a
        # a few instructions earlier but better safe than sorry.
        for i in range(4):
            flist = mover.listdir()

            # 1 is a sym link to the first build for that job.
            # If we delete each job after each run, we only care about
            # this first build.  Else we need to parse nextBuildNumber
            # in the parent directory to get build number.
            if "1" in flist:
                artifactsPath = artifactsPath + "1/"
                mover.chdir(artifactsPath)
                logger.debug("moveArtifacts: build complete  %s" % jobName)
                break
            else:
                logger.debug("moveArtifacts: sleep 5 waiting for build to complete")
                sleep(5)

        # Now loop trying to get the build artifacts.  Artifact files
        # appear to be written after the artifact parent directory and
        # the artifact directory up to ten seconds after its parent.
        # There we will place the sleep at the end of the loop as opposed
        # to the top of the loop.  If artifacts are not copied, then we
        # can move the sleep upfront but preliminary testing indicates
        # that this will work.
        for i in range(4):
            flist = mover.listdir()

            if "archive" in flist:
                artifactsPath = artifactsPath + "archive/"
                mover.chdir(artifactsPath)

                try:
                    os.mkdir(localDir)
                    flist = mover.listdir()
                    if ".autoport-scratch" in flist:
                        mover.chdir(".autoport-scratch")
                        flist = mover.listdir()
                    logger.debug("moveArtifacts: found artifacts %s %s" % (jobName, str(flist)))
                    for f in flist:
                        mover.get(f, localDir + f)
                    outDir = localDir                           # Transfer success
                except IOError as e:
                    logger.warning("moveArtifacts: failed to transfer artifacts %s" % str(flist))
                    logger.debug("moveArtifacts: Error %s" % (str(e)))
                break
            else:
                logger.debug("moveArtifacts: sleep 10 waiting for artifacts")
                sleep(10)
    except IOError as e:
        logger.warning("moveArtifacts: FTP failure for Job %s %s" % (jobName, str(e)))

    if moverCv:
        # Display address of moverCv variable.  Should be the same as top half app.route requester.
        logger.debug("Leaving moveArtifacts, moverCv=%s outDir=%s" % (str(hex(id(moverCv))), outDir))
        moverCv['cv'].acquire()
        moverCv['outDir'] = outDir
        moverCv['cv'].notifyAll()
        moverCv['cv'].release()
    else:
        logger.debug("Leaving moveArtifacts, outDir=%s" % (outDir))

    return outDir

# Run Batch File - takes a batch file name and runs it
@app.route("/autoport/runBatchFile", methods=["GET", "POST"])
def runBatchFile ():
    # Get the batch file name from POST
    try:
        batchName = request.form["batchName"]
    except KeyError:
        return json.jsonify(status="failure", error="missing batchName POST argument"), 400

    # Get the batch file name from POST
    try:
        nodeCSV = request.form["nodeCSV"]
    except KeyError:
        return json.jsonify(status="failure", error="missing buildServer argument"), 400

    logger.debug("In runBatchFile, batchName=%s, nodeCSV=%s" % (batchName, nodeCSV))

    submittedJob = False
    if batchName != "":
        results = batch.parseBatchFile(batchName)
        try:
            fileBuf = results['fileBuf']
        except KeyError:
            return json.jsonify(status="failure", error=results['error']), 400

        try:
            error = fileBuf['error']
            return json.jsonify(status="failure", error=error), 401
        except KeyError:
            pass

        submissionTime = localtime()

        # Randomly generate a batch job UID to append to the job name to provide a grouping
        # for all jobs in the batch file for reporting purposes.
        uid = randint(globals.minRandom, globals.maxRandom)

        # Parse config data
        javaType = ""
        if fileBuf['config']['java'] == "IBM Java":
            javaType = "/etc/profile.d/ibm-java.sh"

        javaScriptType = ""
        if fileBuf['config']['javascript'] == "IBM SDK for Node.js":
            javaScriptType = "/etc/profile.d/ibm-nodejs.sh"

        logger.debug("runBatchFile: javaType=%s javaScriptType=%s nodeCSV=%s" % (javaType, javaScriptType, nodeCSV))

        # Create batch results template, stores list of job names associated with batch file
        # Create a folder of format  <batch_name>.<uuid>
        try:
            temp,batchNameOnly, createdTime = batchName.split('.')
            batchDirName = "%s.%s" % (
                globals.localPathForBatchTestResults + ntpath.basename(batchNameOnly),
                uid
            )
            newBatchName = "%s/%s.%s.%s" %(
                batchDirName,
                ntpath.basename(batchNameOnly),
                uid,
                strftime("%Y-%m-%d-h%H-m%M-s%S", submissionTime)
            )

            if not os.path.exists(batchDirName):
                os.makedirs(batchDirName)
        except ValueError:
            newBatchName = globals.localPathForBatchTestResults + ntpath.basename(batchName)

        f = open(newBatchName, 'a+')
        nodeList = nodeCSV.split(',')
        for node in nodeList:
            # Parse package data
            for package in fileBuf['packages']:

                # if a project can't be built, skip it. Top N may not be buildable - documentation
                selectedBuild = package['build']['selectedBuild']
                selectedTest = package['build']['selectedTest']
                if selectedBuild == "" and selectedTest == "":
                    continue

                # If build info is derived from a travis.yaml file, then both build and test
                # need to be run if specified as 'selectedBuild' is devoted to dependencies and
                # 'selectedTest' is devoted to the named project.  The latter includes both
                # build and test commands as provided by travis.yaml file.
                selectedEnv = package['build']['selectedEnv']
                if (not selectedEnv or "TRAVIS_OS_NAME=" not in selectedEnv) and\
                   'includeTestCmds' in fileBuf['config'] and fileBuf['config']['includeTestCmds'] == 'False':
                    package['build']['selectedTest'] = ""

                if 'includeInstallCmds' in fileBuf['config'] and fileBuf['config']['includeInstallCmds'] == 'False':
                    package['build']['selectedInstall'] = ""
 
                createJob_results = createJob_common(localtime(),
                          uid,
                          package['id'],
                          package['tag'],
                          node,
                          javaType,
                          javaScriptType,
                          package['build']['selectedBuild'],
                          package['build']['selectedTest'],
                          package['build']['selectedInstall'],
                          package['build']['selectedEnv'],
                          package['build']['artifacts'],
                          package['build']['primaryLang'])
                submittedJob = True

                try:
                    f.write(createJob_results['artifactFolder'] + "\n")
                except KeyError:
                    pass
        f.close()
    else:
        return json.jsonify(status="failure", error="could not find batch file"), 404

    logger.debug("Leaving runBatchFile, batchName=%s" % batchName)

    if submittedJob:
        return json.jsonify(status="ok")

    logger.debug("runBatch Error: No project buildable in batch file (%s)!" % batchName)

    return json.jsonify(status="failure", error="Autoport does not know how to build any project in the Batch File!"), 404

@app.route("/autoport/getBatchResults", methods=["GET", "POST"])
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

@app.route("/autoport/removeBatchFile", methods=["GET", "POST"])
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
@app.route("/autoport/listBatchFiles/<repositoryType>")
def listBatchFiles(repositoryType):
    try:
        filt = request.args.get("filter", "")
        if repositoryType != "gsa" and repositoryType != "local" and repositoryType != "all":
            return json.jsonify(status="failure", error="Invalid repository type"), 400
        return json.jsonify(status="ok", results=batch.listBatchFiles(repositoryType, filt.lower()))
    except Exception as e:
        print e
        return json.jsonify(status="failure", error=str(e)), 401

# List available batch Results
@app.route("/autoport/listBatchReports/<repositoryType>")
def listBatchReports(repositoryType):
    """
    This function fetches and returns list of Batch test reports.
    """
    try:
        filt = request.args.get("filter", "")
        if repositoryType != "gsa" and repositoryType != "local" and repositoryType != "all":
            return json.jsonify(status="failure", error="Invalid repository type"), 400
        return json.jsonify(status="ok", results=batch.listBatchReports(repositoryType, filt.lower()))
    except Exception as e:
        print "Error: ", str(e)
        return json.jsonify(status="failure", error=str(e)), 401

# Archive batch reports data to GSA
@app.route("/autoport/archiveBatchReports", methods=['POST'])
def archiveBatchReports():
    try:
        result = {}
        reports = request.json['reports']
        logger.info("In archiveBatchReports reports=" + str(reports))
        for report in reports:
            projectsArr = []
            f = open(report,'r')
            projectsArr = f.read().strip('\n').split('\n')
            f.close()
            status, errors, alreadyThere = catalog.archiveResults(projectsArr)
            logger.info("status=%s errors=%s" % (status, errors))
            if status == "failure":
                return json.jsonify(status="failure", error=errors), 400
            archiveRes = batch.archiveBatchReports(report)
            result[report] = archiveRes
        return json.jsonify(status="ok", results=result), 200
    except Exception as e:
        return json.jsonify(status="failure", error=str(e)), 401

# Removes batch reports data from local or GSA
@app.route("/autoport/removeBatchReports", methods=["POST"])
def removeBatchReports():
    try:
        reports = request.json['reports']
        logger.info("In removeBatchReports reports=" + str(reports))
        batch.removeBatchReportsData(reports, catalog)
        return json.jsonify(status="ok"), 200
    except Exception as e:
        return json.jsonify(status="failure", error=str(e)), 401

# List information about packages on a build server by creating and triggering a Jenkins job on it
@app.route("/autoport/listPackageForSingleSlave")
def listPackageForSingleSlave():
    packageFilter = request.args.get("packageFilter", "")
    selectedBuildServer = request.args.get("buildServer", "")

    if selectedBuildServer == "":
        return json.jsonify(status="failure", error="Build server not selected"), 400

    # If packageFilter is not provided, get info only about installed packages.
    # Else get info about packages matching the filter
    if packageFilter == "":
        configXmlFilePath="./config_template_query_installed_packages_single_slave.xml"
        jobNameSuffix = "listAllInstalledPackagesSingleSlave"
    else:
        configXmlFilePath = "./config_template_search_packages_single_slave.xml"
        jobNameSuffix = "listAllPackagesSingleSlave"

    try:
        results = createJob_SingleSlavePanel_Common(selectedBuildServer, packageFilter, \
                                                    configXmlFilePath, jobNameSuffix)
    except Exception as e:
        return json.jsonify(status="failure", error=str(e)), 401

    try :
        return json.jsonify(status="ok", packageData=results['packageData'])

    except KeyError:
        return json.jsonify(status="failure", error=results['error']), 404

def singleSlaveCallback(outDir):
    logger.debug("In singleSlaveCallback, query results transferred to outDir=%s" % outDir)

    # If present, read the json file and then delete it and its containing folder
    jsonData = []
    if outDir != "":
        localArtifactsFilePath = outDir + "packageListSingleSlave.json"
        try:
            packageJsonFile = open(localArtifactsFilePath)
            jsonData = json.load(packageJsonFile)
        except Exception as e:
            logger.debug("singleSlaveCallback: Error %s" % str(e))
        else:
            packageJsonFile.close()
            # Delete the json file and its containing folder upon success
            os.remove(localArtifactsFilePath)
            os.rmdir(outDir)
    return jsonData

def createJob_SingleSlavePanel_Common(selectedBuildServer, packageFilter, configXmlFilePath, jobNameSuffix, cv=None):

    returnData = {}

    # This condition variable links the completion of the function moveArtifacts()
    # that is run asynchronously by a thread with the invocation of the function
    # listPackageForSingleSlave_Callback that processes the output of the thread
    moverCv = {}
    moverCv['cv'] = threading.Condition()
    moverCv['outDir'] = ""

    logger.debug("In createJob_SingleSlavePanel_Common, cv=%s packageFilter=%s, configXmlFilePath=%s jobNameSuffix=%s," %
       (str(hex(id(cv))), packageFilter, configXmlFilePath, jobNameSuffix))
    logger.debug("createJob_SingleSlavePanel_Common, cv=%s moverCv:%s" % (str(hex(id(cv))), str(hex(id(moverCv)))))

    def createJob_SingleSlavePanel_Callback(outDir):
        data = singleSlaveCallback(outDir)
        return data

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
        elif job_input_param_number == 3:
            param.text = globals.jenkinsRepoUrl
        elif job_input_param_number == 4:
            param.text = globals.localTarRepoLocation
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

    try:
        logger.debug("createJob_SingleSlavePanel_Common: creating jenkins job %s" % jobName)
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
    except MissingSchema as e:
        logger.error("createJob_SingleSlavePanel_Common: Please provide valid jenkins url in settings menu")
        assert(False), "Please provide valid jenkins url in settings menu!"

    if r.status_code == 200:
        # Success, send the jenkins job and start it right away.
        startJobUrl = globals.jenkinsUrl + "/job/" + jobName + "/buildWithParameters?" + "delay=0sec"

        # Start Jenkins job
        requests.get(startJobUrl, proxies=NO_PROXY)


        # Split off a thread to transfer job results from jenkins master to localDir
        # Wait for thread completion as we need to return the content of the result file
        time = strftime("%Y-%m-%d-h%H-m%M-s%S", localtime())
        localDir = globals.localPathForListResults + jobName + "." + time + "/"
        args = [((jobName, localDir, moverCv), {})]
        threadRequests = makeRequests(moveArtifacts, args)

        # Wait for handler createJob_SingleSlavePanel_Callback to run as the caller is expecting results
        moverCv['cv'].acquire()
        [globals.threadPool.putRequest(req) for req in threadRequests]
        logger.debug("createJob_SingleSlavePanel_Common, sleeping on moverCv=%s" % str(hex(id(moverCv))))
        moverCv['cv'].wait()
        outDir = moverCv['outDir']
        logger.debug("createJob_SingleSlavePanel_Common, after sleep on moverCv=%s" % str(hex(id(moverCv))))
        moverCv['cv'].release()

        packageData = createJob_SingleSlavePanel_Callback(outDir)

        # Check for error when using O/S install commands which is recorded in a key
        # packageData is [] when the package is not available
        if packageData and "Failure_reason" in packageData:
            failure_reason = packageData[key]
            returnData = { 'status': "failure", 'error': failure_reason }
        else:
            returnData = { 'status': "ok", 'packageData': packageData, 'node': selectedBuildServer }

    if r.status_code == 400:
        returnData = { 'status': "failure", 'error': "Could not create/trigger the Jenkins job" }

    if cv:
         cv['cv'].acquire()
         cv['results'].append(returnData)
         cv['cnt'] -= 1
         if cv['cnt'] == 0:
             cv['cv'].notifyAll()
         cv['cv'].release()

    return returnData

# Query detailed Jenkin node state for managed lists
def queryNode(node, action):

    callbackData = []              # Apparently has to be an array to avoid new variable allocation

    def queryNodeCallback(request, outDir):
        logger.debug("In queryNodeCallback, query results transferred to outDir=%s" % outDir)
        if outDir:
            jsonData = {}
            localArtifactsFilePath = outDir + "query-os.json"
            try:
                jsonFile = open(localArtifactsFilePath)
                jsonData = json.load(jsonFile)
                logger.debug("jsonData=%s" % jsonData)
            except Exception as e:
                logger.debug("queryNodeCallback: Error %s" % str(e))
            else:
                jsonFile.close()
                callbackData.append(jsonData)
                # Delete the json file and its containing folder
                os.remove(localArtifactsFilePath)
                os.rmdir(outDir)

    logger.debug("In queryNode, node=%s action=%s" % (node, action))

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

    logger.debug("queryNode: creating jenkins job %s" % jobName)
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

        # Split off a thread to transfer job results from jenkins master to localDir
        # Wait for thread completion as we need to return the content of the result file
        time = strftime("%Y-%m-%d-h%H-m%M-s%S", localtime())
        localDir = globals.localPathForListResults + jobName + "." + time + "/"
        args = [((jobName, localDir), {})]
        threadRequests = makeRequests(moveArtifacts, args, queryNodeCallback)
        [globals.threadPool.putRequest(req) for req in threadRequests]
        globals.threadPool.wait()

        if callbackData:
            return { 'status': "success", 'detail': callbackData[0]}

    if r.status_code == 400:
        return { 'status': "failure", 'error': "Could not create/trigger the Jenkins Node Query job" }

    return { 'status': "failure", 'error': "Unknown failure"  }


def listPackageForSingleSlave_common(packageName, selectedBuildServer, cv=None):

    returnData = {}

    # This condition variable links the completion of the function moveArtifacts()
    # that is run asynchronously by a thread with the invocation of the function
    # listPackageForSingleSlave_Callback that processes the output of the thread
    moverCv = {}
    moverCv['cv'] = threading.Condition()
    moverCv['outDir'] = ""

    logger.debug("In listPackageForSingleSlave_common, cv=%s packageName=%s selectedBuildServer=%s" % (str(hex(id(cv))), packageName, selectedBuildServer))
    logger.debug("listPackageForSingleSlave_common, cv=%s moverCv:%s" % (str(hex(id(cv))), str(hex(id(moverCv)))))

    def listPackageForSingleSlave_Callback(outDir):
        data = singleSlaveCallback(outDir)
        return data

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
    job_input_param_number = 1
    for param in xml_parameters:
        if job_input_param_number == 1:
            param.text = buildServerDistribution
        elif job_input_param_number == 2:
            param.text = packageName
        elif job_input_param_number == 3:
            param.text = globals.jenkinsRepoUrl
        elif job_input_param_number == 4:
            param.text = globals.localTarRepoLocation
        job_input_param_number += 1

    # Set Job name
    uid = randint(globals.minRandom, globals.maxRandom)
    jobName = globals.localHostName + '.' + str(uid) + '.' + selectedBuildServer + '.' + "listPackageSingleSlave"

    # Add header to the config
    configXml = "<?xml version='1.0' encoding='UTF-8'?>\n" + ET.tostring(root)

    # Send to Jenkins
    NO_PROXY = {
        'no': 'pass',
    }

    try:
        logger.debug("listPackageForSingleSlave_common: creating jenkins job %s" % jobName)
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
    except MissingSchema as e:
        assert(False), "Please provide valid jenkins url in settings menu!"

    if r.status_code == 200:
        # Success, send the jenkins job and start it right away.
        startJobUrl = globals.jenkinsUrl + "/job/" + jobName + "/buildWithParameters?" + "delay=0sec"
        # Start Jenkins job
        requests.get(startJobUrl, proxies=NO_PROXY)

        # Move artifacts.  Wait for completion as we need to return content of file
        time = strftime("%Y-%m-%d-h%H-m%M-s%S", localtime())
        localDir = globals.localPathForListResults + jobName + "." + time + "/"
        args = [((jobName, localDir, moverCv), {})]
        threadRequests = makeRequests(moveArtifacts, args)

        # Wait for handler listPackageForSingleSlave_Callback to run as the caller is expecting results
        moverCv['cv'].acquire()
        [globals.threadPool.putRequest(req) for req in threadRequests]
        moverCv['cv'].wait()
        outDir = moverCv['outDir']
        moverCv['cv'].release()

        packageData = listPackageForSingleSlave_Callback(outDir)

        logger.debug("listPackageForSingleSlave_common: cnt packageData[]=%s selectedBuildServer=%s" % (str(len(packageData)), selectedBuildServer))

        # If present, read the json file and then delete it and its containing folder
        if packageData:
            returnData = { 'status': "ok", 'packageData': packageData, 'node': selectedBuildServer }
        else:
            returnData = { 'status': "failure", 'error': "Did not transfer package file" }

    if r.status_code == 400:
        returnData = { 'status': "failure", 'error': "Could not create/trigger the Jenkins job" }

    if cv:
         cv['cv'].acquire()
         cv['results'].append(returnData)
         cv['cnt'] -= 1
         if cv['cnt'] == 0:
             cv['cv'].notifyAll()
         cv['cv'].release()

    return returnData

# Install/Delete/Update package on selected build server/slave via a Jenkins job
@app.route("/autoport/managePackageForSingleSlave")
def managePackageForSingleSlave():
    packageName = request.args.get("package_name", "")
    packageVersion = request.args.get("package_version", "")
    packageAction = request.args.get("action", "")
    selectedBuildServer = request.args.get("buildServer", "")
    packageType = request.args.get("type", "")
    extension = request.args.get("extension", "")
    host = ''

    # If there is a packageType available , it indicates that this is a source install
    # and chef job needs to be created for it.
    if packageType:
       for node in globals.nodeDetails:
          if node['nodelabel'] == selectedBuildServer:
              host = node['hostname']
              ipaddress = node['ipaddress']
       chefAttr, runList = chefData.setChefDataForPackage(packageName, packageVersion, \
                               packageType, packageAction, extension)
       job = createChefJob(host, ipaddress, chefAttr, runList)
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
           return json.jsonify(status="failure", error="Failed to run Jenkins job. Job Status: %s" % buildStatus, packageName=packageName, packageAction=packageAction,
                               buildStatus="FAILURE"), 400
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
                return json.jsonify(status="ok",
                    packageName=packageName, packageAction=packageAction, buildStatus=buildStatus)
            else:
                return json.jsonify(status="failure",
                    error="Failed to run Jenkins job. Job Status: " + buildStatus), 400

        if r.status_code == 400:
            return json.jsonify(status="failure",
                error="Could not create/trigger the Jenkins job to perform the action requested"), 400

# List installed and available status of the package in packageName by creating and triggering a Jenkins job
@app.route("/autoport/listManagedPackages", methods=["GET"])
def listManagedPackages():

    cv = {}
    cv['cv'] = threading.Condition()
    cv['cnt'] = 0
    cv['results'] = []

    packageList = []

    def listCallback(data):
        '''
        callback to handle return value of each thread
        and manipulate it further.
        '''
        logger.debug("In listCallback, status=%s node=%s" % (data['status'], data['node']))
        if data['status'] == 'ok':
            try:
                i = globals.nodeLabels.index(data['node'])
                for pkg in data['packageData']:
                    pkg['nodeLabel'] = data['node']
                    pkg['distro'] = globals.nodeDetails[i]['distro']
                    pkg['arch'] = globals.nodeDetails[i]['arch']
                    pkg['os_arch'] = globals.nodeOSes[i]              # This is O/S Description for UI

                    # package_name is set to archive name to distinguish between multiple extensions,
                    # since summary column is not available in managed panel
                    pkg['pkg_name'] = pkg['archiveName'] if 'archiveName' in pkg and package else pkg['packageName']
                    isAddable = False
                    isRemovable = False
                    enableCheckBox = False
                    managedP, managedV, userAddedVersion, removablePackage = sharedData.getManagedPackage(ml, pkg, node)

                    # In case package is not managed and is a user added package, then managedVersion is
                    # set to userAdded version instead of 'N/A'
                    if managedV == 'N/A' and userAddedVersion != 'N/A':
                        managedV = userAddedVersion
                    pkg['managedPackageVersion'] = managedV
                    if managedP:
                        # We allow package to be added to ManagedList.json userPackages section:
                        # 1. If package is installed , but update of a package is available
                        # i.e. (updateVersion > installedVersion)
                        # 2. If package is not installed, but updateVersion is greater than managedVersion.
                        # 3. If package is not installed , but update is available.

                        if ('installedVersion' in pkg and pkg['installedVersion'] and \
                            pkg['installedVersion'] != "N/A") and \
                            ('updateVersion' in pkg and pkg['updateVersion'] and \
                            pkg['updateVersion'] != "N/A"):
                            if LooseVersion(pkg['updateVersion']) > LooseVersion(pkg['installedVersion']):
                                isAddable = True

                        if (('installedVersion' in pkg and pkg['installedVersion'] and pkg['installedVersion'] == "N/A") \
                               and managedV != "N/A") and ('updateVersion' in pkg and pkg['updateVersion'] and \
                                              pkg['updateVersion'] != "N/A"):
                            if LooseVersion(pkg['updateVersion']) > LooseVersion(managedV):
                                isAddable = True

                        if ('installedVersion' in pkg and pkg['installedVersion'] and pkg['installedVersion'] == "N/A") and \
                           ( managedV != "N/A" or pkg['updateVersion'] and pkg['updateVersion'] != "N/A") :
                            isAddable = True

                        if ('updateVersion' in pkg and pkg['updateVersion'] and pkg['updateVersion'] == managedV):
                            isAddable = False

                        if removablePackage == "Yes":
                           # User will be allowed to remove a package if the package is removable and is installed
                            if 'installedVersion' in pkg and pkg['installedVersion'] and \
                                pkg['installedVersion'] != "N/A":
                                isRemovable = True

                    if isAddable or isRemovable:
                        enableCheckBox = True
                    pkg['isAddable'] = isAddable
                    pkg['isRemovable'] = isRemovable
                    pkg['removablePackage'] = removablePackage
                    pkg['enableCheckBox'] = enableCheckBox
                    packageList.append(pkg)
                    logger.debug("listCallback: pkg=%-30s installedVers=%s managedV=%s enableCheckbox=%s" %
                                 (pkg['pkg_name'], pkg['installedVersion'], pkg['managedPackageVersion'], pkg['enableCheckBox']))
            except KeyError:
                return json.jsonify(status="failure", error=results['error'] ), 404

    # Start of listManagedPackages

    try:
        distro = request.args.get("distro", "")
    except KeyError:
        return json.jsonify(status="failure", error="missing distro argument"), 400

    try:
        package = request.args.get("package", "")
    except KeyError:
        return json.jsonify(status="failure", error="missing package argument"), 400

    logger.debug("In listManagedPackages, distro=%s package=%s" % (distro, package))

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

    arg_list = []
    for node in nodes:
        cv['cnt'] += 1
        if  package == "":
            arg_list.append(([packageNames, node, cv], {}))
            methodName = listPackageForSingleSlave_common
        else:
            arg_list.append(([node, package, configXmlFilePath, jobNameSuffix, cv],{}))
            methodName = createJob_SingleSlavePanel_Common

    logger.debug("listManagedPackages, methodName=%s arg_list=%s" % (methodName, arg_list))

    threadRequests = makeRequests(methodName, arg_list, listCallback)

    cv['cv'].acquire()
    [globals.threadPool.putRequest(req) for req in threadRequests]
    while cv['cnt']:
        cv['cv'].wait()
    cv['cv'].release()

    for data in cv['results']:
        if data:
            listCallback(data)

    logger.debug("listManagedPackages, cnt packages[]=%s" % str(len(packageList)))

    return json.jsonify(status="ok", packages=packageList)

# Add package selected by user to the local Managed List
@app.route("/autoport/addToManagedList", methods=["POST"])
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
@app.route("/autoport/removeFromManagedList", methods=["POST"])
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
@app.route("/autoport/synchManagedPackageList")
def synchManagedPackageList():
    try:
        nodes = request.args.get("serverNodeCSV", "")
    except KeyError:
        return json.jsonify(status="failure", error="missing serverNodeCSV argument"), 400

    if nodes == "":
        return json.jsonify(status="failure", error="No node selected"), 400

    path = sharedData.synchManagedPackageList()

    if not path:
        return json.jsonify(status="failure", error="Could not synch the managed list.  Try again." )

    jobs, jobNode = createSynchJobs(nodes)

    return json.jsonify(status="ok",
           message= str(len(jobs)) + " installation job(s) initiated in the background...", jobList = jobNode)

def createSynchJobs(nodes):
    '''
    This routine is responsible to get appropriate chef-attributes
    and list of recipes to be run on selected build slave.
    args:
       nodes variable holds the comma-seperated list of node-labels
    return:
       jobs: list of chef jobs created , i.e one job per node.
    '''

    # dict to hold job names of all the chef jobs to be monitored
    jobs = []
    jobNode = []
    try:
        serverNodes = nodes.split(",")
        for serverNode in serverNodes:
            for node in globals.nodeDetails:
                if node['nodelabel'] == serverNode:
                    # Getting chef attributes and run_list for the node
                    chefAttr, runList, numberOfInstalls,numberOfUnInstalls = chefData.setChefDataForSynch(node['distro'],
                                                                            node['rel'], node['arch'])
                    # Creating chef job for the node.
                    job = createChefJob(node['hostname'], node['ipaddress'], chefAttr, runList, "managed-package")
                    try:
                        if job['status'] == "success":
                            jobs.append(job['jobName'])
                            jobNode.append({'jobName':job['jobName'], 'nodeLabel': node['nodelabel'],\
                                            'install': numberOfInstalls, 'uninstalls':numberOfUnInstalls })
                    except KeyError as e:
                        print str(e)
                        assert(False)
    except KeyError as e:
        print str(e)
        assert(False)

    # Invoking the routine to monitor the chef jobs created above as
    # a separate thread running in the background.  There are no artifacts to be transferred
    threadRequests = makeRequests(monitorChefJobs, jobs)
    [globals.threadPool.putRequest(req) for req in threadRequests]

    # After the synch operation the ManagedList is cleanedup , to remove entries
    # of packages which were meant to be uninstalled (action:'remove')
    for serverNode in serverNodes:
        for node in globals.nodeDetails:
            sharedData.cleanUpManagedList(node['distro'], node['rel'], node['arch'])

    return jobs, jobNode

def createChefJob(host, ipaddress, chefAttr, runList, jobType="single-package"):
    tree = ET.parse("./config_template_knife_bootstrap.xml")
    root = tree.getroot()

    # Job is always triggered on the chef-workstation , and hence assigned node is always master.
    xml_node = root.find("./assignedNode")
    xml_node.text = "master"

    xml_parameters = root.findall("./properties/hudson.model.ParametersDefinitionProperty/parameterDefinitions/hudson.model.StringParameterDefinition/defaultValue")

    i =1

    # In case of sync operation we have to set four build parameters (chefInstallAttr,chefRemoveAttr
    # ,chefInstallRecipes, chefRemoveRecipes) ,corresponding to remove and install operations that are taken care through
    # seperate knife bootstrap commands.
    # However, in case of installation/removal done via single panel requires only 2 build parameters to be set.
    if isinstance(chefAttr, list) and isinstance(runList, list):
       for param in xml_parameters:
            if i == 1:
                param.text = host
            elif i == 2:
                param.text = ipaddress
            elif i == 3:
                param.text = json.dumps(chefAttr[0])
            elif i == 4:
                param.text = json.dumps(runList[0])
            elif i == 5:
                param.text = json.dumps(chefAttr[1])
            elif i == 6:
                param.text = json.dumps(runList[1])
            i += 1
    else:
        for param in xml_parameters:
            if i == 1:
                param.text = host
            elif i == 2:
                param.text = ipaddress
            elif i == 3:
                param.text = json.dumps(chefAttr)
            elif i == 4:
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


@app.route("/autoport/monitorJob", methods=["GET"])
def monitorJob():
    '''
    monitorJob: monitors the jenkins job run for job name
    inputs: HTTP GET param jobName: holds the jobName
            HTTP GET param nodeLabel: holds the nodeLabel
    '''
    status = ""
    requestJobName = request.args.get("jobName", "")
    nodeLabel = request.args.get("nodeLabel", "")
    if requestJobName:
       status = monitorChefJobs(requestJobName, sync=True)
    return json.jsonify(status="ok", jobstatus=status, nodeLabel=nodeLabel)

def monitorChefJobs(jobName, sync=False):
    # Monitor each job in chefJobs
    building = True
    checkBuildUrl = globals.jenkinsUrl + "/job/" + jobName + "/lastBuild/api/json"
    while building:
        try:
            requestInfo = requests.get(checkBuildUrl)
            if requestInfo.status_code == 200:
                buildInfo = json.loads(requests.get(checkBuildUrl).text)
                building = buildInfo['building']
            if building:
                sleep(3)

            if not building:
                jobStatus = buildInfo['result']
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
                    if sync == True:
                    #emit('my response', {'data': 'FAILURE'})
                        return "FAILURE"
                count += 1
            building = False

    consoleLog = globals.jenkinsUrl + "/job/" + jobName + "/lastBuild/consoleText"
    log = str(requests.get(consoleLog).text)
    logfile = open(globals.localPathForChefLogs + jobName, 'w')
    logfile.write(log)
    logfile.close()

    if jobStatus == 'SUCCESS':
        if sync == True:
            return "SUCCESS"
    else:
        if sync == True:
            return "FAILURE"

# Read and sanitize the contents of the named batch file
@app.route("/autoport/parseBatchFile")
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
@app.route("/autoport/listTestResults/<repositoryType>")
def listTestResults(repositoryType):
    try:
        filt = request.args.get("filter", "")
        if repositoryType != "gsa" and repositoryType != "local" and repositoryType != "all":
            return json.jsonify(status="failure", error="Invalid repository type"), 400
        return json.jsonify(status="ok", results=catalog.listJobResults(repositoryType, filt.lower()))
    except Exception as e:
        return json.jsonify(status="failure", error=str(e)), 401

# Removes projects data from local or GSA
@app.route("/autoport/removeProjects", methods=["POST"])
def removeProjects():
    try:
        project = Project(catalog)
        projects = request.json['projects']
        catalog.removeProjectsData(projects, project)
        return json.jsonify(status="ok"), 200
    except Exception as e:
        return json.jsonify(status="failure", error=str(e)), 401

# Get the jenkins build output
# /getBuildResults?left=x&right=y
@app.route("/autoport/getTestResults")
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
        return json.jsonify(status="failure", error="Result not found"), 401

    try:
        rightname = resultPattern.match(rightbuild).group(2)
    except AttributeError:
        return json.jsonify(status="failure", error="Invalid test result name " + rightbuild), 402

    try:
        leftname = resultPattern.match(leftbuild).group(2)
    except AttributeError:
        return json.jsonify(status="failure", error="Invalid test result name " + leftbuild), 403

    try:
        res = resParser.ResBuildCompare(leftname, leftdir, rightname, rightdir)
    except BaseException as e:
        logger.debug("getTestResults: failed resBuildCompare")
        return json.jsonify(status="failure", error=str(e)), 500

    lf = open(leftdir+"/meta.arti")
    try:
        leftmeta = json.load(lf)
    except Exception as e:
        logger.debug("getTestResults: leftbuild json Error=%s" % str(e))
        return json.jsonify(status="failure", error="Corrupted meta data name " + leftbuild), 404
    finally:
        lf.close()

    rf = open(rightdir+"/meta.arti")
    try:
        rightmeta = json.load(rf)
    except Exception as e:
        logger.debug("getTestResults: json rightbuild Error=%s" % str(e))
        return json.jsonify(status="failure", error="Invalid test result name " + rightbuild), 405
    finally:
        lf.close()

    catalog.cleanTmp()
    return json.jsonify(status = "ok",
                        leftCol = leftname,
                        rightCol = rightname,
                        leftProject = leftmeta,
                        rightProject = rightmeta,
                        results = res)

# Get diff log output
@app.route("/autoport/getDiffLogResults")
def getDiffLogResults():
    logFile  = request.args.get("logfile", "")
    leftBuild  = request.args.get("leftbuild", "")
    rightBuild = request.args.get("rightbuild", "")
    leftRepo = request.args.get("leftrepository", "local")
    rightRepo = request.args.get("rightrepository", "local")

    logs = project.getDiffLogResult(logFile, leftBuild, rightBuild, leftRepo, rightRepo)

    if logs.has_key('error'):
        return json.jsonify(
            status = "failure",
            error = logs.get("error", "Something went wrong")
        ), logs.get("http_code", 500)
    else:
        return json.jsonify(
            status = "ok",
            leftCol = logs.get("leftCol", []),
            rightCol = logs.get("rightCol", []),
            results = logs.get("results", [])
        )

# Get diff log output
@app.route("/autoport/getDiffBatchLogResults", methods=["POST"])
def getDiffBatchLogResults():
    leftBatch  = request.json.get("leftbatch", "")
    rightBatch = request.json.get("rightbatch", "")
    leftRepo = request.json.get("leftrepo", "local")
    rightRepo = request.json.get("rigthrepo", "local")
    logFile = request.json.get("logfile", "test_result.arti")

    logs = batch.getBatchDiffLogResults(leftBatch, rightBatch, leftRepo, rightRepo, catalog, logFile)

    if logs.has_key('error'):
        return json.jsonify(
            status = "failure",
            error = logs.get("error", "Something went wrong")
        ), logs.get("http_code", 500)
    else:
        return json.jsonify(
            status = "ok",
            results = logs
        )

@app.route("/autoport/getTestHistory", methods=["POST"])
def getTestHistory():
    projects = request.json['projects']

    # projects = { <job 1> : <job 1's repo>, <job 2> : <job 2's repo>, ... }
    # The key name is always a project.  The value of the key is "gsa" or "local"

    logger.debug("In getTestHistory, projects=%s" % projects)

    out = []
    repoType = ""
    projectNames = []
    for name in projects.keys():
        p = resultPattern.match(name)
        try:
            pkg = p.group(4)                         # ie. junit
            ver = p.group(5)                         # ie. current
        except AttributeError:
            continue
        if not [pkg, ver] in projectNames:
            repoType = projects[name]
            projectNames.append([pkg, ver])
        elif projects[name] != repoType:
            repoType = "all"

    logger.debug("getTestHistory: repoType=%s, projectNames=%s" % (repoType, str(projectNames)))

    jobRes = catalog.listJobResults(repoType, "")
    for projectName in projectNames:
        prjOut = []
        for prj in jobRes:
            if projectName[0] == prj['name'] and projectName[1] == prj['version']:
                resultDir = catalog.getResults(prj['fullName'], prj['repository'])
                try:
                    if resultDir and os.path.isfile(resultDir + "/test_result.arti"):
                        prjRes = resParser.resultParser(resultDir + "/test_result.arti")
                    else:
                        continue
                except BaseException as e:
                    logger.debug("getTestHistory: Error=%s" % str(e))
                    continue
                f = open(resultDir + "/meta.arti")
                try:
                    meta = json.load(f)
                except Exception as e:
                    logger.debug("getTestHistory: json Error=%s" % str(e))
                    continue
                finally:
                    f.close()
                prjOut.append({
                    "name": prj['fullName'],
                    "repository": prj['repository'],
                    "project": meta,
                    "results": prjRes})
                logger.debug("getTestHistory: name=%s, results=%s" % (prj['fullName'], prjres))
        out.append({
            "name": "Test results for project " + projectName[0] + "-" + projectName[1],
            "results": prjOut
        })
    catalog.cleanTmp()

    if not out:
        return json.jsonify(status="failure", error="build failed, no test results"), 500

    return json.jsonify(status = "ok", results = out)

@app.route("/autoport/getTestDetail", methods=["POST"])
def getTestDetail():
    projects = request.json['projects']
    logger.debug("In getTestDetail, projects=%s" % projects)
    out = []
    for projectName in projects:
        repo = projects[projectName]
        resultDir = catalog.getResults(projectName, repo)
        try:
            if resultDir and os.path.isfile(resultDir+"/test_result.arti"):
                res = resParser.resultParser(resultDir+"/test_result.arti")
            else:
                return json.jsonify(status="failure", error="build failed, no test results"), 500
        except BaseException as e:
            return json.jsonify(status="failure", error=str(e)), 500

        f = open(resultDir + "/meta.arti")
        try:
            meta = json.load(f)
        except Exception as e:
            logger.debug("getTestDetail: json Error=%s" % str(e))
            continue
        finally:
            f.close()

        # Validate that the directory looks like a test result
        p = resultPattern.match(projectName)
        try:
            pkg = p.group(4)                         # ie. N-junit
            ver = p.group(5)                         # ie. current
        except AttributeError:
            continue

        out.append({ "job": projectName, "pkg" : pkg, "ver": ver,
                     "results": res, "project": meta, "repository": repo })
        logger.debug("getTestDetail: name=%s, results=%s" % (projectName, res))
    catalog.cleanTmp()
    return json.jsonify(status = "ok", results = out)

@app.route("/autoport/archiveBatchFile", methods=["POST"])
def archiveBatchFile():
    try:
        filename = request.form["filename"]
    except KeyError:
        return json.jsonify(status="failure", error="missing filename POST argument"), 400

    res = batch.archiveBatchFile(filename)

    if res != None:
        return json.jsonify(status="failure", error=res['error'])
    return json.jsonify(status="ok")

@app.route("/autoport/archiveProjects", methods=["POST"])
def archiveProjects():
    projects = request.json['projects']
    status, errors, alreadyThere = catalog.archiveResults(projects)
    return json.jsonify(status=status, error=errors, alreadyThere=alreadyThere)

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
@app.route('/autoport/uploadToRepo', methods=['GET','POST'])
def uploadToRepo():
    postedFile = dict(request.files)
    # sourceType input from combobox
    packageDetails = request.form["packageDetails"]
    try:
        file = postedFile['packageFile'][0]
    except KeyError:
        return json.jsonify(status="failure",
                    error="No File selected for upload"), 400

    # Checking package extension before uploading
    if file and sharedData.getPkgExtensions(file.filename):
        status_msg = sharedData.uploadPackage(file, packageDetails)
        if status_msg:
           return json.jsonify(status="failure",
                error=status_msg), 400
        else:
            return json.jsonify(status="ok")
    else:
        return json.jsonify(status="failure",
                error="Inappropriate file-type"), 400

# Will fetch and return batch test details for given Batch names.
@app.route('/autoport/getBatchTestDetails', methods=['GET', 'POST'])
def getBatchTestDetails():
    batchList = request.json['batchList']
    batchDetails = batch.getBatchTestDetails(batchList, catalog)
    if batchDetails.has_key('error'):
        return json.jsonify(status=batchDetails['status'], error = batchDetails['error']), 400
    else:
        return json.jsonify(status=batchDetails['status'], results = batchDetails)

def autoportJenkinsInit(jenkinsUrl, jenkinsUsername, jenkinsKey):
    # This is called before starting the flask application.  It is responsible
    # for performing initial setup of the Jenkins master.  Only required items
    # should be performed here.  On error, messages are printed to the console
    # and assert(False) is invoked to provide the debug context.
    if jenkinsUrl:
        # Start threads as getJenkinsNodeDetails uses thread pool
        mover.start(urlparse(jenkinsUrl).hostname, jenkinsUsername, jenkinsKey)

        # Get new jenkins node information
        globals.nodeNames, globals.nodeLabels = getJenkinsNodes_init()
        getJenkinsNodeDetails_init()

        sharedData.connect(urlparse(jenkinsUrl).hostname)
        sharedData.uploadChefData()
        chefData.setRepoHost(urlparse(globals.jenkinsUrl).hostname)

def autoportUserInit(hostname, jenkinsUrl, configUsername, configPassword):
    if hostname and configUsername and configPassword :
        if globals.gsaConnected:
            catalog.close()
            batch.disconnect()
        if jenkinsUrl:
            catalog.connect(hostname, urlparse(jenkinsUrl).hostname, archiveUser=configUsername, archivePassword=configPassword)
        batch.connect(hostname, globals.port, archiveUser=configUsername, archivePassword=configPassword)
    # XXX catalog needs a disconnect

if __name__ == "__main__":
    # When the server instance is freshly started clear up all the /tmp/ directories created by the application
    # in previous run, that were not cleaned up.
    for dirname, dirnames, filenames in os.walk('/tmp/'):
        if dirname.startswith('/tmp/autoport_'):
            logger.debug("Deleting: " + dirname)
            shutil.rmtree(dirname, ignore_errors=True)

    p = argparse.ArgumentParser()
    p.add_argument("-p", "--public", action="store_true",
                   help="specifies for the web server to listen over the public network,\
                   defaults to only listening on private localhost")
    p.add_argument("-u", "--jenkinsURL", help="specifies the URL for the Jenkins server,\
                   defaults to '" + globals.jenkinsUrl + "'")
    p.add_argument("-b", "--allocBuildServers", action="store_true",
                   help="Build Servers are dynamically allocated per user")
    p.add_argument("-d", "--debug", action="store_true",
                   help="Set debug mode")
    args = p.parse_args()

    if args.jenkinsURL:
        globals.jenkinsUrl = args.jenkinsURL

    if args.allocBuildServers:
        globals.allocBuildServers = args.allocBuildServers

    autoportJenkinsInit(globals.jenkinsUrl, globals.configJenkinsUsername, globals.configJenkinsKey)
    autoportUserInit(globals.hostname,globals.jenkinsUrl,globals.configUsername,globals.configPassword)

    hostname = "127.0.0.1"
    if args.public:
        hostname = globals.localHostName
    print "You may use your browser now - http://%s:5000/autoport/" % (hostname)

    if args.public:
        app.run(threaded=True, host='0.0.0.0')
    else:
        app.run(debug = args.debug)
