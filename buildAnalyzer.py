from github import GithubException
import globals
import utils

# General strategy is to create a list of language definitions from which build
# and test commands are generated.  Each successive definition that is added to
# the list provides a better commnd line that is more specific to the project.
# The last list definition is returned. With a little luck, it is the preferred
# cmd line as provided by the readme.

def text_analytics_build_commands(listing, repo):
    """
    :param listing: Directory Listing
    :param repo: Repository to search build command in
    :return: A build command :rtype str
    """
    proximity_threshold = 5 # We insist that the build command that we extract
                             # be within 10 lines after encountering the word
                             # 'build'
    max_lines = 5 # Limit the number of lines (i.e. individual commands) we
                  # allow in our output
    max_words = 16 # Limit the number of words we allow per individual command
    max_chars = 64 # Limit the number of characters per individual command

    retval = []
    for f in listing:
        build_found = False
        build_line_number = 0

        commands = [' mvn ',' ant ', ' build ']
        if f.name in ('README.md','BUILDING.md', 'BUILDING.txt','BUILDING',
                      'README.maven', 'README.ant', 'README.textile'):
            if f.type == 'file' and f.size != 0:
                fstr = repo.get_file_contents(f.path).content.decode('base64',
                                                                     'strict')
                """ :type : str """
                lines = 0
                
                for idx, line in enumerate(fstr.splitlines()):
                    line = line.lower()
                    if 'build' in line:
                        build_found = True
                        build_line_number = idx
                    if build_found and (idx - build_line_number) < proximity_threshold:
                        for command in commands:
                            if command in line and 'install' not in line and\
                            len(line) > 0 and len(line) <= max_chars and\
                            len(line.split(' ')) <= max_words and\
                            lines <= max_lines and\
                            not line[len(line) - 1] == ':':
                                retval.append(utils.clean(line))
                                lines = lines + 1
        if len(retval) > 0: # If you find a build command in one file, then
                            # don't check other files
            break
    return ';'.join(retval)

