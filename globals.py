import ConfigParser
import os
import paramiko
import socket
from github import Github
from cache import Cache
from threadpool import ThreadPool
from urlparse import urlparse

# Config Globals
# All global variables should be here
def init():
    # parse global data from config file
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

    # globals based on config file
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
    global artifactsPathPrefix
    global threadPoolSize
    global minRandom
    global maxRandom

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
    artifactsPathPrefix = configOptions['artifactspathprefix']
    threadPoolSize = int(configOptions['threadpoolsize'])
    minRandom = int(configOptions['minrandom'])
    maxRandom = int(configOptions['maxrandom'])
    
    # globals not based on config file
    global github
    global cache
    global nodes
    global sshClient
    global ftpClient
    global threadPool
    global localHostName

    # need to use the token to be able to perform more requests per hour
    github = Github(githubToken)

    # used for caching repo data
    cache = Cache(github)

    # Jenkins slave node pools
    nodes = {'x86': "x86", 'ppcle': "ppcle"}
   
    # create pool of worker threads that query Jenkins for job completion 
    threadPool = ThreadPool(threadPoolSize)

    # get local hostname to append to job names
    localHostName = socket.gethostname()

    # setup global SSH and FTP clients connected to Jenkins master
    sshClient = paramiko.SSHClient()
    sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    sshClient.connect(urlparse(jenkinsUrl).hostname, username=configJenkinsUsername, key_filename=configJenkinsKey)
    ftpClient = sshClient.open_sftp()
