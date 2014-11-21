import paramiko
import tempfile
import shutil
import os
import globals

class Catalog:
    def __init__(self, hostname, username=globals.jenkinsGsaUsername,
            password=globals.jenkinsGsaPassword,
            path=globals.gsaPathForTestResults):
        assert(hostname != None and username != "" and password != "")
        self.__host = hostname
        self.__username = username
        self.__password = password
        self.__path = path
        self.__tmpdirs = []
        try:
            self.__sshClient = paramiko.SSHClient()
            self.__sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.__sshClient.connect(self.__host, username=self.__username, password=self.__password)
            self.__ftpClient = self.__sshClient.open_sftp()
        except IOError:
            assert(False)

    # TODO make use of repoType, also probably build a json object here instead of a list of strings
    def listJobResults(self, repoType, filt):
        filteredList = []
        if repoType == "gsa" or repoType == "all":
            try:
                print "Getting list of archived jenkins job results"
                self.__ftpClient.chdir(self.__path)
                fullList = self.__ftpClient.listdir()
                if filt == "":
                    return fullList
                filteredList = []
                for item in fullList:
                    print item
                    if filt in item.lower():
                        print filt," -> ",item
                        filteredList.append({item, "gsa"})
            except IOError:
                pass
        elif repoType == "local" or repoType == "all":
            # TODO check if an archived version is already there
            #      for each local one?
            pass
        return filteredList

    def getResults(self, build):
        try:
            putdir = tempfile.mkdtemp(prefix="autoport_")
            self.__ftpClient.chdir(self.__path+"/"+build)
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

