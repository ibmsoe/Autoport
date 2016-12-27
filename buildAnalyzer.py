from github import GithubException
from collections import OrderedDict
from log import logger
import globals
import utils
import yaml
import re


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

    # Symbols used as prompts
    promptsStr = '$#>%'

    # Symbols in commands we don't allow.  Not a proper list.  We have limitations such
    # as $VAR to prevent expanded environment variables which we don't support yet
    noContainsStr = '$'

    # Commands don't end with these characters.
    noEndsWithStr = ':[]().,'

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
                    logger.debug("text_analytics_cmds, idx=%s scanning line=%s" % (str(idx), line))

                    isText = False
                    for word in english:
                        if word in line.split(' '):
                            isText = True
                            break

                    if isText or any(x in line for x in noContainsStr):
                        continue

                    lastChar = line[len(line) - 1]

                    # check for command prompt symbols at beginning of line
                    if line.lstrip()[0] in promptsStr:
                        line = line.lstrip()[1:].lstrip()

                    for command in commands:
                                                                    # TODO: validate start of command line
                        if len(line.split(' ')) <= max_words and\
                           lines <= max_lines and\
                           not lastChar in noEndsWithStr:           # Commands don't end with ':[]()'
                            if command in line:
                                retval.append(utils.clean(line))
                                lines = lines + 1
                                break
                            elif (projectLang == 'C' or projectLang == 'C++' or projectLang == 'Perl') and\
                                 'make' in line:
                                retval.append(utils.clean(line))
                                lines = lines + 1
                                break
            else:
                build_found = False

        if len(retval):
            break          # If you find a build command sequence in one file, don't search other files

    return ';'.join(retval)


def eliminateDupEnv(env):
    """
    Method to eliminate duplicate environment variables
    This is patterned after convertEnv()
    """

    if not env:
        return env

    # Split by all whitespace, blanks, tabs, and newlines
    envList = env.split()

    # Splits too much.  We don't want to split by embedded blanks and tabs if var is quoted
    quoteType = ""
    combine = ""
    newEnv=[]
    for subString in envList:
        if '="' in subString:                                  # Start of quoted variable
            quoteType = '"'
            n = subString.find('="')
            key = subString[:n]
        elif "='" in subString:                                # Start of quoted variable
            quoteType = "'"
            n = subString.find("='")
            key = subString[:n]
        else:
            n = subString.find("=")
            key = subString[:n]

        if quoteType and quoteType in subString[-1]:           # Ends in quoted variable
            if key not in newEnv:
                if combine:
                    combine = combine + ' ' + subString
                else:
                    combine = subString
                newEnv.append(combine)
            quoteType = ""
            combine = ""
        elif quoteType:                                        # Mid of quoted variable
            if combine:
                combine = combine + ' ' + subString
            else:
                combine = subString
        elif key + "=" not in " ".join(newEnv):                # not a quoted variable
            newEnv.append(subString)

    newEnv = " ".join(newEnv)
    return newEnv

def selectTravisMatrix(repo, matrix):
    """
    Method to select a matrix entry of environment variables.  Only one entry in
    matrix is chosen as each line is intended for a unique build.  Try to choose
    the line that best fits our supported platforms
    """

    linuxEnv = ""
    lessEnv = ""

    compilers = ['gcc', 'clang', 'autotools', 'make', 'cmake', 'scons', 'sbt']
    restrict = ['android', 'arm', 'ia32', 'macos', 'osx', 'x86-64', 'x64', 'ppc']
    lessRestrict = ['android', 'arm', 'ia32', 'macos', 'osx']

    # TravisCI processes include and exclude sections to determine builds

    if 'include' in matrix:
        matrix = matrix['include']

    for platform in matrix:

        # Environment is selected based on operating system type
        if 'os' in platform and 'env' in platform:
            if platform['os'].lower() != 'linux':
                continue
            linuxEnv = platform['env']
        # Environment is based on some other selection like compiler
        elif 'compiler' in platform and 'env' in platform:
            if platform['compiler'].lower() not in compilers:
                continue
            linuxEnv = platform['env']
        elif 'os' not in platform and 'exclude' not in platform:
            linuxEnv = platform

        if not isinstance(linuxEnv, list) and not isinstance(linuxEnv, basestring):
            linuxEnv = ""
            continue

        # Convert it to a string for comparisons below
        if isinstance(linuxEnv, list):
            try:
                linuxEnv = ' '.join(linuxEnv)
            except:
                linuxEnv = ""

        if not any(x in linuxEnv.lower() for x in restrict):
            break
        if not any(x in linuxEnv.lower() for x in lessRestrict):
            lessEnv = linuxEnv
        linuxEnv = ""

    if not linuxEnv:
        linuxEnv = lessEnv

    logger.debug("Leaving selectTravisMatrix, proj=%s selectedEnv=%s" % (repo.name, linuxEnv))

    return linuxEnv

