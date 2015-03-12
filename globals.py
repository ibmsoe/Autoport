import ConfigParser
import os
import paramiko
from github import Github
from cache import Cache
from threadpool import ThreadPool
from urlparse import urlparse

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
    global mavenPath
    global githubToken

    global hostname

    global configUsername
    global configPassword
    global configJenkinsUsername
    global configJenkinsKey
    global pathForTestResults
    global pathForBatchFiles
    global localPathForTestResults
    global localPathForBatchFiles
    global jobNamePrefix
    global artifactsPathPrefix
    global threadPoolSize

    # unchanging project configurations
    global github
    global cache
    global nodes
    global sshClient
    global ftpClient
    global threadPool

    jenkinsUrl = configOptions['jenkinsurl']
    mavenPath = configOptions['mavenpath']
    githubToken = configOptions['githubtoken']

    hostname = configOptions['hostname']

    configUsername = configOptions['username']
    configPassword = configOptions['password']
    configJenkinsUsername = configOptions['jenkinsusername']
    configJenkinsKey = configOptions['autoportjenkinskey']
    pathForTestResults = configOptions['pathfortestresults']
    pathForBatchFiles = configOptions['pathforbatchfiles']
    localPathForTestResults = configOptions['localpathfortestresults']
    localPathForBatchFiles = configOptions['localpathforbatchfiles']
    jobNamePrefix = configOptions['jobnameprefix']
    artifactsPathPrefix = configOptions['artifactspathprefix']
    threadPoolSize = int(configOptions['threadpoolsize'])

    # need to use the token to be able to perform more requests per hour
    github = Github(githubToken)

    # used for caching repo data
    cache = Cache(github)

    # Jenkins slave node pools
    nodes = {'x86': "x86", 'ppcle': "ppcle"}
   
    # create pool of worker threads that query Jenkins for job completion 
    threadPool = ThreadPool(threadPoolSize)

    # setup global SSH and FTP clients connected to Jenkins master
    sshClient = paramiko.SSHClient()
    sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    sshClient.connect(urlparse(jenkinsUrl).hostname, username=configJenkinsUsername, key_filename=configJenkinsKey)
    ftpClient = sshClient.open_sftp()
