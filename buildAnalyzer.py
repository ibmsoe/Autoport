from github import GithubException
from log import logger
import globals
import utils
import yaml

# General strategy is to create a list of language definitions from which build
# and test commands are generated.  Each successive definition that is added to
# the list provides a better commnd line that is more specific to the project.
# The last list definition is returned. With a little luck, it is the preferred
# cmd line as provided by the readme.

def text_analytics_cmds(project, projectLang, grepStack, searchKey):
    """
    :param project: project name
    :param projectLang: primary language of project
    :param searchKey: build or test
    :param grepStack: list of file contents each as a string to analyze
    :return: A build command :rtype str
    """
    proximity_threshold = 10 # We insist that the command that we extract be within
                             # x lines after encountering the word 'build' or 'text'.
                             # Need to factor in HTML syntax.
    max_lines = 5   # Limit the number of lines (i.e. individual commands)
    max_words = 16  # Limit the number of words we allow per individual command
    max_chars = 128 # Limit the number of characters per individual command

    logger.debug("In text_analytics_cmds, project=%s, searchKey=%s, cnt grepStack[]=%s" % (project, searchKey, str(len(grepStack))))

    # List most common build and test commands first
    commands = ['mvn ', 'ant ', 'npm ', 'grunt ', 'python ', 'py.test ', 'cd ',
                'gem ', 'rake ', 'build.sh ', 'bootstrap.sh ', 'autogen.sh ',
                'autoreconf ', 'automake ', 'aclocal ', 'scons ', 'sbt ',
                'cmake ', 'gradle ', 'bundle ', 'perl ', 'php ']

    # List words that, if appearing in front of a command, indicate that it's
    # descriptive text, not a build command
    english = ['the', 'a', 'an', 'is', 'are', 'can', 'you', 'of', 'in', 'from',
               'this', 'to', 'that', 'when', 'should', 'might']

    retval = []
    for fstr in grepStack:
        build_found = False
        build_line_number = 0
        lines = 0

        for idx, line in enumerate(fstr.splitlines()):
            line = line.lower()
            if searchKey in line:
                build_found = True
                build_line_number = idx
            if build_found and\
               idx - build_line_number < proximity_threshold:
                if len(line):
                    # TODO: Remove, limit, or put under globals.text_analytics before GA
                    logger.debug("text_analytics_cmds, idx=%s scanning line=%s" % (str(idx), line))

                    isText = False
                    for word in english:
                        if word in line.split(' '):
                            isText = True
                            break

                    if isText:
                        continue

                    for command in commands:
                                                                    # TODO: validate start of command line
                        if len(line.split(' ')) <= max_words and\
                           lines <= max_lines and\
                           not line[len(line) - 1] == ':':          # command lines don't end with :
                            if command in line and '$' not in line:
                                retval.append(utils.clean(line))
                                lines = lines + 1
                                break
                            elif (projectLang == 'C' or projectLang == 'C++' or projectLang == 'Perl') and 'make' in line and '$' not in line:
                                retval.append(utils.clean(line))
                                lines = lines + 1
                                break
            else:
                build_found = False

        if len(retval):
            break          # If you find a build command sequence in one file, don't search other files

    return ';'.join(retval)

