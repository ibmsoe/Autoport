from github import GithubException
# General strategy is to create a list of language definitions from which build and test
# commands are generated.  Each successive definition that is added to the list provides
# a better commnd line that is more specific to the project.  The last list definition
# is returned. With a little luck, it is the preferred cmd line as provided by the readme

def inferBuildSteps(listing, repo):

    # Gather all possible build, test, and environment options    
    # This is what gets returned
    build_info = {
        'buildOptions': [],
        'testOptions': [],
        'envOptions': [],
        'success': False,
        'reason': "primary language unknown",
        'selectedBuild': "",
        'selectedTest': "",
        'selectedEnv': "",
        'artifacts': "*.arti"
    }

    # This is added to the list first.  Additional list elements are added on top of it
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
        'build' : "if [ -e setup.py ]; then python setup.py install > build_result.arti; fi",
        'test' : "py.test > test_result.arti",
        'env' : "",
        'artifacts': "*.arti",
        'reason': "primary language",
        'error': "",
        'success': True }

    base_ruby_def = {
        'build system': "Ruby",
        'primary lang': "Ruby",
        'grep build': "gem install %s"%(repo.name),
        'grep test': "rake test",
        'grep env': "",
        'build' : "bundle install > dependency.arti; if [ -e Rakefile ]; then rake install > build_result.arti; fi",
        'test' : "rake test > test_result.arti",
        'env' : "",
        'artifacts': "*.arti",
        'reason': "primary language",
        'error': "",
        'success': True }

    base_php_def = {
        'build system': "PHP",
        'primary lang': "PHP",
        'grep build': "",
        'grep test': "",
        'grep env': "",
        'build' : "if [ -e composer.json ]; then curl -sS https://getcomposer.org/installer | php; php composer.phar install > build_result.arti; fi",
        'test' : "",
        'env' : "",
        'artifacts': "*.arti",
        'reason': "primary language",
        'error': "",
        'success': True }

    base_perl_def = {
        'build system': "Perl",
         'primary lang': "Perl",
         'grep build': "",
         'grep test': "",
         'grep env': "",
         'build': "if [ -e Makefile.PL ]; then perl Makefile.PL > build_result.arti; fi; make >> build_result.arti ; make install >> build_result.arti",
         'test' : "make test > test_result.arti",
         'env' : "",
         'artifacts': "*.arti", 
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

    base_cxx_def = {
        'build system': "C++",
        'primary lang': "C++",
        'grep build': "",
        'grep test': "",
        'grep env': "",
        'build': " if [ -e configure.ac ]; then autoconfig > build_result.arti; ./configure >> build_result.arti; make >> build_result.arti; make install >> build_result.arti; elif [ -x configure ]; then ./configure > build_result.arti; make >> build_result.arti; make install >> build_result.arti; elif [ -e CMakeLists.txt ]; then cmake . > build_result.arti; make  >> build_result.arti; make install >> build_result.arti; elif [ -e SConstruct ]; then scons all  > build_result.arti; fi",
        'test': " if [ -x configure ]; then make test  > test_result.arti; elif [ -e CMakeLists.txt ]; then make test > test_result.arti; elif [ -e SConstruct ]; then scons test  > test_result.arti; fi",
        'env' : "",
        'artifacts': "*.arti ",
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

    supported_langs = [ base_python_def, base_ruby_def, base_php_def, base_perl_def, base_c_def, base_cxx_def, base_java_def ]

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

    # This is most favored definition and is appended to the end of the list
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

    # Append empty language definition to list
    langlist = [ base_empty_def ]

    # Push primary language
    for lang in supported_langs:
        if lang['primary lang'] == repo.language:
            langlist.append(lang)

    # Create a stack of readme files to grep
    grepstack = []
    try:
        readmeStr = repo.get_readme().content.decode('base64', 'strict')
    except IOError as e:
        return { 'success': False, 'error': "I/O error({0}): {1}".format(e.errno, e.strerror) }
    except GithubException as e:
        return { 'success': False, 'error': "GithubException ({0}): {1}".format(e.status, e.data['message']), 'primary lang': repo.language }
    grepstack.insert(0, readmeStr)                 # may be a null pointer

    # Add build system specific definitions to language list based on the presense
    # of specific files like pom.xml.  Also, queue readme related files to grep later
    # looking for environment variables and command lines
    # TODO: This is just looking at files in the root directory.

    buildsh = None
    makefile = None
    for f in listing:
        if f.name == 'pom.xml':
            langlist.append(maven_def)         # If we find specific build files we can improve our commands by grepping readme's 
        elif f.name == 'build.xml':
            langlist.append(ant_def)
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
    # Else if only the primary language definition is present, len(langlist) <= 2), push
    # Makefile as it is there for a reason.  Either, the primary language definition is 'C'
    # and we are pushing it again (no harm), or it is another language which does not
    # ordinarily use Makefiles.  It is safe to add when the length of stack is 2.
    # A Makefile is a better bet than a primary language definition which is generic. For
    # example, if the build system is something other than maven, ant, or gradle.
    #
    # On the other hand, if both pom.xml and Makefile are present, len(langlist) == 3,
    # then one could argue that developers would favor makefiles as being simpler and better
    # understood. Once we have the ability to grep a Makefile we could scan it for Java or Python
    # to determine whether the makefile applies to multiple languages.  For now, we assume
    # that it does.  Later, we can conditionally push it to the lang stack.  TODO: improve

    if buildsh != None:
        langlist.append(buildsh_def)
    elif makefile != None:
        langlist.append(0, c_def)

    # Add each template match to build info in the order they were found
    for lang in langlist:
        if lang['build']: 
            build_info['buildOptions'].append(lang['build'])
        if lang['test']: 
            build_info['testOptions'].append(lang['test'])
        if lang['env']: 
            build_info['envOptions'].append(lang['env'])
        build_info['reason'] = lang['reason']

    # Check the last element added to the langlist for readme/other important file info
    lang = langlist[-1]
    if lang['build']:
        for readmeStr in grepstack:
            if readmeStr:
                delim = ["`", "'", '"', "\n"]                   # delimeters used to denote end of cmd
                cmd = lang['grep test']
                if cmd:
                    strFound = buildFilesParser(readmeStr, cmd, delim)
                    if strFound:
                        build_info['testOptions'].append(cmd)
                cmd = lang['grep build']
                if cmd:
                    strFound = buildFilesParser(readmeStr, cmd, delim)
                    if strFound:
                        build_info['buildOptions'].append(cmd)
                env = lang['grep env']
                if env:
                    delim = [";", " ", "\n"]                    # delimeters used to denote end of environment variable
                    strFound = buildFilesParser(readmeStr, env, delim)
                    if strFound:
                        build_info['envOptions'].append(strFound)
                break

    # Make the build, test, and env options of the last added element the default options
    # as those are the most likely to be correct
    if build_info['buildOptions']:
        build_info['success'] = True
        build_info['selectedBuild'] = build_info['buildOptions'][-1]
    
        if build_info['testOptions']:
            build_info['selectedTest'] = build_info['testOptions'][-1]
    
            if build_info['envOptions']:
                build_info['selectedEnv'] = build_info['envOptions'][-1]

    return build_info

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
