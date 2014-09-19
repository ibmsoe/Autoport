# Imports
import xml.etree.ElementTree as ET
import requests
import webbrowser
from flask import Flask, request, render_template, json
from github import Github
from classifiers import classify
from buildAnalyzer import inferBuildSteps
from cache import Cache

# Config
jenkinsUrl = "http://soe-test1.aus.stglabs.ibm.com:8080"

# Globals
app = Flask(__name__)
github = Github("9294ace21922bf38fae227abaf3bc20cf0175b08")
cache = Cache(github)

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

	for repo in github.search_repositories(query, **searchArgs)[:10]:
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
	build = inferBuildSteps(cache.getDir(repo)) # buildAnalyzer.py
	# Collect data
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
		"build": build
	}
	# Send
	return json.jsonify(status="ok", repo=repoData, type="detail")

# Create Job - takes a repo id and creates a Jenkins job for it
# Returns a JSON file with the new job URL on success
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

	# Read template XML file
	tree = ET.parse("config_template.xml")
	root = tree.getroot()
	# Find elements we want to modify
	xml_github_url = root.find(
		"./properties/com.coravy.hudson.plugins.github.GithubProjectProperty/projectUrl")
	xml_git_url = root.find(
		"./scm/userRemoteConfigs/hudson.plugins.git.UserRemoteConfig/url")
	xml_default_branch = root.find(
		"./scm/branches/hudson.plugins.git.BranchSpec/name")
	xml_command = root.find("./builders/hudson.tasks.Shell/command")

	# Get repository
	repo = cache.getRepo(id)

	# Infer build steps if possible
	build = inferBuildSteps(cache.getDir(repo))

	# Modify selected elements
	xml_github_url.text = repo.html_url
	xml_git_url.text = "https" + repo.git_url[3:]
	xml_default_branch.text = "*/" + repo.default_branch
	if build['success']:
		xml_command.text = build['steps']

	# Add header to the config
	configXml = "<?xml version='1.0' encoding='UTF-8'?>\n" + ET.tostring(root)

	jobName = "(PortAutoTool) " + repo.name

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
		# Success, send new job URL as response
		jobUrl = jenkinsUrl + "/job/" + jobName + "/"
		webbrowser.open_new_tab(jobUrl)
		return #json.jsonify(status="ok", returnUrl=returnUrl)

	return json.jsonify(status="failure", error="jenkins error")

if __name__ == "__main__":
    app.run(debug = True)