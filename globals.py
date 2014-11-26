import ConfigParser
import os
from github import Github
from cache import Cache

# Config Globals
# All global variables should be here
def init():

    # parse global data
    config = ConfigParser.ConfigParser()
    config.read("./config.ini")

    configOptions = {}
    sections = config.sections()
    for section in sections:
        options = config.options(section)
        for option in options:
            try:
                configOptions[option] = config.get(section, option)
                if configOptions[option] == -1:
                    DebugPrint("skip: %s" % option)
            except:
                print("exception on %s!" % option)
                configOptions[option] = None


    # changeable project configurations
    global jenkinsUrl
    global gsaPathForTestResults
    global gsaPathForBatchFiles
    global mavenPath
    global githubToken
    global hostname
    global jenkinsGsaUsername
    global jenkinsGsaPassword
    global localPathForTestResults

    # unchanging project configurations
    global jobNamePrefix
    global batch_folder
    global test_folder
    global github
    global cache
    global nodes

    jenkinsUrl = configOptions['jenkinsurl']
    gsaPathForTestResults = configOptions['gsapathfortestresults']
    gsaPathForBatchFiles = configOptions['gsapathforbatchfiles']
    mavenPath = configOptions['mavenpath']
    githubToken = configOptions['githubtoken']
    hostname = configOptions['hostname']
    jenkinsGsaUsername = configOptions['jenkinsgsausername']
    jenkinsGsaPassword = configOptions['jenkinsgsapassword']
    localPathForTestResults = configOptions['localpathfortestresults']

    jobNamePrefix = "NewListTest" #Autoport
    batch_folder = "./" + os.path.basename(gsaPathForBatchFiles) + "/"
    test_folder = "./" + os.path.basename(gsaPathForTestResults) + "/"
    github = Github(githubToken)
    cache = Cache(github)
    nodes = {'x86': "x86", 'ppcle': "ppcle"}