def interpretTravis(repo, travisFile, travis_def):
    """
    Method to interpret the travis control file and fill out the
    travis_def with appropriate values.
    """

    logger.debug("In interpretTravis, project %s" % repo.name)

    travis_flag = None
    try:
        travis_data = repo.get_file_contents(travisFile.path).content.decode('base64', 'strict')
    except Exception as e:
        logger.debug("interpretTravis: File Error %s" % str(e))
        travis_data = ""

    if travis_data:
        try:
            data = yaml.safe_load(travis_data)
        except Exception as e:
            logger.debug("interpretTravis: Yaml Error %s" % str(e))
            data = ""

        if data and 'script' in data and not any('$' in s for s in data['script']):
            if isinstance(data['script'], list):
                travis_def['test'] = '; '.join(data['script'])
            else:
                travis_def['test'] = data['script']

            travis_def['build'] = "echo ---See test log for travis-style build---"
            if 'before_script' in data and not any('$' in s for s in data['before_script']):
                if isinstance(data['before_script'], list):
                    travis_def['build'] = '; '.join(data['before_script'])
                else:
                    travis_def['build'] = data['before_script']

            # Keep repo.primary lang as reports are tied to it.  Travis has their own defs

            travis_flag = travisFile
            logger.debug("interpretTravis: %s test command: %s" % (repo.name, travis_def['test']))
            logger.debug("interpretTravis: %s build command: %s" % (repo.name, travis_def['build']))

    return travis_flag

