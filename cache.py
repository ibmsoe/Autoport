import collections

RepoDataTuple = collections.namedtuple('RepoDataTuple', ['repoName', 'data'])

class Cache:
	def __init__(self, github):
		self.github = github # PyGitHub wrapper
		self.repos = collections.deque(maxlen=128) # Cache repos
		self.langs = collections.deque(maxlen=128) # Cache language data
		self.dirs = collections.deque(maxlen=128) # Cache directory structure data

	# Returns a cached repo, or, if it's not in the cache
	# it will acquire, cache, and return it
	def getRepo(self, id):
		# Is repo already in cache?
		for repo in self.repos:
			if repo.id == id:
				return repo
		# repo not in cache, so acquire it and add it
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
		# Is language data for repo already cached?
		for langsTuple in self.langs:
			if langsTuple.repoName == repo.name:
				return langsTuple.data
		# Not in cache, acquire and cache
		newLangs = repo.get_languages()
		self.langs.append(RepoDataTuple(repo.name, newLangs))
		return newLangs

	def getDir(self, repo):
		# Is directory already cached?
		for dirTuple in self.dirs:
			if dirTuple.repoName == repo.name:
				return dirTuple.data
		# Not in cache, acquire and cache
		newDir = repo.get_dir_contents('/')
		self.dirs.append(RepoDataTuple(repo.name, newDir))
		return newDir