def getAllTargets(repo, Makefile):
    logger.debug("In getAllTargets, proj=%s" % repo.name)
    try:
       targets = []
       subTargets = []
       data = repo.get_file_contents(Makefile.path).content.decode('base64', 'strict')
       makefile_data = data.split("\n")
       target_pattern = re.compile("^[^\-#\s\$\.\%][a-zA-Z0-9_\/\s\.\-]*(?!:=):[a-zA-Z0-9_\$\(\)\/\s\-\.]*;*")
       for line in makefile_data:
           m = target_pattern.search(line)
           if m:
               tgt = m.group(0).partition(':')
               target = tgt[0].split()
               targets.extend(target)
               for i in xrange(len(target)):
                   subTargets.append(tgt[2].strip(";").split())
       logger.debug("In getAllTargets: proj=%s, all targets=%s" %(repo.name, targets))
       return targets, subTargets
    except Exception as e:
        logger.debug("In getAllTargets: File Error %s" % str(e))
        makefile_data = ""


def getMakeTestCommand(repo, Makefile):
    logger.debug("In getMakeTestCommand, proj=%s" % repo.name)
    try:
       targets, subTargets = getAllTargets(repo, Makefile)
       subTgt, reqTgt = "", ""
       for count, tgt in enumerate(targets):
           if tgt == "test" or tgt == "check":
               reqTgt = "make %s" %(tgt)
               logger.debug("In getMakeTestCommand, target=%s found in makefile" % tgt)
               return reqTgt
           elif "test" in tgt:
             logger.debug("In getMakeTestCommand, proj=%s, candidate target %s" % (repo.name, tgt))
             logger.debug("In getMakeTestCommand, proj=%s, associated subtargets %s" % (repo.name, subTargets[count]))
             if len(subTgt) < len(subTargets[count]) or subTgt == "":
                 reqTgt = tgt
                 subTgt = subTargets[count]
                 logger.debug("In getMakeTestCommand, proj=%s, candidate target %s" % (repo.name, reqTgt))
       if not reqTgt:
           logger.debug("In getMakeTestCommand, proj=%s, No specific test target found in makefile" % repo.name)
       else:
           reqTgt = "make %s" %(reqTgt)
           logger.debug("In getMakeTestCommand, proj=%s, target=%s found in makefile" % (repo.name,reqTgt))
       return reqTgt
    except Exception as e:
        logger.debug("getMakeTestCommand: %s" % str(e))

