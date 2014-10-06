# Looks for certain files (e.g. Makefile) and returns the corresponding build
# steps
def inferBuildSteps(listing):
	for f in listing:
		if f.name == "Makefile":
			return {
				'build': "./configure\nmake\n",
				'test' : "make all",
				'env' : "",
				'dependency': "", #place holder
				'reason': "Makefile",
				'success': True
			}
		elif f.name == "build.xml":
			return {
				'build': "ant",
				'test' : "", #place holder
				'env' : "",
				'dependency': "", #place holder
				'reason': "build.xml",
				'success': True
			}
		elif f.name == "pom.xml":
			return {
				'build': "mvn dependency:list -DexcludeTransitive > dependency_artifacts.txt; mvn clean compile",
				'test' : "mvn test",
				'env' : 'JAVA_HOME=/opt/ibm/java-ppc64le-71',
				'dependency': "dependency_artifacts.txt",
				'reason': "pom.xml",
				'success': True
			}
	return {'success': False}