def inferBuildSteps(listing, repo):

    if not listing or not repo:
        return { 'success': False, 'error': "Github I/O error" }

    # Gather all possible build, test, and environment options
    # This is what gets returned
    build_info = {
        'buildSystem': "",
        'primaryLang': "",
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
        'grep build': "python setup.py build",  # Search readme for this string. If found, use it as build cmd
        'grep test': "py.test",                 # Same for test command. Maybe we can pick up some extra arguments
        'grep env': "",
        'build' : "if [ -e setup.py ]; then sudo python setup.py install; fi",
        'test' : "py.test",
        'env' : "",
        'artifacts': "*.arti",
        'reason': "primary language",
        'error': "",
        'success': True }

    base_js_def = {
        'build system': "JavaScript",
        'primary lang': "JavaScript",
        'grep build': "",
        'grep test': "",
        'grep env': "",
        'build' : "if [ -e package.json ]; then npm install; fi",
        'test' : "if [ -e package.json ]; then npm test; fi",
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
        'build' : "bundle install; if [ -e Rakefile ]; then rake install; fi",
        'test' : "rake test",
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
        'build' : "if [ -e composer.json ]; then curl -sS https://getcomposer.org/installer | php; php composer.phar install; fi",
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
        'build': "if [ -e Makefile.PL ]; then perl Makefile.PL; fi; make; make install",
        'test' : "make test",
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
        'build': "if [ -e configure.ac ]; then autoreconf -iv; fi; if [ -x configure ]; then ./configure; fi; make",
        # 'build': "if [ -e configure.ac ]; then aclocal; fi; if [ -e Makefile.am ]; then automake --add-missing; fi; if [ -e configure.ac ]; then autoconfig; fi; if [ -x configure ]; then ./configure; fi; make",
        'test' : "make test",
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
        'build': "if [ -e configure.ac ]; then autoreconf -iv; fi; if [ -x configure ]; then ./configure; fi; make",
        # 'build': "if [ -e configure.ac ]; then aclocal; fi; if [ -e Makefile.am ]; then automake --add-missing; fi; if [ -e configure.ac ]; then autoconfig; fi; if [ -x configure ]; then ./configure; fi; make",
        'test' : "make test",
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
        'build': "if [ -e pom.xml ]; then mvn clean compile; elif [ -e build.xml ]; then ant; elif [ -e build.gradle ]; then gradle -q; fi",
        'test': "if [ -e pom.xml ]; then mvn test -fn; elif [ -e build.xml ]; then ant test; elif [ -e build.gradle ]; then gradle -q test; fi",
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
        'build': "if [ -e sbt ]; then chmod a+x ./sbt; ./sbt clean compile; elif [ -e build.gradle ]; then gradle -q; fi",
        'test': "if [ -e sbt ]; then ./sbt test; elif [ -e build.gradle ]; then gradle -q test; fi",
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
        'build': "ant clean; ant",
        'test': "ant test",
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
        'build': "mvn dependency:list -DexcludeTransitive; mvn clean compile",
        'test' : "mvn test -fn",
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
        'build': "cmake . ; if [ -x configure ]; then ./configure; fi; make",
        'test' : "make test",
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
        'build': "scons all",
        'test' : "scons test",
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
        'build': "sbt clean compile",
        'test' : "sbt test",
        'env' : "",
        'artifacts': "*.arti",
        'reason': "build.sbt ",
        'error': "",
        'success': True }

    c_def = {
        'build system': "make",
        'primary lang': repo.language,
        'grep build': "",
        'grep test': "make check",
        'grep env': "CFLAGS=",
        'build': "if [ -x configure ]; then ./configure; fi; make",
        'test' : "make test",
        'env' : "",
        'artifacts': "*.arti",
        'reason': "Makefile",
        'error': "",
        'success': True }

    bootstrap_def = {
        'build system': "make",
        'primary lang': repo.language,
        'grep build': "",
        'grep test': "make check",
        'grep env': "CFLAGS=",
        'build': "if [ -x bootstrap.sh ]; then ./bootstrap.sh; elif [ -x autogen.sh ]; then ./autogen.sh; fi; if [ -x configure ]; then ./configure; fi; make",
        'test' : "make test",
        'env' : "",
        'artifacts': "*.arti",
        'reason': "bootstrap.sh or autogen.sh",
        'error': "",
        'success': True }

    # This is most favored definition and is appended to the end of the list
    # Setting default build command to `` in the definition
    # This would take care that no other language definition
    # should fill the build command in case we have .travis.yml
    # present in project.
    travis_def = {
        'build system': "travis control file",
        'primary lang': repo.language,
        'grep build': "",
        'grep test': "",
        'grep env': "",
        'build': "",
        'test' : "",
        'env' : "",
        'artifacts': "*.arti",
        'reason': ".travis.yml",
        'error': "",
        'success': True }

    buildsh_def = {
        'build system': "custom build script",
        'primary lang': repo.language,
        'grep build': "build.sh",
        'grep test': "build.sh check",
        'grep env': "",
        'build': "./build.sh",
        'test' : "./build.sh",
        'env' : "",
        'artifacts': "*.arti",
        'reason': "build.sh",
        'error': "",
        'success': True }

    logger.debug("In inferBuildSteps, name=%s, primary lang=%s" % (repo.name, repo.language))

    # Fix base empty definition in case it is returned
    if repo.language:
        base_empty_def['primary lang'] = repo.language

    # Append empty language definition to list
    langlist = [ base_empty_def ]

    # Push primary language
    for lang in supported_langs:
        if lang['primary lang'] == repo.language:
            langlist.append(lang)

    # Add build system specific definitions to language list based on the presense
    # of specific files like pom.xml.  Also, queue readme related files to grep later
    # looking for environment variables and command lines
    # TODO: This is just looking at files in the root directory.

    readmeFiles = ['building', 'readme']
    grepstack = []

    buildsh = None
    bootstrap = None
    makefile = None
    travis = None
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
        elif f.name == '.travis.yml':
            travis = interpretTravis(repo, f, travis_def)
        elif any(x in f.name.lower() for x in readmeFiles):
            if f.type == 'file' and f.size != 0:
                try:
                    fstr = repo.get_file_contents(f.path).content.decode('base64', 'strict')
                    if fstr != "":
                        grepstack.insert(0, fstr)
                        logger.debug("inferBuildSteps, grepfile=%s" % f.name)
                except:
                    pass

    # Travis YML file take precedence over build.sh, bootstrap.sh, and Makefile.
    # Next, build.sh is favored, because it bridges languages, sets environment variables, ...
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

    if travis != None:
        langlist.append(travis_def)
    elif buildsh != None:
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
        build_info['primaryLang'] = lang['primary lang']

    lang = langlist[-1]
    if lang['build']:
        build_info['buildSystem'] = lang['build system']
        # Check the last element added to the langlist for readme/other important file info
        if not travis:
            for readmeStr in grepstack:
                if readmeStr:
                    delim = ["`", "'", '"', "#", "\n"]        # denotes end of cmd
                    cmd = lang['grep test']
                    if cmd and cmd.find('$') == -1:
                        strFound = buildFilesParser(readmeStr, cmd, delim)
                        if strFound:
                            build_info['testOptions'].append(strFound)
                    cmd = lang['grep build']
                    if cmd and cmd.find('$') == -1:
                        strFound = buildFilesParser(readmeStr, cmd, delim)
                        if strFound:
                            build_info['buildOptions'].append(strFound)
                    env = lang['grep env']
                    if env:
                        # Look first for 'VAR="' form. eg. VAR="string"
                        envStr = env + '"'
                        delim = ['"']                        # denotes end of environment variable
                        strFound = buildFilesParser(readmeStr, envStr, delim)
                        if strFound:
                            strFound = strFound + '"'
                        else:
                            # Look next for 'VAR=' form. .eg VAR=7
                            delim = [";", " ", "#", "\n"]    # denotes end of environment variable
                            strFound = buildFilesParser(readmeStr, env, delim)
                            if strFound.find('"'):           # This was ruled out above in first check 
                                strFound = ""                # String should not have embedded quote
                        if strFound:
                            build_info['envOptions'].append(strFound)
                    break

            # Add build commands extracted using text analytics
            command = text_analytics_cmds(repo.name, repo.language, grepstack, 'build')
            logger.debug("inferBuildSteps, text_analytics build cmd=%s" % command)
            if command:
                if globals.useTextAnalytics:
                    build_info['buildOptions'].insert(len(build_info), '[TextAnalytics]' + command)
                else:
                    build_info['buildOptions'].insert(0, '[TextAnalytics]' + command)

            # Add build commands extracted using text analytics
            command = text_analytics_cmds(repo.name, repo.language, grepstack, 'test')
            logger.debug("inferBuildSteps, text_analytics test cmd=%s" % command)
            if command:
                if globals.useTextAnalytics:
                    build_info['testOptions'].insert(len(build_info), '[TextAnalytics]' + command)
                else:
                    build_info['testOptions'].insert(0, '[TextAnalytics]' + command)

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