def inferBuildSteps(listing, repo):

    # Gather all possible build, test, and environment options
    # This is what gets returned
    build_info = {
        'buildSystem': "",
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

    # This is added to the list first.  Additional list elements are added on
    # top of it as we perform discovery.  In the end, if we can't figure out
    # how to build the project, then this entry is used to convey the unknown
    # primary language to the end user.
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

    # These are the base lang definitions. They should cover the top two or
    # three build systems to achieve 60% or better compilation success.  The
    # command line is not project or build system specific.  Represents
    # standard use of the build system, eg make.
    base_python_def = {
        'build system': "Python",
        'primary lang': "Python",
        'grep build': "python setup.py build",	# Search readme for this string. If found, use it as build cmd
        'grep test': "py.test",			# Same for test command. Maybe we can pick up some extra arguments
        'grep env': "",
        'build' : "if [ -e setup.py ]; then sudo python setup.py install > build_result.arti 2>&1; fi",
        'test' : "py.test > test_result.arti 2>&1",
        'env' : "",
        'artifacts': "*.arti",
        'reason': "primary language",
        'error': "",
        'success': True }

    base_js_def = {
        'build system': "JavaScript",
        'primary lang': "JavaScript",
        'grep build': "npm install %s"%(repo.name),	# Search readme for this string. If found, use it as build cmd
        'grep test': "npm test",			# Same for test command. Maybe we can pick up some extra arguments
        'grep env': "",
        'build' : "if [ -e package.json ]; then npm install > build_result.arti 2>&1; fi",
        'test' : "if [ -e package.json ]; then npm test > test_result.arti 2>&1; fi",
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
        'build' : "bundle install > build_result.arti 2>&1; if [ -e Rakefile ]; then rake install >> build_result.arti 2>&1; fi",
        'test' : "rake test > test_result.arti 2>&1",
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
        'build' : "if [ -e composer.json ]; then curl -sS https://getcomposer.org/installer | php; php composer.phar install > build_result.arti 2>&1; fi",
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
         'grep test': "make check",
         'grep env': "",
         'build': "if [ -e Makefile.PL ]; then perl Makefile.PL > build_result.arti 2>&1; fi; make >> build_result.arti 2>&1; make install >> build_result.arti 2>&1",
         'test' : "make test > test_result.arti 2>&1",
         'env' : "",
         'artifacts': "*.arti",
         'reason': "primary language",
         'error': "",
         'success': True }

    base_c_def = {
        'build system': "make",
        'primary lang': "C",
        'grep build': "",
        'grep test': "make check",
        'grep env': "CFLAGS=",
        'build': "if [ -e configure.ac ]; then autoreconf -iv > build_result.arti 2>&1; fi; if [ -x configure ]; then ./configure >> build_result.arti 2>&1; fi; make >> build_result.arti 2>&1",
        # 'build': "if [ -e configure.ac ]; then aclocal > build_result.arti 2>&1; fi; if [ -e Makefile.am ]; then automake --add-missing >> build_result.arti 2>&1; fi; if [ -e configure.ac ]; then autoconfig >> build_result.arti 2>&1; fi; if [ -x configure ]; then ./configure >> build_result.arti 2>&1; fi; make >> build_result.arti 2>&1",
        'test' : "make test > test_result.arti 2>&1",
        'env' : "",
        'artifacts': "*.arti",
        'reason': "Primary language",
        'error': "",
        'success': True }

    base_cxx_def = {
        'build system': "make",
        'primary lang': "C++",
        'grep build': "",
        'grep test': "make check",
        'grep env': "CXXFLAGS=",
        'build': "if [ -e configure.ac ]; then autoreconf -iv > build_result.arti 2>&1; fi; if [ -x configure ]; then ./configure >> build_result.arti 2>&1; fi; make >> build_result.arti 2>&1",
        # 'build': "if [ -e configure.ac ]; then aclocal > build_result.arti 2>&1; fi; if [ -e Makefile.am ]; then automake --add-missing >> build_result.arti 2>&1; fi; if [ -e configure.ac ]; then autoconfig >> build_result.arti 2>&1; fi; if [ -x configure ]; then ./configure >> build_result.arti 2>&1; fi; make >> build_result.arti 2>&1",
        'test' : "make test > test_result.arti 2>&1",
        'env' : "",
        'artifacts': "*.arti",
        'reason': "Primary language",
        'error': "",
        'success': True }

    base_java_def = {
        'build system': "Java",
        'primary lang': "Java",
        'grep build': "",
        'grep test': "",
        'grep env': "",
        'build': "if [ -e pom.xml ]; then mvn clean compile > build_result.arti 2>&1; elif [ -e build.xml ]; then ant > build_result.arti 2>&1; elif [ -e build.gradle ]; then gradle -q > build_result.arti 2>&1; fi",
        'test': "if [ -e pom.xml ]; then mvn test -fn > test_result.arti 2>&1; elif [ -e build.xml ]; then ant test > test_result.arti 2>&1; elif [ -e build.gradle ]; then gradle -q test > test_result.arti 2>&1; fi",
        'env' : "",
        'artifacts': "*.arti",
        'reason': "primary language",
        'error': "",
        'success': True }

    base_scala_def = {
        'build system': "Scala",
        'primary lang': "Scala",
        'grep build': "",
        'grep test': "",
        'grep env': "",
        'build': "if [ -e sbt ]; then chmod a+x ./sbt; ./sbt clean compile > build_result.arti 2>&1; elif [ -e build.gradle ]; then gradle -q > build_result.arti 2>&1; fi",
        'test': "if [ -e sbt ]; then ./sbt test  > test_result.arti 2>&1; elif [ -e build.gradle ]; then gradle -q test > test_result.arti 2>&1; fi",
        'env' : "",
        'artifacts': "*.arti ",
        'reason': "primary language",
        'error': "",
        'success': True }

    supported_langs = [ base_python_def,base_js_def, base_ruby_def, base_php_def, base_perl_def, base_c_def, base_cxx_def, base_java_def, base_scala_def ]

    # These definitions are added based on the presense of a specific build file.  We can
    # simply the command line provided by the base definition and grep for project and build
    # system specific parameters in README files.  eg. maven and MAVEN_OPTS
    ant_def = {
        'build system': "ant",
        'primary lang': "Java",
        'grep build': "ant clean",
        'grep test' : "ant test",
        'grep env': "ANT_OPTS=",
        'build': "ant clean > build_result.arti 2>&1; ant >> build_result.arti 2>&1",
        'test': "ant test > test_result.arti 2>&1",
        'env' : "",
        'artifacts': "*.arti",
        'reason': "build.xml",
        'error': "",
        'success': True }

    maven_def = {
        'build system': "maven",
        'primary lang': "Java",
        'grep build': "",
        'grep test': "",
        'grep env': "MAVEN_OPTS=",
        'build': "mvn dependency:list -DexcludeTransitive > build_result.arti 2>&1; mvn clean compile >> build_result.arti 2>&1",
        'test' : "mvn test -fn > test_result.arti 2>&1",
        'env' : "",
        'artifacts': "*.arti",
        'reason': "pom.xml",
        'error': "",
        'success': True }

    cmake_def = {
        'build system': "C++_cmake",
        'primary lang': "C++",
        'grep build': "",
        'grep test': "make check",
        'grep env': "CXXFLAGS=",
        'build': "cmake . > build_result.arti 2>&1; if [ -x configure ]; then ./configure >> build_result.arti 2>&1; fi; make >> build_result.arti 2>&1",
        'test' : "make test > test_result.arti 2>&1",
        'env' : "",
        'artifacts': "*.arti",
        'reason': "CMakeLists.txt",
        'error': "",
        'success': True }

    scons_def = {
        'build system': "C++_scons",
        'primary lang': "C++",
        'grep build': "",
        'grep test': "",
        'grep env': "CXXFLAGS=",
        'build': "scons all > build_result.arti 2>&1;",
        'test' : "scons test > test_result.arti 2>&1",
        'env' : "",
        'artifacts': "*.arti",
        'reason': "SConstruct ",
        'error': "",
        'success': True }

    sbt_def = {
        'build system': "sbt",
        'primary lang': "Scala",
        'grep build': "",
        'grep test': "",
        'grep env': "",
        'build': "sbt clean compile > build_result.arti 2>&1;",
        'test' : "sbt test > test_result.arti 2>&1",
        'env' : "",
        'artifacts': "*.arti",
        'reason': "build.sbt ",
        'error': "",
        'success': True }

    c_def = {
        'build system': "make",
        'primary lang': "C/C++",
        'grep build': "",
        'grep test': "make check",
        'grep env': "CFLAGS=",
        'build': "if [ -x configure ]; then ./configure > build_result.arti 2>&1; fi; make >> build_result.arti 2>&1",
        'test' : "make test > test_result.arti 2>&1",
        'env' : "",
        'artifacts': "*.arti",
        'reason': "Makefile",
        'error': "",
        'success': True }

    bootstrap_def = {
        'build system': "make",
        'primary lang': "C/C++",
        'grep build': "",
        'grep test': "make check",
        'grep env': "CFLAGS=",
        'build': "if [ -x bootstrap ]; then ./bootstrap.sh > build_result.arti 2>&1; elif [ -x autogen.sh ]; then ./autogen.sh > build_result.arti 2>&1; fi; if [ -x configure ]; then ./configure >> build_result.arti 2>&1; fi; make >> build_result.arti 2>&1",
        'test' : "make test > test_result.arti 2>&1",
        'env' : "",
        'artifacts': "*.arti",
        'reason': "bootstrap.sh",
        'error': "",
        'success': True }

    # This is most favored definition and is appended to the end of the list
    buildsh_def = {
        'build system': "custom build script",
        'primary lang': "",
        'grep build': "build.sh",
        'grep test': "build.sh check",
        'grep env': "",
        'build': "./build.sh > build_result.arti 2>&1",
        'test' : "./build.sh test > test_result.arti 2>&1",
        'env' : "",
        'artifacts': "*.arti",
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
    bootstrap = None
    makefile = None
    for f in listing:
        if f.name == 'pom.xml':
            langlist.append(maven_def)         # If we find specific build files we can improve our commands by grepping readme's
        elif f.name == 'build.xml':
            langlist.append(ant_def)
        elif f.name == 'CMakeLists.txt':
            langlist.append(cmake_def)
        elif f.name == 'SConstruct':
            langlist.append(scons_def)
        elif f.name == 'build.sbt':
            langlist.append(sbt_def)
        elif f.name == 'package.json':
            langlist.append(base_js_def)      # Sometimes there is more CSS than JavaScript so base language is not recognized
        elif f.name == 'Makefile':
            makefile = f
        elif f.name in ('bootstrap.sh', 'autogen.sh'):
            bootstrap = f
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
    elif bootstrap != None:
        langlist.append(bootstrap_def)
    elif makefile != None:
        langlist.append(c_def)

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
        build_info['buildSystem'] = lang['build system']
        for readmeStr in grepstack:
            if readmeStr:
                delim = ["`", "'", '"', "#", "\n"]                   # delimiters used to denote end of cmd
                cmd = lang['grep test']
                if cmd:
                    strFound = buildFilesParser(readmeStr, cmd, delim)
                    if strFound:
                        strFound = appendArtifact(strFound)
                        build_info['testOptions'].append(strFound)
                cmd = lang['grep build']
                if cmd:
                    strFound = buildFilesParser(readmeStr, cmd, delim)
                    if strFound:
                        strFound = appendArtifact(strFound)
                        build_info['buildOptions'].append(strFound)
                env = lang['grep env']
                if env:
                    # Look first for 'VAR='.  Form is VAR=7
                    delim = [";", " ", "#", "\n"]                    # delimiters used to denote end of environment variable
                    strFound = buildFilesParser(readmeStr, env, delim)
                    if strFound:
                        # Look next for 'VAR="'.  Form is VAR="string"
                        envStr = env + '"'
                        delim = ['"']                           # delimiters used to denote end of environment variable
                        strFound2 = buildFilesParser(readmeStr, envStr, delim)
                        if strFound2:
                            strFound = strFound2 + '"'
                    if strFound:
                        build_info['envOptions'].append(strFound)
                break

    #Add commands extracted using text analytics
    text_analytics_suffix = ' > build_result.arti 2>&1;'
    build_command = text_analytics_build_commands(listing, repo)

    if build_command:
        if globals.useTextAnalytics:
            build_info['buildOptions'].insert(len(build_info), '[TextAnalytics]'+build_command+text_analytics_suffix)
        else:
            #print 'Globals.useTextAnalytics:' +str(globals.useTextAnalytics)
            build_info['buildOptions'].insert(0, '[TextAnalytics]'+build_command+text_analytics_suffix)
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

# appendArtifact - Removes trailing semi-colon if present and modifies
# command to re-direct stdin/stderr to the Jenkins's build artifact
def appendArtifact(cmd):
    if cmd[-1] == ';':
        cmd = cmd[:-1]
    if '>' not in cmd:
        cmd += " > test_result.arti 2>&1"
    return cmd;

# Build Files Parser - Looks for string searchTerm in string fileBuf and then iterates over
# list of delimiters and finds the one with the smallest index, returning the string found between the
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
        startingIndex = len(searchTerm)
        smallestIndex = lenFileBuf # this is one bigger than the biggest index, acts as infinity
        # If searchTerm found find the smallest index delimeter
        for delim in delimeter:
            if smallestIndex < lenFileBuf:
                j = fileBuf[i:].find(delim, startingIndex, smallestIndex)
            else:
                j = fileBuf[i:].find(delim, startingIndex)

            if j != -1:
                smallestIndex = j

        # If smallest index is smaller than the length of the searchTerm we found a delimeter
        if smallestIndex < lenFileBuf:
            return fileBuf[i:][:smallestIndex]

    return ""

