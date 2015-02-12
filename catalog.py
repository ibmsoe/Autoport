import paramiko
import tempfile
import shutil
import os
import globals

class Catalog:
    def __init__(self, archiveHost, jenkinsHost,
            archiveUser=globals.configUsername,
            archivePassword=globals.configPassword,
            jenkinsUser=globals.configJenkinsUsername,
            jenkinsKey=globals.configJenkinsKey,
            copyPath=globals.pathForTestResults,
            localPath=globals.localPathForTestResults):
        #assert(archiveHost != None and archiveUser != "" and archivePassword != "")
        self.__archiveHost = archiveHost
        self.__archiveUser = archiveUser
        self.__archivePassword = archivePassword
        self.__jenkinsHost = jenkinsHost
        self.__jenkinsUser = jenkinsUser
        self.__jenkinsKey = jenkinsKey
        self.__copyPath = copyPath
        self.__localPath = localPath
        self.__tmpdirs = []
        try:
            self.__archiveSshClient = paramiko.SSHClient()
            self.__archiveSshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.__archiveSshClient.connect(self.__archiveHost, username=self.__archiveUser, password=self.__archivePassword)
            self.__archiveFtpClient = self.__archiveSshClient.open_sftp()

            self.__jenkinsSshClient = paramiko.SSHClient()
            self.__jenkinsSshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.__jenkinsSshClient.connect(self.__jenkinsHost, username=self.__jenkinsUser, key_filename=self.__jenkinsKey)
            self.__jenkinsFtpClient = self.__jenkinsSshClient.open_sftp()
        except IOError as e:
            print str(e)
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
            self.__jenkinsFtpClient.chdir(self.__localPath)
            fullList = self.__jenkinsFtpClient.listdir()
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
            self.__archiveFtpClient.chdir(self.__copyPath)
            fullList = self.__archiveFtpClient.listdir()
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
        try:
            putdir = tempfile.mkdtemp(prefix="autoport_")
            self.__jenkinsFtpClient.chdir(self.__localPath+build)
            self.__jenkinsFtpClient.get("meta.arti", putdir+"/meta.arti")
            self.__jenkinsFtpClient.get("dependency.arti", putdir+"/dependency.arti")
            self.__jenkinsFtpClient.get("test_result.arti", putdir+"/test_result.arti")
            self.__tmpdirs.append(putdir)
            return putdir
        except IOError as e:
            print "Exception:",str(e)
            return None

    def getGSAResults(self, build):
        try:
            putdir = tempfile.mkdtemp(prefix="autoport_")
            self.__archiveFtpClient.chdir(self.__copyPath+build)
            self.__archiveFtpClient.get("meta.arti", putdir+"/meta.arti")
            self.__archiveFtpClient.get("dependency.arti", putdir+"/dependency.arti")
            self.__archiveFtpClient.get("test_result.arti", putdir+"/test_result.arti")
            self.__tmpdirs.append(putdir)
            return putdir
        except IOError:
            return None

    def archiveResults(self, builds):
        errors = []
        alreadyThere = []
        for build in builds:
            try:
                self.__archiveFtpClient.stat(self.__copyPath+build)
                alreadyThere.append(build)
                continue
            except IOError as e:
                pass # Directory's not there, try to add it
            try:
                tmpDir = self.getLocalResults(build)
                if tmpDir == None:
                    print "Can't fetch jenkins copy of",build
                    errors.append(build)
                    continue
                self.__archiveFtpClient.mkdir(self.__copyPath+build)
                self.__archiveFtpClient.put(tmpDir+"/meta.arti",
                                     self.__copyPath+build+"/meta.arti")
                self.__archiveFtpClient.put(tmpDir+"/dependency.arti",
                                     self.__copyPath+build+"/dependency.arti")
                self.__archiveFtpClient.put(tmpDir+"/test_result.arti",
                                     self.__copyPath+build+"/test_result.arti")
            except IOError as e:
                print "Can't push ",build,": exception=",str(e)
                errors.append(build)
            # remove the 'local' copy
            try:
                self.__jenkinsFtpClient.remove(self.__localPath+build+"/meta.arti")
                self.__jenkinsFtpClient.remove(self.__localPath+build+"/dependency.arti")
                self.__jenkinsFtpClient.remove(self.__localPath+build+"/test_result.arti")
                self.__jenkinsFtpClient.rmdir(self.__localPath+build)
            except IOError as e:
                print "Can't remove local copy of",build,": exception=",str(e)
        for directory in errors:
            try:
                self.__archiveFtpClient.stat(self.__copyPath+directory)
            except IOError as e:
                if 'No such file' in str(e):
                    continue
            try:
                files = self.__archiveFtpClient.listdir()
                for f in files:
                    self.__archiveFtpClient.unlink(self.__copyPath+directory+'/'+f)
                self.__archiveFtpClient.rmdir(self.__copyPath+directory)
            except IOError as e:
                print "Can't remove directory",self.__copyPath+directory,":",str(e)
        return errors, alreadyThere

    def cleanTmp(self):
        for tmpdir in self.__tmpdirs:
            if os.path.exists(tmpdir):
                shutil.rmtree(tmpdir)
        tmpdir = []

    def close(self):
        self.__archiveFtpClient.close()
        self.__jenkinsFtpClient.close()
        self.cleanTmp()

    def __del__(self):
        self.close()

