#!/usr/bin/env python

# Imports
import xml.etree.ElementTree as ET
import requests
import re
import argparse
import datetime
from flask import Flask, request, render_template, json
from github import Github
from classifiers import classify
from buildAnalyzer import inferBuildSteps
from cache import Cache
from os import path, makedirs

# Config
jenkinsUrl = "http://soe-test1.aus.stglabs.ibm.com:8080"
jobNamePrefix = "AutoPortTool"

# Globals
upload_folder = "./uploads/"

app = Flask(__name__)
github = Github("9294ace21922bf38fae227abaf3bc20cf0175b08")
cache = Cache(github)
nodes = {'x86': "x86", 'ppcle': "ppcle"}
maxResults = 10

# Main page - just serve up main.html
@app.route("/")
def main():
    return render_template("main.html")

# Search - return a JSON file with search results or the matched
# repo if there's a solid candidate
@app.route("/search")
def search():
    # Get and validate arguments
    query = request.args.get("q", "")
    if query == "":
        return json.jsonify(status="failure", error="missing query")

    searchArgs = None # Used to pass in sort argument to pygithub
    sort = request.args.get("sort", "") # Check for optional sort argument
    if sort in ['stars', 'forks', 'updated']:
        searchArgs = {'sort': sort}
    elif sort == 'relevance' or sort == '':
        # Must pass no argument if we want to sort by relevance
        searchArgs = {}
    else:
        return json.jsonify(status="failure", error="bad sort type")

    autoselect = request.args.get("auto", "")
    if autoselect != "false":
        autoselect = True
    else:
        autoselect = False

    # Query Github and return a JSON file with results
    results = []
    isFirst = True
    numResults = maxResults

    repos = github.search_repositories(query, **searchArgs)

    if repos.totalCount == 0:
        # TODO - return no results page
        return json.jsonify(status="failure", error="no results")
    elif repos.totalCount <= maxResults:
        numResults = len(repos)

    for repo in repos[:numResults]: 
        cache.cacheRepo(repo)
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
    return json.jsonify(status="ok", results=results, type="multiple")

# Detail - returns a JSON file with detailed information about the repo
@app.route("/detail/<int:id>")
def detail(id, repo=None):
    # Get the repo if it wasn't passed in (from Search auto picking one)
    if repo is None:
        try:
            idInt = int(id)
        except ValueError:
            return json.jsonify(status="failure", error="bad id")
        repo = cache.getRepo(id)
    # Get language data
    languages = cache.getLang(repo)
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
    build = inferBuildSteps(cache.getDir(repo), repo) # buildAnalyzer.py
    # Collect data

    # Get list of tag names
    tags = []
    try:
        for tag in cache.getTags(repo):
            tags.append(tag.name)
    except TypeError:
        # PyGithub issue #278: Iterating through repo.get_tags() throws
        # NoneType TypeError for repositories with lots of tags:
        # https://github.com/jacquev6/PyGithub/issues/278
        print "ERROR: PyGithub threw a TypeError while iterating through tags"
    tags.sort(key=tagSortKey, reverse=True)

    if (not tags) or (len(tags) < 1):
        recentTag, tags = "",      ""
    elif len(tags) == 1:
        recentTag, tags = tags[0], ""
    else:
        recentTag, tags = tags[0], tags[1:]

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
    return json.jsonify(status="ok", repo=repoData, type="detail")


# Upload Batch File - takes a file and uploads it to a permanent location (TBD)
@app.route("/uploadBatchFile", methods=['GET', 'POST'])
def uploadBatchFile():
    try:
        fileStr = request.form["file"]
    except KeyError:
        return json.jsonify(status="failure", error="missing file")

    if not path.exists(upload_folder):
        makedirs(upload_folder)

    f = open(upload_folder + "batch_file." + str(datetime.datetime.today()), "w")
    f.write(fileStr)

    return json.jsonify(status="ok")

