# Imports
from flask import Flask, request, render_template, json
from github import Github, PaginatedList
import xml.etree.ElementTree as ET
import requests
from classifiers import classify

# Config
jenkinsUrl = "http://soe-test1.aus.stglabs.ibm.com:8080"

# Globals
app = Flask(__name__)
github = Github()

@app.route("/")
def main():
    return render_template("main.html")

@app.route("/search")
def search():
	# Get and validate arguments
	query = request.args.get("q", "")
	if query == "":
		return json.jsonify(status="failure", error="missing query")

	searchArgs = None
	sort = request.args.get("sort", "")
	if sort in ['stars', 'forks', 'updated']:
		searchArgs = {'sort': sort}
	elif sort == 'relevance':
		# Must pass no argument if we want to sort by relevance
		searchArgs = {}
	else:
		return json.jsonify(status="failure", error="bad sort type")

	# Query Github and return a JSON file with results
	results = []
	isFirst = True
	print(searchArgs)
	for repo in github.search_repositories(query, **searchArgs)[:10]:
		if isFirst and repo.name == query and repo.stargazers_count > 500:
			return detail(repo.id, repo)
		isFirst = False
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

@app.route("/detail/<int:id>")
def detail(id, repo=None):
	if repo is None:
		try:
			idInt = int(id)
		except ValueError:
			return json.jsonify(status="failure", error="bad id")

		repo = github.get_repo(id)
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
		"description": repo.description,
		"classifications": classify(repo)
	}
	return json.jsonify(status="ok", repo=repoData, type="detail")

@app.route("/createJob", methods=['POST'])
def createJob():
	# Ensure we have all the post arguments we need
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
	xml_github_url = root.find(
		"./properties/com.coravy.hudson.plugins.github.GithubProjectProperty/projectUrl")
	xml_git_url = root.find(
		"./scm/userRemoteConfigs/hudson.plugins.git.UserRemoteConfig/url")
	xml_default_branch = root.find(
		"./scm/branches/hudson.plugins.git.BranchSpec/name")

	# Get repository
	repo = github.get_repo(id)

	# Modify selected elements
	xml_github_url.text = repo.html_url
	xml_git_url.text = "https" + repo.git_url[3:]
	xml_default_branch.text = "*/" + repo.default_branch

	#Send Jenkins the config file
	configXml = "<?xml version='1.0' encoding='UTF-8'?>\n" + ET.tostring(root)

	jobName = "(PortAutoTool) " + repo.name

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
		return json.jsonify(status="ok", jobUrl=jobUrl)

	return json.jsonify(status="failure", error="jenkins error")

if __name__ == "__main__":
    app.run(debug = True)