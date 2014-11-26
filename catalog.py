import paramiko
import tempfile
import shutil
import os
import globals

class Catalog:
    def __init__(self, hostname, username=globals.jenkinsGsaUsername,
            password=globals.jenkinsGsaPassword,
            gsaPath=globals.gsaPathForTestResults,
            localPath=globals.localPathForTestResults):
        assert(hostname != None and username != "" and password != "")
        self.__host = hostname
        self.__username = username
        self.__password = password
        self.__gsaPath = gsaPath
        self.__localPath = localPath
        self.__tmpdirs = []
        try:
            self.__sshClient = paramiko.SSHClient()
            self.__sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.__sshClient.connect(self.__host, username=self.__username, password=self.__password)
            self.__ftpClient = self.__sshClient.open_sftp()
        except IOError:
            assert(False)

    def listJobResults(self, repoType, filt):
        res = []
        if repoType == "gsa" or repoType == "all":
            res = self.listGSAJobResults(filt)
        if repoType == "local" or repoType == "all":
            res = res + self.listLocalJobResults(filt)
        return res

    def listLocalJobResults(self, filt):
        filteredList = []
        try:
            print "Getting list of archived jenkins job results"
            fullList = os.listdir(self.__localPath)
            filteredList = []
            for item in fullList:
                if filt in item.lower() or filt == "":
                    filteredList.append([item, "local"])
        except IOError:
            pass
        return filteredList

    def listGSAJobResults(self, filt):
        filteredList = []
        try:
            print "Getting list of archived jenkins job results"
            self.__ftpClient.chdir(self.__gsaPath)
            fullList = self.__ftpClient.listdir()
            filteredList = []
            for item in fullList:
                if filt in item.lower() or filt == "":
                    filteredList.append([item, "gsa"])
        except IOError:
            pass
        return filteredList

    def getResults(self, build, repository):
        if repository == "gsa":
            return self.getGSAResults(build)
        elif repository == "local":
            return self.getLocalResults(build)

    def getLocalResults(self, build):
        return self.__localPath+"/"+build

    def getGSAResults(self, build):
        try:
            putdir = tempfile.mkdtemp(prefix="autoport_")
            self.__ftpClient.chdir(self.__gsaPath+"/"+build)
            self.__ftpClient.get("meta.arti", putdir+"/meta.arti")
            self.__ftpClient.get("dependency.arti", putdir+"/dependency.arti")
            self.__ftpClient.get("test_result.arti", putdir+"/test_result.arti")
            self.__tmpdirs.append(putdir)
            return putdir
        except IOError:
            return None

    def cleanTmp(self):
        for tmpdir in self.__tmpdirs:
            if os.path.exists(tmpdir):
                shutil.rmtree(tmpdir)
        tmpdir = []

    def close(self):
        self.__ftpClient.close()
        self.cleanTmp()

    def __del__(self):
        self.close()

