# General strategy is to create a stack of language definitions from which build and test
# commands are generated.  The initial entry is the base language definition.  Subsequent
# entries are added based on the presense of specific build files enabling better command
# lines to be produced.  Ultimately, top of stack is returned.  In between, there is
# grepping of readme files based on hints provided by the various language definitions
# to improve command generation and discovery of environment variables.

def inferBuildSteps(listing, repo):

    # base_lang_def are added based on primary language designation.  Multiple build
    # tools should be supported if applicable. Script are run on the Jenkins build client
    # to invoke the appropriate build command. There is no ability to grep for environment
    # variables as these are specific to the build tool like maven and ant.

    base_python_def = {
        'build system': "Python",
        'grep build': "python setup.py build",	# Search readme for this string. If found, use it as build cmd
        'grep test': "py.test",			# Same for test command. Maybe we can pick up some extra arguments
        'grep env': "",
        'build' : "if [ -e setup.py ]; then python setup.py install; fi",
        'test' : "py.test",
        'env' : "",
        'artifacts': "",
        'reason': "primary language",
        'success': True }

    base_c_def = {
        'build system': "make",
        'grep build': "",
        'grep test': "make test",
        'grep env': "",
        'build': "if [ -x configure ]; then ./configure; fi; make clean; make",
        'test' : "make all",
        'env' : "",
        'artifacts': "",
        'reason': "primary language",
        'success': True }

    base_java_def = {
        'build system': "Java",
        'grep build': "",
        'grep test': "",
        'grep env': "",
        'build': "if [ -e pom.xml ]; then mvn clean compile; elif [ -e build.xml ]; then ant; elif [ -e build.gradle ]; then gradle -q; fi",
        'test': "if [ -e pom.xml ]; then mvn test -fn > test_result.arti; elif [ -e build.xml ]; then ant test; elif [ -e build.gradle ]; then gradle -q test; fi",
        'env' : "",
        'artifacts': "",
        'reason': "primary language",
        'success': True }

    base_empty_def = {
        'build system': "",
        'grep build': "",
        'grep test': "",
        'grep env': "",
        'build': "",
        'test' : "",
        'env' : "",
        'artifacts': "",
        'reason': "primary language unknown",
        'success': False }

    # These definitions are added based on the presense of a build file.  We can
    # simply the command line and and search for environment variables.

    ant_def = {
        'build system': "ant",
        'grep build': "ant clean; ant",
        'grep test': "ant test",
        'grep env': "ANT_OPTS",
        'build': "ant",
        'test' : "ant test",
        'env' : "",
        'artifacts': "",
        'reason': "build.xml",
        'success': True }

    maven_def = {
        'build system': "maven",
        'grep build': "",
        'grep test': "",
        'grep env': "MAVEN_OPTS",
        'build': "mvn dependency:list -DexcludeTransitive > dependency.arti; mvn clean compile",
        'test' : "mvn test -fn > test_result.arti",
        'env' : "",
        'artifacts': "*.arti",
        'reason': "pom.xml",
        'success': True }

    c_def = {
        'build system': "make",
        'grep build': "",
        'grep test': "make test",
        'grep env': "",
        'build': "if [ -x configure ]; then ./configure; fi; make clean; make",
        'test' : "make all",
        'env' : "",
        'artifacts': "",
        'reason': "Makefile",
        'success': True }

    # This is most favored definition and is added to top of stack

    buildsh_def = {
        'build system': "custom build script",
        'grep build': "build.sh",
        'grep test': "build.sh test",
        'grep env': "",
        'build': "./build.sh",
        'test' : "./build.sh test",
        'env' : "",
        'artifacts': "",
        'reason': "build.sh",
        'success': True }

    # Push base language definition based on primary language

    langstack = []
    if repo.language == 'Python':
        langstack.insert(0, base_python_def)
    elif repo.language == 'C':
        langstack.insert(0, base_c_def)
    elif repo.language == 'Java':
        langstack.insert(0, base_java_def)
    else:
        base_empty_def['build system'] = repo.language
        langstack.insert(0, base_empty_def)

    # Create a stack of readme files to grep
    grepstack = []
    try:
        readmeStr = repo.get_readme().content.decode('base64', 'strict')
    except IOError as e:
        return { 'success': False, 'error': "I/O error({0}): {1}".format(e.errno, e.strerror) }
    grepstack.insert(0, readmeStr)                 # may be a null pointer

    # Push additional definitions based on the presense of build files
    buildsh = None
    makefile = None
    for f in listing:
        if f.name == 'pom.xml':
            langstack.insert(0, maven_def)         # If we find specific build files we can improve our commands by grepping readme's 
        elif f.name == 'build.xml':
            langstack.insert(0, ant_def)
        elif f.name == 'Makefile':
            makefile = f
        elif f.name == 'build.sh' or f.name == 'run_build.sh':
            buildsh = f
#       elif f.name == 'BUILDING.md' or f.name == 'BUILDING.txt' or
#                      'README.maven' or f.name == 'README.ant':
#           fstr = pygithub get file content (f.name)
#           grepstack.insert(0, fstr)

    # build.sh is favored, because it bridges languages, sets environment variables, ...
    # Else if only the primary language definition is present, push Makefile as it may
    # apply to multiple languages.  It doesn't take precedence necessarily over a pom.xml
    # file but if one is not present we should fall back to the Makefile as it is better
    # than nothing.  The base java definition would not work!
    #
    # On the other hand, if both pom.xml and Makefile are present, then one could argue
    # that developers would favor makefiles as being simpler and better understood. Once
    # we have the ability to grep a Makefile we could scan it for Java or Python to
    # determine whether the makefile applies to multiple languages. For now, we assume
    # that it does. Later, we can conditionally push it to the lang stack.

    if buildsh != None:
        langstack.insert(0, buildsh_def)
#   elif len(langstack) == 1 and makefile != None:
    elif makefile != None:
        langstack.insert(0, c_def)

    delim = ["`", "'", '"', "\n"]                               # delimeters used to denote end of cmd

    # For now we just process the top of stack language, but we could process the
    # intermediate entries potentially to improve our grepping of build.sh...

    lang = langstack.pop(0)

    if lang['build'] != "":
        for readmeStr in grepstack:
            print "README: ", readmeStr
            if readmeStr != "":
                cmd = lang['grep test']
                if cmd != "":
                    print "GREP test cmd: ", cmd
                    strFound = buildFilesParser(readmeStr, cmd, delim)
                    print "GREP test str: ", strFound
                    if strFound != "":
                        lang['test'] = cmd                      # safe but loses extra cmd arguments possibly in strFound
#                       lang['test'] = strFound                 # TODO: needs to be validated.  May need to be sanitized
                cmd = lang['grep build']
                if cmd != "":
                    print "GREP build cmd: ", cmd
                    strFound = buildFilesParser(readmeStr, cmd, delim)
                    print "GREP build str: ", strFound
                    if strFound != "":
                        lang['build'] = cmd                     # safe but loses extra cmd arguments possibly in strFound
#                       lang['build'] = strFound	        # TODO: needs to be validated.  May need to be sanitized
                env = lang['grep env']
                if env != "":
                    print "GREP env cmd: ", env
                    strFound = buildFilesParser(readmeStr, env, delim)
                    print "GREP env str: ", strFound
#                   if strFound != "":                           # TODO: debug, can we provide this separately instead of 
#                       lang['build'] = strFound + lang['build']       # as part of the build and test command 
#                       lang['test'] = strFound + lang['test']         # need to sanitize strFound
                break

    print "BUILD: " + lang['build']
    print "TEST: " + lang['test']
    return lang

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
