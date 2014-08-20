# Looks for certain files (e.g. Makefile) and returns the corresponding build
# steps
def inferBuildSteps(repo):
	listing = repo.get_dir_contents('/')
	for f in listing:
		if f.name == "Makefile":
			return {
				'steps': "./configure\nmake\n",
				'reason': "Makefile",
				'success': True
			}
		elif f.name == "build.xml":
			return {
				'steps': "ant",
				'reason': "build.xml",
				'success': True
			}
		elif f.name == "pom.xml":
			return {
				'steps': "mvn clean compile",
				'reason': "pom.xml",
				'success': True
			}
	return {'success': False}