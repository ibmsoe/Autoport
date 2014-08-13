from flask import Flask, request, render_template, json
from github import Github
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
			"language": repo.language
		})
	return json.jsonify(status="ok", results=results)

@app.route("/createJob", methods=['POST'])
def createJob():
	# Ensure we have all the post arguments we need
	try:
		name = request.form["name"]
		github_url = request.form["github_url"]
		git_url = request.form["git_url"]
	except KeyError:
		return json.jsonify(status="failure",
			error="missing name, github_url, or git_url")
		
	return json.jsonify(status="ok")

if __name__ == "__main__":
    app.run(debug = True)