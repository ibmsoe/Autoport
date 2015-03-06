
# General strategy is to create a stack of language definitions from which build and test
# commands are generated.  Each successive definition that is added to the stack provides
# a better commnd line that is more specific to the project.  The last stack definition
# is returned. With a little luck, it is the preferred cmd line as provided by the readme

def inferBuildSteps(listing, repo):

    # This is added to the stack first.  Additional stack elements are added on top of it
    # as we perform discovery.  In the end, if we can't figure out how to build the project,
    # then this entry is used to convey the unknown primary language to the end user

    base_empty_def = {
        'build system': "",
        'primary lang': "",
        'grep build': "",
        'grep test': "",
        'grep env': "",
        'build': "",
        'test' : "",
        'env' : "",
        'artifacts': "",
        'reason': "primary language unknown",
        'error': "primary language unknown",
        'success': False }

    # These are the base lang definitions. They should cover the top two or three build
    # systems to achieve 60% or better compilation success.  The command line is not project
    # or build system specific.  Represents standard use of the build system, eg make all

    base_python_def = {
        'build system': "Python",
        'primary lang': "Python",
        'grep build': "python setup.py build",	# Search readme for this string. If found, use it as build cmd
        'grep test': "py.test",			# Same for test command. Maybe we can pick up some extra arguments
        'grep env': "",
        'build' : "if [ -e setup.py ]; then python setup.py install; fi",
        'test' : "py.test",
        'env' : "",
        'artifacts': "",                        # TODO: Need to specify a build artifact
        'reason': "primary language",
        'error': "",
        'success': True }

    base_ruby_def = {
        'build system': "Ruby",
        'primary lang': "Ruby",
        'grep build': "gem install %s"%(repo.name),
        'grep test': "rake test",
        'grep env': "",
        'build' : "bundle install; if [ -e Rakefile ]; then rake install; fi",
        'test' : "rake test",
        'env' : "",
        'artifacts': "",                        # TODO: Need to specify a build artifact
        'reason': "primary language",
        'error': "",
        'success': True }

    base_php_def = {
        'build system': "PHP",
        'primary lang': "PHP",
        'grep build': "",
        'grep test': "",
        'grep env': "",
        'build' : "if [ -e composer.json ]; then curl -sS https://getcomposer.org/installer | php; php composer.phar install; fi",
        'test' : "",
        'env' : "",
        'artifacts': "",                        # TODO: Need to specify a build artifact
        'reason': "primary language",
        'error': "",
        'success': True }

    base_c_def = {
        'build system': "make",
        'primary lang': "C",
        'grep build': "",
        'grep test': "",
        'grep env': "",
        'build': "if [ -x configure ]; then ./configure; fi; make clean; make all",
        'test' : "make test",
        'env' : "",
        'artifacts': "",                        # TODO: Need to specify a build artifact
        'reason': "primary language",
        'error': "",
        'success': True }

    base_java_def = {
        'build system': "Java",
        'primary lang': "Java",
        'grep build': "",
        'grep test': "",
        'grep env': "",
        'build': "if [ -e pom.xml ]; then mvn clean compile; elif [ -e build.xml ]; then ant; elif [ -e build.gradle ]; then gradle -q; fi",
        'test': "if [ -e pom.xml ]; then mvn test -fn > test_result.arti; elif [ -e build.xml ]; then ant test; elif [ -e build.gradle ]; then gradle -q test; fi",
        'env' : "",
        'artifacts': "",                        # TODO: Need to specify a build artifact
        'reason': "primary language",
        'error': "",
        'success': True }

    supported_langs = [ base_python_def, base_ruby_def,base_php_def, base_c_def, base_java_def ]

    # These definitions are added based on the presense of a specific build file.  We can
    # simply the command line provided by the base definition and grep for project and build
    # system specific parameters in README files.  eg. maven and MAVEN_OPTS

    ant_def = {
        'build system': "ant",
        'primary lang': "Java",
        'grep build': "ant clean; ant",
        'grep test': "ant test",
        'grep env': "ANT_OPTS",
        'build': "ant",
        'test' : "ant test",
        'env' : "",
        'artifacts': "",                        # TODO: Need to specify a build artifact
        'reason': "build.xml",
        'error': "",
        'success': True }

    maven_def = {
        'build system': "maven",
        'primary lang': "Java",
        'grep build': "",
        'grep test': "",
        'grep env': "MAVEN_OPTS",
        'build': "mvn dependency:list -DexcludeTransitive > dependency.arti; mvn clean compile",
        'test' : "mvn test -fn > test_result.arti",
        'env' : "",
        'artifacts': "*.arti",
        'reason': "pom.xml",
        'error': "",
        'success': True }

    c_def = {
        'build system': "make",
        'primary lang': "C",
        'grep build': "",
        'grep test': "make test",
        'grep env': "",
        'build': "if [ -x configure ]; then ./configure; fi; make clean; make",
        'test' : "make all",
        'env' : "",
        'artifacts': "",                        # TODO: Need to specify a build artifact
        'reason': "Makefile",
        'error': "",
        'success': True }

    # This is most favored definition and is added to top of stack

    buildsh_def = {
        'build system': "custom build script",
        'primary lang': "",
        'grep build': "build.sh",
        'grep test': "build.sh test",
        'grep env': "",
        'build': "./build.sh",
        'test' : "./build.sh test",
        'env' : "",
        'artifacts': "",
        'reason': "build.sh",
        'error': "",
        'success': True }

    # Fix base empty definition in case it is returned
    base_empty_def['primary lang'] = repo.language

    # Push empty language definition on stack
    langstack = [ base_empty_def ]

    # Push primary language
    for lang in supported_langs:
        if lang['primary lang'] == repo.language:
            langstack.insert(0, lang)

    # Create a stack of readme files to grep
    grepstack = []
    try:
        readmeStr = repo.get_readme().content.decode('base64', 'strict')
    except IOError as e:
        return { 'success': False, 'error': "I/O error({0}): {1}".format(e.errno, e.strerror) }
    grepstack.insert(0, readmeStr)                 # may be a null pointer

    # Add build system specific definitions to language stack based on the presense
    # of specific files like pom.xml.  Also, queue readme related files to grep later
    # looking for environment variables and command lines
    # TODO: This is just looking at files in the root directory.

    buildsh = None
    makefile = None
    for f in listing:
        if f.name == 'pom.xml':
            langstack.insert(0, maven_def)         # If we find specific build files we can improve our commands by grepping readme's 
        elif f.name == 'build.xml':
            langstack.insert(0, ant_def)
        elif f.name == 'Makefile':
            makefile = f
        elif f.name in ('build.sh', 'run_build.sh'):
            buildsh = f
        elif f.name in ('BUILDING.md', 'BUILDING.txt', 'README.maven', 'README.ant'):
            if f.type == 'file' and f.size != 0:
                fstr = repo.get_file_contents(f.path).content.decode('base64', 'strict')
                if fstr != "":
                    grepstack.insert(0, fstr)

    # build.sh is favored, because it bridges languages, sets environment variables, ...
    # Else if only the primary language definition is present, len(langstack) <= 2), push
    # Makefile as it is there for a reason.  Either, the primary language definition is 'C'
    # and we are pushing it again (no harm), or it is another language which does not
    # ordinarily use Makefiles.  It is safe to add when the length of stack is 2.
    # A Makefile is a better bet than a primary language definition which is generic. For
    # example, if the build system is something other than maven, ant, or gradle.
    #
    # On the other hand, if both pom.xml and Makefile are present, len(langstack) == 3,
    # then one could argue that developers would favor makefiles as being simpler and better
    # understood. Once we have the ability to grep a Makefile we could scan it for Java or Python
    # to determine whether the makefile applies to multiple languages.  For now, we assume
    # that it does.  Later, we can conditionally push it to the lang stack.  TODO: improve


    if buildsh != None:
        langstack.insert(0, buildsh_def)
