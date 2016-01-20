import ConfigParser
import os
import paramiko
import socket
import logging
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

    # First initialize logging level
    global logLevel
    logLevel = configOptions['loglevel']
    lvl = getattr(logging, logLevel.upper(), None)
    if not isinstance(lvl, int):
        logLevel = "INFO"

    # Globals based on config file
    global jenkinsUrl
    global githubToken
    global hostname
    global port
    global configUsername
    global configPassword
    global configJenkinsUsername
    global configJenkinsKey
    global pathForTestResults
    global pathForBatchTestResults
    global pathForBatchFiles
    global localPathForTestResults
    global localPathForBatchFiles
    global localPathForBatchTestResults
    global artifactsPathPrefix
    global threadPoolSize
    global useTextAnalytics
    global expiryForTmp

    # user configuration globals that are supported by the user interface
    jenkinsUrl = configOptions['jenkinsurl']
    githubToken = configOptions['githubtoken']
    hostname = configOptions['hostname']
    configUsername = configOptions['username']
    configPassword = configOptions['password']
    configJenkinsUsername = configOptions['jenkinsusername']
    configJenkinsKey = configOptions['autoportjenkinskey']
    pathForTestResults = configOptions['pathfortestresults']
    pathForBatchTestResults = configOptions['pathforbatchtestresults']
    pathForBatchFiles = configOptions['pathforbatchfiles']
    localPathForTestResults = configOptions['localpathfortestresults']
    localPathForBatchFiles = configOptions['localpathforbatchfiles']
    localPathForBatchTestResults = configOptions['localpathforbatchtestresults']
    artifactsPathPrefix = configOptions['artifactspathprefix']
    threadPoolSize = int(configOptions['threadpoolsize'])
    useTextAnalytics = configOptions['usetextanalytics'] == 'True'
    expiryForTmp = configOptions['expiryfortmp']

    if not configOptions.has_key('port'):
        port = 22
    else:
        port = int(configOptions['port'])

    # globals not based on config file
    global github
    global cache
    global nodeLabels
    global nodeNames
    global nodeOSes
    global nodeHosts
    global nodeIPs
    global nodeDetails
    global nodeUbuntu
    global nodeRHEL
    global nodeCentOS
    global sshClient
    global ftpClient
    global threadPool
    global localHostName
    global minRandom
    global maxRandom
    global localPathForListResults
    global localPathForConfig
    global localPathForPackages
    global localPathForChefLogs
    global allocBuildServers
    global jenkinsRepoUrl
    global localTarRepoLocation
    global gsaConnected


    # need to use the token to be able to perform more requests per hour
    github = Github(githubToken)

    # used for caching repo data
    cache = Cache(github)

    # create pool of worker threads that query Jenkins for job completion
    threadPool = ThreadPool(threadPoolSize)

    # get local hostname to append to job names
    localHostName = socket.gethostname()

    # set random number range for UUID
    minRandom = 100000
    maxRandom = 999999

    localPathForListResults="./data/list_results/"
    localPathForConfig="./data/config/"
    localPathForPackages="./data/packages/"
    localPathForChefLogs="./data/chef_logs/"

    nodeLabels = []
    nodeNames = []
    nodeIPs = []
    nodeDetails = []
    nodeUbuntu = []
    nodeRHEL = []
    nodeCentOS = []
    nodeOSes = []
    nodeHosts = []

    allocBuildServers = False

    # if substring length not greater than 4 means port is not part of URL
    jenkinsUrlSubStringLength = jenkinsUrl.rfind(':')
    if jenkinsUrlSubStringLength > 4:
        jenkinsUrlNoPort = jenkinsUrl[:jenkinsUrl.rfind(':')]
    else:
        jenkinsUrlNoPort = jenkinsUrl

    jenkinsRepoUrl = '%s:%s/autoport_repo/archives' % (jenkinsUrlNoPort, '90')
    localTarRepoLocation = '/var/opt/autoport/'
    gsaConnected = False
