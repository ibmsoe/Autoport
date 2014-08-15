import datetime

# Define classification constants
GOOD = 1
NEUTRAL = 2
BAD = 3
UNCERTAIN = 4

# Creates simple classifiers for star, fork, size, date properties
def makeSimpleClassifier(higherIsBetter, neutralCount, goodCount):
	if higherIsBetter:
		def classifier(value):
			if value > goodCount:
				return GOOD
			elif value > neutralCount:
				return NEUTRAL
			else:
				return BAD
		return classifier
	else:
		def classifier(value):
			if value < goodCount:
				return GOOD
			elif value < neutralCount:
				return NEUTRAL
			else:
				return BAD
		return classifier

# Setup classifier functions
star = makeSimpleClassifier(True, 500, 1000)
fork = makeSimpleClassifier(True, 150, 400)
size = makeSimpleClassifier(False, 500000, 200000)
date = makeSimpleClassifier(False, 60, 30)

def lang(language):
	if language in ['C', 'C++', 'Objective-C']:
		return BAD
	elif language in ['Shell', 'Java', 'C#', 'Scala', 'Go']:
		return NEUTRAL
	elif language in ['JavaScript', 'Ruby', 'PHP', 'Python', 'Dart', 'Lua']:
		return GOOD
	return UNCERTAIN

def classify(repo):
	daysSinceLastUpdate = (datetime.datetime.utcnow() - repo.updated_at).days
	return {
		'stars': star(repo.stargazers_count),
		'forks': fork(repo.forks_count),
		'language': lang(repo.language),
		'size': size(repo.size),
		'date': date(daysSinceLastUpdate)
	}