# Looks for certain files (e.g. Makefile) and returns the corresponding build
# steps
def inferBuildSteps(listing, repo):
    for f in listing:
        if f.name == "build.sh":
            return {
                'build': "./build.sh",
                'test' : "make all",
                'env' : "",
                'dependency': "", 
                'reason': "build.sh",
                'success': True
            }
        elif f.name == "Makefile":
            return {
                'build': "./configure; make",
                'test' : "make all",
                'env' : "",
                'dependency': "", 
                'reason': "Makefile",
                'success': True
            }
        elif f.name == "build.xml":
            return {
                'build': "ant",
                'test' : "",
                'env' : "",
                'dependency': "",
                'reason': "build.xml",
                'success': True
            }
        elif f.name == "pom.xml":
            # Get the readme
            s = repo.get_readme().content.decode('base64', 'strict')

            opts = "MAVEN_OPTS" # maven options to look for
            delim = "\n" # delimeter used to denote end of option
            maven_export = "" # export command to be appended to the front of the build command

            # Search the readme for opts
            i = s.find(opts)

            if i != -1:
                # If opts found find the delimeter
                j = s[i:].find(delim)

                if j != -1:
                    # If delimeter found store export command
                    maven_export = "export " + s[i:][:j] + "; "
                    
            return {
                'build': maven_export + "mvn dependency:list -DexcludeTransitive > dependency_artifacts.txt; mvn clean compile",
                'test' : "mvn test -fn",
                'env' : 'JAVA_HOME=/opt/ibm/java-ppc64le-71',
                'dependency': "dependency_artifacts.txt",
                'reason': "pom.xml",
                'success': True
            }
    return {'success': False}
