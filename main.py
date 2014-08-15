# Imports
from flask import Flask, request, render_template, json
from github import Github
import xml.etree.ElementTree as ET
import requests
from classifiers import classify

# Config
jenkinsUrl = "http://soe-test1.aus.stglabs.ibm.com:8080"

app = Flask(__name__)

@app.route("/")
def main():
    return render_template("main.html")

@app.route("/search")
def search():
	# Get and validate query
	query = request.args.get("q", "")
	if query == "":
		return json.jsonify(status="failure", error="missing query")
	# Query Github and return a JSON file with results
	g = Github()
	results = []
	for repo in g.search_repositories(query)[:10]:
		results.append({
			"name": repo.name,
			"owner": repo.owner.login,
			"owner_url": repo.owner.html_url,
			"stars": repo.stargazers_count,
			"forks": repo.forks_count,
			"url": repo.html_url,
			"git_url": "https" + repo.git_url[3:],
			"size_kb": repo.size,
			"last_update": str(repo.updated_at),
			"language": repo.language,
			"default_branch": repo.default_branch,
			"classifications": classify(repo)
		})
	return json.jsonify(status="ok", results=results)

@app.route("/createJob", methods=['POST'])
def createJob():
	# Ensure we have all the post arguments we need
	try:
		name = "(PortAutoTool) " + request.form["name"]
		github_url = request.form["github_url"]
		git_url = request.form["git_url"]
		default_branch = request.form["default_branch"]
	except KeyError:
		return json.jsonify(status="failure",
			error="missing name, github_url, or git_url")

	# Read template XML file
	tree = ET.parse("config_template.xml")
	root = tree.getroot()
	xml_github_url = root.find(
		"./properties/com.coravy.hudson.plugins.github.GithubProjectProperty/projectUrl")
	xml_git_url = root.find(
		"./scm/userRemoteConfigs/hudson.plugins.git.UserRemoteConfig/url")
	xml_default_branch = root.find(
		"./scm/branches/hudson.plugins.git.BranchSpec/name")

	# Modify selected elements
	xml_github_url.text = github_url
	xml_git_url.text = git_url
	xml_default_branch.text = "*/" + default_branch

	#Send Jenkins the config file
	configXml = "<?xml version='1.0' encoding='UTF-8'?>\n" + ET.tostring(root)

	r = requests.post(
		jenkinsUrl + "/createItem",
		headers={
			'Content-Type': 'application/xml'
		},
		params={
			'name': name
		},
		data=configXml
	)

	if r.status_code == 200:
		# Success, send new job URL as response
		jobUrl = jenkinsUrl + "/job/" + name + "/"
		return json.jsonify(status="ok", jobUrl=jobUrl)

	return json.jsonify(status="failure", error="jenkins error")

if __name__ == "__main__":
    app.run(debug = True)