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
    global jenkinsHome
    global jenkinsHostname
    global githubToken
    global configHostname
    global configPort
    global configUsername
    global configPassword
    global configJenkinsUsername
    global configJenkinsPassword
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
    global enableKnowledgeBase
    global connectionURL
    global connectionPort
    global dbUsername
    global dbPassword
    global dbName
    global dbCollectionName
    global stackApiKey
    global enableTagSearch

    # user configuration globals that are supported by the user interface
    githubToken = configOptions['githubtoken']
    configHostname = configOptions['hostname']
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
    enableKnowledgeBase = configOptions['enableknowledgebase'] == 'True'
    stackApiKey = configOptions['stackapikey']
    enableTagSearch = configOptions['enabletagsearch'] == 'True'

    # user configuration globals that are not supported by the user interface
    expiryForTmp = configOptions['expiryfortmp']
    if not configOptions.has_key('port'):
        configPort = 22
    else:
        configPort = int(configOptions['port'])

    # Apparently nginx reverse proxy with stacked urls - http://server-x:8800/server-y:8080/
    # requires a trailing slash(/) character, so the input value may include it.  Normalize
    # input to not include it as url manipulation elsewhere adds it as required
    jenkinsUrl = configOptions['jenkinsurl']
    if not jenkinsUrl or "<" in jenkinsUrl:
        jenkinsUrl = ""
    elif jenkinsUrl[-1] == '/':
        jenkinsUrl = jenkinsUrl[:-1]

    # This field is used to open socket connections.  A second field is provided so that an
    # IP Address or alternate hostname may be given as a proxy server may be used to provide
    # access to jenkinsUrl.
    jenkinsHostname = configOptions['jenkinshostname']
    if jenkinsUrl:
        if not jenkinsHostname or "<" in jenkinsHostname:
           jenkinsHostname = urlparse(jenkinsUrl).hostname
    else:
        jenkinsHostname = ""

    jenkinsHome = configOptions['jenkinshome']
    if jenkinsHome:
        if not jenkinsHome or "<" in jenkinsHome:
           jenkinsHome = "/home/jenkins/jenkins_home"

    configJenkinsPassword = configOptions['jenkinspassword']
    if not configJenkinsPassword or "<" in configJenkinsPassword:
        configJenkinsPassword = ""

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
    global sftpConnected
    global auth

    # need to use the token to be able to perform more requests per hour
    github = Github(githubToken)

    # used for caching repo data
    cache = Cache(github)

    # create pool of worker threads that query Jenkins for job completion
    threadPool = ThreadPool(threadPoolSize)

    # get local short hostname to prefix to job names
    localHostName = socket.gethostname().split('.')[0]

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

    auth = ""

    # if substring length not greater than 4 means port is not part of URL
    jenkinsUrlSubStringLength = jenkinsUrl.rfind(':')
    if jenkinsUrlSubStringLength > 4:
        jenkinsUrlNoPort = jenkinsUrl[:jenkinsUrl.rfind(':')]
    else:
        jenkinsUrlNoPort = jenkinsUrl

    jenkinsRepoUrl = '%s:%s/autoport_repo/archives' % (jenkinsUrlNoPort, '90')
    localTarRepoLocation = '/var/opt/autoport/'
    sftpConnected = False

    # used for rebuilding jenkins slaves in a cloud environment
    global os_username
    global os_password
    global os_tenant_name
    global os_auth_url

    if configOptions.has_key('os_username'):
        os_username = configOptions['os_username']
        os_password = configOptions['os_password']
        os_tenant_name = configOptions['os_tenant_name']
        os_auth_url = configOptions['os_auth_url']
    else:
        os_username = ""
        os_password = ""
        os_tenant_name = ""
        os_auth_url = ""

    # used for enabling knowledge base feature
    if enableKnowledgeBase:
        connectionURL = configOptions['connectionurl']
        connectionPort = configOptions['connectionport']
        dbUsername = configOptions['dbusername']
        dbPassword = configOptions['dbpassword']
        dbName = configOptions['dbname']
        dbCollectionName = configOptions['dbcollectionname']

    # used for seraching errors in logs using stackExchange api
    if not stackApiKey or "<" in stackApiKey:
        stackApiKey = None