def interpretTravis(repo, travisFile, travis_def):
    """
    Method to interpret the travis control file and fill out the
    travis_def with appropriate values.
    """

    logger.debug("In interpretTravis, proj=%s" % repo.name)

    travis_flag = None
    try:
        travis_data = repo.get_file_contents(travisFile.path).content.decode('base64', 'strict')
        if 'docker' in travis_data:
            travis_data = ""
    except Exception as e:
        logger.debug("interpretTravis: File Error %s" % str(e))
        travis_data = ""

    if travis_data:
        try:
            data = yaml.safe_load(travis_data)
        except Exception as e:
            logger.debug("interpretTravis: Yaml Error %s" % str(e))
            data = ""

        if data and 'script' in data and data['script']:
            # Get general environment variables first
            generalEnv = ""
            if 'env' in data:
                logger.debug("interpretTravis: proj=%s env=%s" % (repo.name, data['env']))

                if isinstance(data['env'], dict):
                    dictEnv = data['env']
                    if dictEnv.has_key('global'):
                        generalEnv = dictEnv['global']
                        try:
                            # Join them.  They are meant to be applied to each
                            # row in a matrix and are common to all builds
                            if isinstance(generalEnv, list):
                                generalEnv = ' '.join(generalEnv)
                        except:
                            generalEnv = ""
                    if dictEnv.has_key('matrix'):
                        linuxEnv = selectTravisMatrix(repo, dictEnv['matrix'])
                        # Add linuxEnv to generalEnv if it is non-empty
                        if generalEnv and linuxEnv:
                            generalEnv = generalEnv + " " + linuxEnv
                        elif linuxEnv:
                            generalEnv = linuxEnv
                elif isinstance(data['env'], list):
                    for item in data['env']:
                        if not any(x in item.lower() for x in ['cuda', 'win64', 'linux32', 'macos', 'android', 'ios']):
                            break
                    if not isinstance(item, dict):
                        generalEnv = item
                    else:
                        logger.debug("interpretTravis: skipping env proj=%s env=%s" % (repo.name, item))
                elif isinstance(data['env'], basestring):
                    generalEnv = data['env']

                logger.debug("interpretTravis: proj=%s generalEnv=%s" % (repo.name, generalEnv))

            # Add in distro specific environment variables
            linuxEnv = ""
            if 'matrix' in data:
                linuxEnv = selectTravisMatrix(repo, data['matrix'])

            # Combine general and linux specific environment variables
            if generalEnv and linuxEnv:
                generalEnv = generalEnv + " " + linuxEnv
            elif linuxEnv:
                generalEnv = linuxEnv

            # Add TravisCI control variables that apply for our builds
            generalEnv = "TRAVIS_OS_NAME=linux PLATFORM=linux " + generalEnv

            # Eliminate duplicate entries
            travis_def['env'] = eliminateDupEnv(generalEnv)

            # Create directories that are listed in cache section
            cacheCmds=""
            if 'cache' in data and data['cache']:
                cache=data['cache']
                if 'directories' in cache:
                    dirList = ' '.join(cache['directories'])
                    if dirList:
                        # Directories may be outside /home/jenkins, eg. /home/travis
                        cacheCmds = "sudo mkdir -p " + dirList
                        cacheCmds += "; sudo chown -R jenkins.jenkins " + dirList

            logger.debug("interpretTravis: proj=%s directories=%s" % (repo.name, cacheCmds))

            # Add autoport build command which comes from yaml before_install and install
            privileged = ['apt', 'dpkg', 'yum', 'rpm', 'install']
            dontAddSudo = [ 'if', 'then', 'elif', 'else', 'fi', 'case', 'function', 'until',
                            'for', 'while', 'do', 'done', 'true', 'false', 'in', 'npm' ]
            beforeInstall = ""
            if 'before_install' in data and data['before_install']:
                if isinstance(data['before_install'], list):
                    newCmds = []
                    for cmdline in data['before_install']:
                        if cmdline.endswith(';'):
                            cmdline = cmdline[:-1]
                        cmd = cmdline.split()[0]
                        if any(x in cmdline for x in privileged) and\
                           'sudo' not in cmdline and cmd not in dontAddSudo:
                            newCmds.append('sudo ' + cmdline)
                        else:
                            newCmds.append(cmdline)
                    beforeInstall = '; '.join(newCmds)
                elif isinstance(data['before_install'], basestring):
                    cmdline = data['before_install']
                    cmd = cmdline.split()[0]
                    if any(x in cmdline for x in privileged) and\
                       'sudo' not in cmdline and cmd not in dontAddSudo:
                        beforeInstall = 'sudo ' + cmdline
                    else:
                        beforeInstall = cmdline

            logger.debug("interpretTravis: proj=%s beforeInstall=%s" % (repo.name, beforeInstall))

            install = ""
            if 'install' in data and data['install']:
                if isinstance(data['install'], list):
                    newCmds = []
                    for cmdline in data['install']:
                        if cmdline.endswith(';'):
                            cmdline = cmdline[:-1]
                        cmd = cmdline.split()[0]
                        if any(x in cmdline for x in privileged) and\
                           'sudo' not in cmdline and cmd not in dontAddSudo:
                            newCmds.append('sudo ' + cmdline)
                        else:
                            newCmds.append(cmdline)
                    install = '; '.join(newCmds)
                elif isinstance(data['install'], basestring):
                    cmdline = data['install']
                    cmd = cmdline.split()[0]
                    if any(x in cmdline for x in privileged) and\
                       'sudo' not in cmdline and cmd not in dontAddSudo:
                        install = 'sudo ' + cmdline
                    else:
                        install = cmdline

            logger.debug("interpretTravis: proj=%s install=%s" % (repo.name, install))

            if beforeInstall and install:
                travis_def['build'] = beforeInstall + '; ' + install
            elif beforeInstall:
                travis_def['build'] = beforeInstall
            else:
                travis_def['build'] = install
            # Add autoport test command which comes from yaml before_script and script
            beforeScript = ""
            if 'before_script' in data and data['before_script']:
                if isinstance(data['before_script'], list):
                    beforeScript = '; '.join(data['before_script'])
                elif isinstance(data['before_script'], basestring):
                    beforeScript = data['before_script']

            if not travis_def['build'] and beforeScript:
                travis_def['build'] = beforeScript
            elif beforeScript:
                travis_def['test'] = beforeScript

            cmdline = ""
            if isinstance(data['script'], list):
                cmdline = '; '.join(data['script'])
            elif isinstance(data['script'], basestring):
                cmdline = data['script']

            if travis_def['test']:
                travis_def['test'] = travis_def['test'] + '; ' + cmdline
            else:
                travis_def['test'] = cmdline

            # If the cache section identified directories, include cmds to create them
            if cacheCmds:
                travis_def['build'] = cacheCmds + '; ' + travis_def['build']

            # If there is only one command, specify it as build.  A test command
            # may be generated based on the stack of commands that are independently
            # produced by the framework via non-travis based rules
            if not travis_def['build']:
                travis_def['build'] = travis_def['test']
                travis_def['test'] = ""

            # Keep repo.primary lang as reports are tied to it.  Travis has their own defs

            travis_flag = travisFile
            logger.debug("interpretTravis: proj=%s env: %s" % (repo.name, travis_def['env']))
            logger.debug("interpretTravis: proj=%s build command: %s" % (repo.name, travis_def['build']))
            logger.debug("interpretTravis: proj=%s test command: %s" % (repo.name, travis_def['test']))

    return travis_flag