#   elif len(langstack) <= 2 and makefile != None:
    elif makefile != None:
        langstack.insert(0, c_def)

    # For now we just process the top of stack language

    lang = langstack.pop(0)
    if lang['build'] != "":
        for readmeStr in grepstack:
            if readmeStr != "":
                delim = ["`", "'", '"', "\n"]                   # delimeters used to denote end of cmd
                cmd = lang['grep test']
                if cmd != "":
                    print "GREP test grep: ", cmd
                    strFound = buildFilesParser(readmeStr, cmd, delim)
                    print "GREP test outstr: ", strFound
                    if strFound != "":
                        lang['test'] = cmd                      # safe but loses extra cmd arguments possibly in strFound
#                       lang['test'] = strFound                 # TODO: needs to be validated.  May need to be sanitized
                cmd = lang['grep build']
                if cmd != "":
                    print "GREP build grep: ", cmd
                    strFound = buildFilesParser(readmeStr, cmd, delim)
                    print "GREP build outstr: ", strFound
                    if strFound != "":
                        lang['build'] = cmd                     # safe but loses extra cmd arguments possibly in strFound
#                       lang['build'] = strFound	        # TODO: needs to be validated.  May need to be sanitized
                env = lang['grep env']
                if env != "":
                    delim = [";", " ", "\n"]                    # delimeters used to denote end of environment variable
                    print "GREP env grep: ", env
                    strFound = buildFilesParser(readmeStr, env, delim)
                    print "GREP env outstr: ", strFound
                    if strFound != "":
                        lang['env'] = strFound
                break

    return lang

# Build Files Parser - Looks for string searchTerm in string fileBuf and then iterates over
# list of delimeters and finds the one with the smallest index, returning the string found between the
# two indices
def buildFilesParser(fileBuf, searchTerm, delimeter):
    # Get the length of the file
    lenFileBuf = len(fileBuf)

    # Search the fileBuf for searchTerm
    try:
        i = fileBuf.find(searchTerm)
    except UnicodeDecodeError:
        return ""

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