# Create Job - takes a repo id, repo tag, and arch and creates a Jenkins job for it
# Opens a new tab with a new jenkins job URL on the client side on success,
# while the current tab stays in the same place.
@app.route("/createJob", methods=['GET', 'POST'])
def createJob():
    # Ensure we have a valid id number as a post argument
    try:
        idStr = request.form["id"]
    except KeyError:
        return json.jsonify(status="failure",
            error="missing repo id")

    try:
        id = int(idStr)
    except ValueError:
        return json.jsonify(status="failure",
            error="invalid id number")

    # Ensure we have a valid architecture as a post argument
    try:
        arch = request.form["arch"]
    except KeyError:
        return json.jsonify(status="failure", error="missing arch")

    # Check to see if we have a valid tag number as a post argument    
    try:
        tag = request.form["tag"]
    except KeyError:
        tag = "Current"
    
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
    xml_dependency_artifact = root.find("./publishers/hudson.tasks.ArtifactArchiver/artifacts")
    xml_node = root.find("./assignedNode")

    # Get repository
    repo = cache.getRepo(id)

    # Infer build steps if possible
    build = inferBuildSteps(cache.getDir(repo), repo)

    # Modify selected elements
    archName = ""
    if arch == "x86":
        xml_node.text = nodes['x86']
        archName = "x86"
    elif arch == "ppcle":
        xml_node.text = nodes['ppcle']
        archName = "ppcle"

    xml_github_url.text = repo.html_url
    xml_git_url.text = "https" + repo.git_url[3:]

    jobName = jobNamePrefix + ' - ' + archName + ' - ' + repo.name

    if (tag == "") or (tag == "Current"):
        xml_default_branch.text = "*/" + repo.default_branch
        jobName += "-current"
    else:
        xml_default_branch.text = "tags/" + tag
        jobName += "-" + tag

    if build['success']:
        xml_build_command.text = build['build']
        xml_test_command.text = build['test']
        xml_env_command.text = build['env']
        xml_dependency_artifact.text = build['dependency']

    # Add header to the config
    configXml = "<?xml version='1.0' encoding='UTF-8'?>\n" + ET.tostring(root)

    # Send to Jenkins
    r = requests.post(
        jenkinsUrl + "/createItem",
        headers={
            'Content-Type': 'application/xml'
        },
        params={
            'name': jobName
        },
        data=configXml
    )

    if r.status_code == 200:
        # Success, send the jenkins job and start it right away.
        startJobUrl = jenkinsUrl + "/job/" + jobName + "/build?delay=0sec"

        # But then redirect to job home to monitor job progress.
        homeJobUrl = jenkinsUrl + "/job/" + jobName + "/"

        # Stays on the same page, after creating a new jenkins job.
        return json.jsonify(status = "ok", sjobUrl = startJobUrl, hjobUrl = homeJobUrl)

    return json.jsonify(status = "failure", error = 'jenkins error')

def tagSortKey (tagName):
    m = re.search(r'\d+(\.\d+)+', tagName)
    if m:
        return map(int, m.group().split('.'))
    else:
        return [0,0,0,0]

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("-p", "--public",               action="store_true", help="specifies for the web server to listen over the public network, defaults to only listening on private localhost")
    p.add_argument("-u", "--jenkinsURL",                                help="specifies the URL for the Jenkins server, defaults to '" + jenkinsUrl + "'")
    p.add_argument("-n", "--jenkinsJobNamePrefix",                      help="specifies a string to prefix to the Jenkins job name, defaults to '" + jobNamePrefix + "'")
    args = p.parse_args()

    if args.jenkinsURL:
        jenkinsUrl = args.jenkinsURL
    if args.jenkinsJobNamePrefix:
        jobNamePrefix = args.jenkinsJobNamePrefix

    if args.public:
        app.run(debug = True, host='0.0.0.0')
    else:
        app.run(debug = True)