def inferBuildSteps(listing, repo, mongoClient=None):
    if not listing or not repo:
        return { 'success': False, 'error': "Github I/O error" }

    # Projects are not necessarily code. eg. lapack
    primaryLang = repo.language
    if not primaryLang:
        primaryLang = "N/A"

    logger.debug("In inferBuildSteps, proj=%s, lang=%s, url=%s" % (repo.name, primaryLang, repo.html_url))

    # Gather all possible build, test, and environment options
    # This is what gets returned
    build_info = {
        'buildSystem': "",
        'primaryLang': "",
        'envOptions': [],
        'buildOptions': [],
        'testOptions': [],
        'installOptions': [],
        'success': False,
        'reason': "Primary language unknown",
        'selectedEnv': "",
        'selectedBuild': "",
        'selectedTest': "",
        'selectedInstall': "",
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
        'grep install': "",
        'grep env': "",
        'build': "",
        'test' : "",
        'install':"",
        'env' : "",
        'artifacts': "",
        'reason': "Primary language unknown",
        'error': "Primary language unknown",
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
        'grep install': "",
        'grep env': "",
        'build' : "if [ -e setup.py ]; then sudo python setup.py install; fi",
        'test' : "py.test",
        'install':"",
        'env' : "",
        'artifacts': "*.arti",
        'reason': "Primary language",
        'error': "",
        'success': True }

    base_js_def = {
        'build system': "JavaScript",
        'primary lang': "JavaScript",
        'grep build': "",
        'grep test': "",
        'grep install': "",
        'grep env': "",
        'build' : "if [ -e package.json ]; then npm install; fi",
        'test' : "if [ -e package.json ]; then npm test; fi",
        'install':"",
        'env' : "",
        'artifacts': "*.arti",
        'reason': "Primary language",
        'error': "",
        'success': True }

    base_ruby_def = {
        'build system': "Ruby",
        'primary lang': "Ruby",
        'grep build': "gem install %s"%(repo.name),
        'grep test': "rake test",
        'grep env': "",
        'grep install': "",
        'build' : "bundle install; if [ -e Rakefile ]; then rake install; fi",
        'test' : "rake test",
        'install':"",
        'env' : "",
        'artifacts': "*.arti",
        'reason': "Primary language",
        'error': "",
        'success': True }

    base_php_def = {
        'build system': "PHP",
        'primary lang': "PHP",
        'grep build': "",
        'grep test': "",
        'grep install': "",
        'grep env': "",
        'build' : "if [ -e composer.json ]; then curl -sS https://getcomposer.org/installer | php; php composer.phar install; fi",
        'test' : "",
        'install':"",
        'env' : "",
        'artifacts': "*.arti",
        'reason': "Primary language",
        'error': "",
        'success': True }

    base_perl_def = {
        'build system': "Perl",
        'primary lang': "Perl",
        'grep build': "",
        'grep test': "make check",
        'grep install': "",
        'grep env': "",
        'build': "if [ -e Build.PL ]; then  perl ./Build.PL; elif [ -e Makefile.PL ]; then perl Makefile.PL; make; fi",
        'test' : "if [ -e Build.PL ]; then ./Build test; elif [ -e Makefile.PL ]; then getMakeTestTarget; make $TEST; fi",
        'install':"make install",
        'env' : "",
        'artifacts': "*.arti",
        'reason': "Primary language",
        'error': "",
        'success': True }

    base_c_def = {
        'build system': "make",
        'primary lang': "C",
        'grep build': "",
        'grep test': "make check",
        'grep install': "",
        'grep env': "CFLAGS=",
        'build': "if [ -e configure.ac ]; then autoreconf -iv; fi; if [ -x configure ]; then ./configure; fi; make",
        # 'build': "if [ -e configure.ac ]; then aclocal; fi; if [ -e Makefile.am ]; then automake --add-missing; fi; if [ -e configure.ac ]; then autoconfig; fi; if [ -x configure ]; then ./configure; fi; make",
        'test' : "getMakeTestTarget; make $TEST;",
        'install' : "sudo make install",
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
        'grep install': "",
        'grep env': "CXXFLAGS=",
        'build': "if [ -e configure.ac ]; then autoreconf -iv; fi; if [ -x configure ]; then ./configure; fi; make",
        # 'build': "if [ -e configure.ac ]; then aclocal; fi; if [ -e Makefile.am ]; then automake --add-missing; fi; if [ -e configure.ac ]; then autoconfig; fi; if [ -x configure ]; then ./configure; fi; make",
        'test' : "getMakeTestTarget; make $TEST;",
        'install' : "sudo make install",
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
        'grep install': "",
        'grep env': "",
        'build': "if [ -e pom.xml ]; then mvn compile; elif [ -e build.xml ]; then ant; elif [ -x gradlew ]; then ./gradlew build; elif [ -e build.gradle ]; then gradle -q build; fi",
        'test': "if [ -e pom.xml ]; then mvn test -fn; elif [ -e build.xml ]; then ant test; elif [ -e build.gradle ]; then gradle -q test; fi",
        'install':"",
        'env' : "",
        'artifacts': "*.arti",
        'reason': "Primary language",
        'error': "",
        'success': True }

    base_scala_def = {
        'build system': "Scala",
        'primary lang': "Scala",
        'grep build': "",
        'grep test': "",
        'grep install': "",
        'grep env': "",
        'build': "if [ -e sbt ]; then chmod a+x ./sbt; ./sbt compile; elif [ -x gradlew ]; then ./gradlew build; elif [ -e build.gradle ]; then gradle -q build; fi",
        'test': "if [ -e sbt ]; then ./sbt test; elif [ -e build.gradle ]; then gradle -q test; fi",
        'install': "",
        'env' : "",
        'artifacts': "*.arti ",
        'reason': "Primary language",
        'error': "",
        'success': True }

    base_go_def = {
        'build system': "Go",
        'primary lang': "Go",
        'grep build': "go build",
        'grep test': "go test",
        'grep install': "go get",
        'grep env': "",
        'build': "mkdir -p $WORKSPACE/go/src/github.com/%s $WORKSPACE/go/bin $WORKSPACE/go/pkg;rsync -r $WORKSPACE/* $WORKSPACE/go/src/github.com/%s --exclude go ;cd $WORKSPACE/go/src/github.com/%s;go get -v ./...;go install"%(repo.name,repo.name,repo.name),
        'test': "cd $WORKSPACE/go/src/github.com/%s;go test"%(repo.name),
        'install': "go install",
        'env' : "GOPATH=${WORKSPACE}/go:/opt/go GOBIN=$WORKSPACE/go/bin:/opt/go/bin",
        'artifacts': "*.arti ",
        'reason': "Primary language",
        'error': "",
        'success': True }

    base_r_def = {
        'build system': "R",
        'primary lang': "R",
        'grep build': "Rscript",
        'grep test': "",
        'grep install': "",
        'grep env': "",
        'build': "if [ -e DESCRIPTION ]; then R CMD build .; fi",
        'test': "if [ -e %s*tar.gz ]; then R CMD check %s*tar.gz; fi"%(repo.name, repo.name),
        'install': "",
        'env' : "",
        'artifacts': "*.arti ",
        'reason': "Primary language",
        'error': "",
        'success': True }

    supported_langs = [ base_python_def, base_js_def, base_ruby_def, base_php_def,
                        base_perl_def, base_c_def, base_cxx_def, base_java_def,
                        base_scala_def, base_go_def, base_r_def ]

    # These definitions are added based on the presense of a specific build file.  We can
    # simply the command line provided by the base definition and grep for project and build
    # system specific parameters in README files.  eg. maven and MAVEN_OPTS
    ant_def = {
        'build system': "ant",
        'primary lang': "Java",
        'grep build': "ant build",
        'grep test' : "ant test",
        'grep install': "",
        'grep env': "ANT_OPTS=",
        'build': "ant",
        'test': "ant test",
        'install': "ant publish-local",
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
        'grep install': "",
        'grep env': "MAVEN_OPTS=",
        'build': "mvn dependency:list -DexcludeTransitive; mvn -DskipTests package",
        'test' : "mvn test -fn",
        'install': "mvn -DskipTests install",
        'env' : "",
        'artifacts': "*.arti",
        'reason': "pom.xml",
        'error': "",
        'success': True }

    gradle_def = {
        'build system': "gradle",
        'primary lang': "Java",
        'grep build': "",
        'grep test': "",
        'grep install': "",
        'grep env': "GRADLE_OPTS=",
        'build': "if [ -x gradlew ]; then ./gradlew build; else gradle -q build; fi",
        'test' : "gradle -q test",
        'install': "gradle -q uploadArchives",
        'env' : "",
        'artifacts': "*.arti",
        'reason': "build.gradle",
        'error': "",
        'success': True }

    cmake_def = {
        'build system': "C++_cmake",
        'primary lang': "C++",
        'grep build': "",
        'grep test': "make check",
        'grep install': "",
        'grep env': "CXXFLAGS=",
        'build': "cmake . ; if [ -x configure ]; then ./configure; fi; make",
        'test' : "getMakeTestTarget; make $TEST",
        'install': "",
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
        'grep install': "",
        'grep env': "CXXFLAGS=",
        'build': "scons all",
        'test' : "scons test",
        'install': "",
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
        'grep install': "",
        'grep env': "",
        'build': "sbt compile",
        'test' : "sbt test",
        'install': "",
        'env' : "",
        'artifacts': "*.arti",
        'reason': "build.sbt ",
        'error': "",
        'success': True }

    c_def = {
        'build system': "make",
        'primary lang': primaryLang,
        'grep build': "",
        'grep test': "make check",
        'grep install': "",
        'grep env': "CFLAGS=",
        'build': "if [ -x configure ]; then ./configure; fi; make",
        'test' : "getMakeTestTarget; make $TEST",
        'install' : "sudo make install",
        'env' : "",
        'artifacts': "*.arti",
        'reason': "Makefile",
        'error': "",
        'success': True }

    bootstrap_def = {
        'build system': "make",
        'primary lang': primaryLang,
        'grep build': "",
        'grep test': "make check",
        'grep install': "",
        'grep env': "CFLAGS=",
        'build': "if [ -x bootstrap.sh ]; then ./bootstrap.sh; elif [ -x autogen.sh ]; then ./autogen.sh; fi; if [ -x configure ]; then ./configure; fi; make",
        'test' : "getMakeTestTarget; make $TEST",
        'install': "sudo make install",
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
        'primary lang': primaryLang,
        'grep build': "",
        'grep test': "",
        'grep install': "",
        'grep env': "",
        'build': "",
        'test' : "",
        'install': "",
        'env' : "",
        'artifacts': "*.arti",
        'reason': ".travis.yml",
        'error': "",
        'success': True }

    buildsh_def = {
        'build system': "custom build script",
        'primary lang': primaryLang,
        'grep build': "build.sh",
        'grep test': "build.sh check",
        'grep install': "",
        'grep env': "",
        'build': "./build.sh",
        'test' : "./build.sh test",
        'install': "sudo ./build.sh install",
        'env' : "",
        'artifacts': "*.arti",
        'reason': "build.sh",
        'error': "",
        'success': True }

    base_empty_def['primary lang'] = primaryLang

    # Append empty language definition to list
    langlist = [ base_empty_def ]

    # Push primary language
    for lang in supported_langs:
        if lang['primary lang'] == primaryLang:
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
    directory_feed = []
    langlist_length = len(langlist)
    for f in listing:
        if f.type == 'dir':
            if f.name == "build" or f.name == "scripts" or f.name == "src":
                directory_feed.insert(0, f.path)
            else:
                directory_feed.append(f.path)
            continue
        if f.name == 'pom.xml':
            langlist.append(maven_def)         # If we find specific build files we can improve our commands by grepping readme's
        elif f.name == 'build.gradle':
            langlist.append(gradle_def)
        elif f.name == 'build.xml':
            langlist.append(ant_def)
        elif f.name == 'CMakeLists.txt':
            langlist.append(cmake_def)
        elif f.name in ('SConstruct', 'Sconstruct', 'sconstruct'):
            langlist.append(scons_def)
        elif f.name == 'build.sbt':
            langlist.append(sbt_def)
        elif f.name == 'package.json':
            langlist.append(base_js_def)      # Sometimes there is more CSS than JavaScript so base language is not recognized
        elif f.name == 'Makefile' or f.name == 'makefile':
            makefile = f
        elif f.name in ('bootstrap.sh', 'autogen.sh'):
            bootstrap = f
        elif f.name in ('build.sh', 'run_build.sh'):
            buildsh = f
        elif f.name == '.travis.yml':
            travis = interpretTravis(repo, f, travis_def)
        elif any(x in f.name.lower() for x in readmeFiles):
            if f.type == 'file' and f.size != 0 and not travis:
                try:
                    fstr = repo.get_file_contents(f.path).content.decode('base64', 'strict')
                    if fstr != "":
                        grepstack.insert(0, fstr)
                        logger.debug("inferBuildSteps: proj=%s, grepfile=%s" % (repo.name, f.name))
                except:
                    pass
    cmds = []
    subdirs = []
    if len(langlist) <= langlist_length and makefile == None and bootstrap == None and buildsh == None and travis == None:
        for directory in directory_feed:
            if "doc" in directory or "book" in directory or "example" in directory:
                continue
            logger.info("Looking for build files at %s/%s" % (repo.html_url, directory))
            listing = repo.get_dir_contents(directory)
            for f in listing:
                if f.name == 'pom.xml':
                    subdirs.append(directory)
                    cmds.append(maven_def)
                elif f.name == 'build.gradle':
                    subdirs.append(directory)
                    cmds.append(gradle_def)
                elif f.name == 'build.xml':
                    subdirs.append(directory)
                    cmds.append(ant_def)
                elif f.name == 'CMakeLists.txt':
                    subdirs.append(directory)
                    cmds.append(cmake_def)
                elif f.name in ('SConstruct', 'Sconstruct', 'sconstruct'):
                    subdirs.append(directory)
                    cmds.append(scons_def)
                elif f.name == 'build.sbt':
                    subdirs.append(directory)
                    cmds.append(sbt_def)
                elif f.name == 'package.json':
                    subdirs.append(directory)
                    cmds.append(base_js_def)
                elif f.name == 'Makefile' or f.name == 'makefile':
                    subdirs.append(directory)
                    makefile = f
                elif f.name in ('bootstrap.sh', 'autogen.sh'):
                    subdirs.append(directory)
                    bootstrap = f
                elif f.name in ('build.sh', 'run_build.sh'):
                    subdirs.append(directory)
                    buildsh = f
                elif f.name == '.travis.yml':
                    subdirs.append(directory)
                    travis = interpretTravis(repo, f, travis_def)
                elif any(x in f.name.lower() for x in readmeFiles):
                    if f.type == 'file' and f.size != 0 and not travis:
                        try:
                            fstr = repo.get_file_contents(f.path).content.decode('base64', 'strict')
                            if fstr != "":
                                grepstack.insert(0, fstr)
                                logger.debug("inferBuildSteps: proj=%s, grepfile=%s" % (repo.name, f.name))
                        except:
                            pass
        if len(cmds) > 0 and len(subdirs) > 0:
            cmd = cmds[-1]
            subdir = subdirs[-1]
            cmd['build'] = "cd ./%s; %s" %(subdir,cmd['build'])
            cmd['test'] = "cd ./%s; %s" %(subdir, cmd['test'])
            langlist.append(cmd)

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
    if len(subdirs) > 0:
        subdir = subdirs[-1]
    if travis != None:
        if len(subdirs) > 0:
            travis_def['build'] = "cd ./%s; %s" %(subdir,travis_def['build'])
            travis_def['test'] = "cd ./%s; %s" %(subdir,travis_def['test'])
            langlist.append(travis_def)
        else:
            langlist.append(travis_def)
    elif buildsh != None:
        if len(subdirs) > 0:
            buildsh_def['build'] = "cd ./%s; %s" %(subdir,buildsh_def['build'])
            buildsh_def['test'] = "cd ./%s; %s" %(subdir,buildsh_def['test'])
            langlist.append(buildsh_def)
        else:
            langlist.append(buildsh_def)
    elif bootstrap != None:
        if len(subdirs) > 0:
            bootstrap_def['build'] = "cd ./%s; %s" %(subdir, bootstrap_def['build'])
            bootstrap_def['test'] = "cd ./%s; %s" %(subdir, bootstrap_def['test'])
            langlist.append(bootstrap_def)
        else:
            langlist.append(bootstrap_def)
    elif makefile != None:
        if len(subdirs) > 0:
            buildVal = c_def['build']
            c_def['build'] = "cd ./%s; %s" %(subdir, c_def['build'])
            c_def['test'] = "cd ./%s; %s" %(subdir, c_def['test'])
            langlist.append(c_def)
        else:
            langlist.append(c_def)

    # Add each template match to build info in the order they were found
    for lang in langlist:
        if lang['build']:
            build_info['buildOptions'].append(lang['build'])
        if lang['test']:
            build_info['testOptions'].append(lang['test'])
        if lang['install']:
            build_info['installOptions'].append(lang['install'])
        if lang['env']:
            build_info['envOptions'].append(lang['env'])
        build_info['reason'] = lang['reason']
        build_info['primaryLang'] = lang['primary lang']

    # Check the last element added to the langlist for readme/other important file info
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
                    cmd = lang['grep install']
                    if cmd and cmd.find('$') == -1:
                        strFound = buildFilesParser(readmeStr, cmd, delim)
                        if strFound:
                            build_info['installOptions'].append(strFound)
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

            # Text analytics is deactivated until there is significant progress.  It can
            # still be enabled via the settings menu, but the recommendation is always
            # put last.  This effectively hides it but allows continued development.
            if globals.useTextAnalytics:
                # Add build commands extracted using text analytics
                command = text_analytics_cmds(repo.name, primaryLang, grepstack, 'build')
                if command:
