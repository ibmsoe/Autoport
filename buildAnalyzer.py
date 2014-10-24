# Looks for certain files (e.g. Makefile) and returns the corresponding build
# steps
def inferBuildSteps(listing, repo):
    for f in listing:
        if f.name == "build.sh":
            return {
                'build system': "custom build script",
                'build': "./build.sh",
                'test' : "make all",
                'env' : "",
                'artifacts': "", 
                'reason': "build.sh",
                'success': True
            }
        elif f.name == "Makefile":
            return {
                'build system': "make",
                'build': "./configure; make",
                'test' : "make all",
                'env' : "",
                'artifacts': "", 
                'reason': "Makefile",
                'success': True
            }
        elif f.name == "build.xml":
            return {
                'build system': "ant",
                'build': "ant",
                'test' : "",
                'env' : "",
                'artifacts': "",
                'reason': "build.xml",
                'success': True
            }
        elif f.name == "pom.xml":
            # Get the readme
            readmeStr = repo.get_readme().content.decode('base64', 'strict')

            # Search for options related to maven
            opts = "MAVEN_OPTS" # maven options to look for
            delim = ["`", "\n"] # delimeters used to denote end of option
            strFound = buildFilesParser(readmeStr, opts, delim)
            
            if strFound != "":
                maven_export = "export " + strFound + "; " # export command to be appended to the front of the build command
            else:
                maven_export = ""
                    
            return {
                'build system': "maven",
                'build': maven_export + "mvn dependency:list -DexcludeTransitive > dependency.arti; mvn clean compile",
                'test' : "mvn test -fn > test_result.arti",
                'env' : '',
                'artifacts': "*.arti",
                'reason': "pom.xml",
                'success': True
            }
    return {'success': False}

# Build Files Parser - Looks for string searchTerm in string fileBuf and then iterates over
# list of delimeters and finds the one with the smallest index, returning the string found between the
# two indices
def buildFilesParser(fileBuf, searchTerm, delimeter):
    # Get the length of the file     
    lenFileBuf = len(fileBuf)

    # Search the fileBuf for searchTerm
    i = fileBuf.find(searchTerm)
    
    if i != -1:
        smallestIndex = lenFileBuf # this is one bigger than the biggest index, acts as infinity
        # If searchTerm found find the smallest index delimeter
        for delim in delimeter:
            if smallestIndex < lenFileBuf:
                j = fileBuf[i:].find(delim, 0, smallestIndex)
            else:
                j = fileBuf[i:].find(delim)

            if j != -1:
                smallestIndex = j

        # If smallest index is smaller than the length of the searchTerm we found a delimeter
        if smallestIndex < lenFileBuf:
            return fileBuf[i:][:smallestIndex]

    return ""
