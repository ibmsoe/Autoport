import collections

# For storing language data
LangsTuple = collections.namedtuple('LangsTuple', ['repoName', 'data'])

class Cache:
	def __init__(self, github):
		self.github = github # PyGitHub wrapper
		self.repos = collections.deque(maxlen=128) # Cache repos
		self.langs = collections.deque(maxlen=128) # Cache language data

	# Returns a cached repo, or, if it's not in the cache
	# it will acquire, cache, and return it
	def getRepo(self, id):
		for repo in self.repos:
			if repo.id == id:
				return repo
		newRepo = github.get_repo(id)
		self.repos.append(newRepo)
		return newRepo

	# Caches the repository for later use
	def cacheRepo(self, repo):
		if not repo in self.repos:
			self.repos.append(repo)

	# Returns a cached language, or acquires and caches it if it's
	# not present in the cache.
	def getLang(self, repo):
		for langsTuple in self.langs:
			if langsTuple.repoName == repo.name:
				return langsTuple.data
		newLangs = repo.get_languages()
		self.langs.append(LangsTuple(repo.name, newLangs))
		return newLangs