#                   if globals.useTextAnalytics:
                    if False:
                        build_info['buildOptions'].insert(len(build_info), '[TextAnalytics]' + command)
                    else:
                        build_info['buildOptions'].insert(0, '[TextAnalytics]' + command)

                # Add test commands extracted using text analytics
                command = text_analytics_cmds(repo.name, primaryLang, grepstack, 'test')
                if command:
#                   if globals.useTextAnalytics:
                    if False:
                        build_info['testOptions'].insert(len(build_info), '[TextAnalytics]' + command)
                    else:
                        build_info['testOptions'].insert(0, '[TextAnalytics]' + command)
                # Add install commands extracted using text analytics
                if command:
#                   if globals.useTextAnalytics:
                    if False:
                        build_info['installOptions'].insert(len(build_info), '[TextAnalytics]' + command)
                    else:
                        build_info['installOptions'].insert(0, '[TextAnalytics]' + command)
    if globals.enableKnowledgeBase and mongoClient is not None:
        logger.debug("inferBuildSteps: knowledge base is enabled")
        repoURL = repo.html_url
        repoVersion = 'current'
        repoURL = repoURL.replace('.','_')
        query_dict = { repoURL+'.'+repoVersion : { '$exists' : True } }
        logger.debug("inferBuildSteps: Fetching recommendation for repoURL = %s,\
                      repoVersion = %s" %(repo.html_url,repoVersion))
        record = mongoClient.queryForRecord(query_dict)
        build_info.update({'recommendations':''})
        if record.count() > 0:
            try:
                logger.debug("inferBuildSteps: Recommendation for repoURL = %s," \
                              "repoVersion = %s found" %(repo.html_url,repoVersion))
                record = record.next()
                recomendationDict = record[repoURL][repoVersion]
                retVal = compareNodes(recomendationDict['build_nodes'])
                recomendationDict['build_cmd'] = recomendationDict['build_cmd'].replace('\n',' ')
                recomendationDict['test_cmd'] = recomendationDict['test_cmd'].replace('\n',' ')
                recomendationDict['env'] = recomendationDict['env']
                if retVal:
                    if recomendationDict['build_cmd'] not in build_info['buildOptions']:
                        build_info['buildOptions'].append(recomendationDict['build_cmd'])
                        build_info['reason'] = 'Autoport Knowledge Base'
                        if recomendationDict['test_cmd'] and \
                           recomendationDict['test_cmd'] not in build_info['testOptions']:
                            build_info['testOptions'].append(recomendationDict['test_cmd'])
                        if recomendationDict['env'] and \
                           recomendationDict['env'] not in build_info['envOptions']:
                            build_info['envOptions'].append(recomendationDict['env'])
                    else:
                        if build_info['buildOptions'][-1] != recomendationDict['build_cmd']:
                            build_info['buildOptions'].remove(recomendationDict['build_cmd'])
                            build_info['buildOptions'].append(recomendationDict['build_cmd'])
                            build_info['reason'] = 'Autoport Knowledge Base'
                            if recomendationDict['test_cmd'] and \
                               recomendationDict['test_cmd'] in build_info['testOptions']:
                                build_info['testOptions'].remove(recomendationDict['test_cmd'])
                                build_info['testOptions'].append(recomendationDict['test_cmd'])
                            elif recomendationDict['test_cmd']:
                                build_info['testOptions'].append(recomendationDict['test_cmd'])
                            if recomendationDict['env'] and \
                               recomendationDict['env'] in build_info['envOptions']:
                                build_info['envOptions'].remove(recomendationDict['env'])
                                build_info['envOptions'].append(recomendationDict['env'])
                            elif recomendationDict['env']:
                                build_info['envOptions'].append(recomendationDict['env'])

                if record[repoURL][repoVersion]['build_cmd'] not in build_info['buildOptions']:
                    recomendationDict.update({'url':repo.html_url})
                    recomendationDict.update({'packageName':repo.name})
                    recomendationDict.update({'packageVersion':'current'})
                    build_info['recommendations'] = recomendationDict
            except Exception as e:
                logger.warning("inferBuildSteps: recommendations error %s" %(str(e)))

    # Make the build, test, and env options of the last added element the default options
    # as those are the most likely to be correct
    if build_info['buildOptions']:
        build_info['success'] = True
        build_info['selectedBuild'] = build_info['buildOptions'][-1]
        if build_info['testOptions']:
            build_info['selectedTest'] = build_info['testOptions'][-1]
        if build_info['installOptions']:
            build_info['selectedInstall'] = build_info['installOptions'][-1]
        if build_info['envOptions']:
            build_info['selectedEnv'] = build_info['envOptions'][-1]

    logger.debug("Leaving inferBuildSteps, proj=%s, env=%s" % (repo.name, build_info['selectedEnv']))
    logger.debug("Leaving inferBuildSteps, proj=%s, build cmd=%s" % (repo.name, build_info['selectedBuild']))
    logger.debug("Leaving inferBuildSteps, proj=%s, test cmd=%s" % (repo.name, build_info['selectedTest']))
    logger.debug("Leaving inferBuildSteps, proj=%s, install cmd=%s" % (repo.name, build_info['selectedInstall']))

    return build_info

# This routine is used to compare the selected nodes with
# total number of slave nodes available
def compareNodes(nodes):
   matched = True
   for node in globals.nodeLabels:
       if node not in nodes:
           matched = False
   return matched


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