# Build Files Parser - Looks for string searchTerm in string fileBuf and then
# iterates over list of delimiters and finds the one with the smallest index,
# returning the string found between the two indices
def buildFilesParser(fileBuf, searchTerm, delimeter):

    # Need to prepend "./" in front of these commands as they are part of the project
    localCmds = ['bootstrap.sh', 'autogen.sh', 'build.sh' ]

    # Disallow strings containing the following substrings
    # -- compile of 32-bit apps not supported on le.  eg. -m32 redis
    # -- we don't want any platform specific strings as this is cross-platform
    disallow = ['32', 'arm', 'x86', 'ppc', 's390' ]

    # Get the length of the file
    lenFileBuf = len(fileBuf)

    i = 0
    found = False
    while i != -1 and i < lenFileBuf and not found:

        try:
            i = fileBuf.find(searchTerm, i)
        except UnicodeDecodeError:
            return ""

        match = ""
        if i != -1:
            startingIndex = len(searchTerm)
            lenFileBuf -= startingIndex

            # Find delimiter with the smallest index as there are multiple delimiters
            smallestIndex = lenFileBuf;
            for delim in delimeter:
                j = fileBuf[i:].find(delim, startingIndex, smallestIndex)
                if j != -1:
                    smallestIndex = j
                    match = fileBuf[i:][:smallestIndex]
            if match:
                found = not any(x in match.lower() for x in disallow)
                if not found:
                    logger.debug("buildFilesParser, searchTerm=%s eliminated match=%s" % (searchTerm, match))
                    match = ""
            i += startingIndex

    if found:
        for x in localCmds:
            if not "./" + x in match:
                match = match.replace(x, "./" + x)

    logger.debug("Leaving buildFilesParser, searchTerm=%s match=%s" % (searchTerm, match))
    return match
