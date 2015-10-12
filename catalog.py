import paramiko
import tempfile
import shutil
import os
import re
import shutil
import globals
from stat import S_ISDIR
from log import logger

resultPattern = re.compile('(.*?)\.(.*?)\.(.*?)\.N-(.*?)\.(.*?)\.(\d\d\d\d-\d\d-\d\d-h\d\d-m\d\d-s\d\d)')

class Catalog:
    def connect(self, archiveHost, jenkinsHost,
            archivePort=globals.port,
            archiveUser=globals.configUsername,
            archivePassword=globals.configPassword,
            jenkinsUser=globals.configJenkinsUsername,
            jenkinsKey=globals.configJenkinsKey,
            copyPath=globals.pathForTestResults,
            localPath=globals.localPathForTestResults):
        self.__archiveHost = archiveHost
        self.__archivePort = archivePort
        self.__archiveUser = archiveUser
        self.__archivePassword = archivePassword
        self.__jenkinsHost = jenkinsHost
        self.__jenkinsUser = jenkinsUser
        self.__jenkinsKey = jenkinsKey
        self.__copyPath = copyPath
        self.__localPath = localPath
        self.__tmpdirs = []

        try:
            self.__jenkinsSshClient = paramiko.SSHClient()
            self.__jenkinsSshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.__jenkinsSshClient.connect(self.__jenkinsHost, username=self.__jenkinsUser, \
                                            key_filename=self.__jenkinsKey)
            self.__jenkinsFtpClient = self.__jenkinsSshClient.open_sftp()
        # Error handling
        except paramiko.AuthenticationException as ae:
            msg = "Please provide valid Jenkins credentials in settings menu!"
            logger.warning(msg)
            assert(False), msg
        except paramiko.SSHException as se:
            msg = "SSH connection error to Jenkins.  You may need to authenticate.  Check networking!"
            logger.warning(msg)
            assert(False), msg
        except IOError as e:
            msg = str(e) + ". Please ensure that the Jenkins URL is correct in the settings menu!"
            logger.warning(msg)
            assert(False), msg

        try:
            globals.gsaConnected = False
            self.__archiveSshClient = paramiko.SSHClient()
            self.__archiveSshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.__archiveSshClient.connect(self.__archiveHost, username=self.__archiveUser,\
                                            password=self.__archivePassword,port=self.__archivePort)
            self.__archiveFtpClient = self.__archiveSshClient.open_sftp()
            globals.gsaConnected = True
        # Error handling
        except paramiko.AuthenticationException as ae:
            logger.warning("Connection error to archive storage")
            logger.warning("Use settings menu to specify your user credentials!")
        except paramiko.SSHException as se:
            logger.warning("SSH connection error to archive storage")
            logger.warning("You may need to authenticate.  Check networking!")
        except IOError as e:
            logger.warning(str(e))
            logger.warning("Please ensure that the archive hostname is correct in the settings menu!")

    def listJobResults(self, repoType, filt):
        results = []

        jobs = []
        try:
            if repoType == "local" or repoType == "all":
                jobs = self.listLocalJobResults(filt)

            if repoType == "gsa" or repoType == "all":
                jobs = jobs + self.listGSAJobResults(filt)
        except Exception as e:
            logger.warning(str(e))
            assert(False), str(e)

        for jobDesc in jobs:
             job = jobDesc[0]
             repo = jobDesc[1]

             # Validate that the directory looks like a test result
             try:
                 nodeLabel = resultPattern.match(job).group(3)
                 pkgName = resultPattern.match(job).group(4)
                 pkgVer = resultPattern.match(job).group(5)
                 date = resultPattern.match(job).group(6)
             except AttributeError:
                 continue

             # The node may not be known to this autoport instance.  Jobs
             # are aggregated in gsa.  Jenkin build nodes may be retired
             if nodeLabel in globals.nodeLabels:
                 i = globals.nodeLabels.index(nodeLabel)
                 distro = globals.nodeOSes[i]
             else:
                 distro = nodeLabel

             results.append({'fullName': job,
                             'name': pkgName,
                             'version': pkgVer,
                             'os': distro,
                             'repository': repo,
                             'completed': date,
                             'server': nodeLabel})
        return results

    def listLocalJobResults(self, filt):
        filteredList = []
        try:
            fullList = os.listdir(self.__localPath)
            for item in fullList:
                if item == ".gitignore":
                    continue
                if filt in item.lower() or filt == "":
                    filteredList.append([item, "local"])
        except IOError:
            msg = "Please provide valid local test results path in settings menu!"
            log.warning(msg)
            assert(False), msg
        except OSError as e:
            msg = "Please provide valid local test results path in settings menu!"
            log.warning(msg)
            assert(False), msg
        return filteredList

    def listGSAJobResults(self, filt):
        filteredList = []
        try:
            self.__archiveFtpClient.chdir(self.__copyPath)
            fullList = self.__archiveFtpClient.listdir()
            for item in fullList:
                if filt in item.lower() or filt == "":
                    filteredList.append([item, "gsa"])
        except IOError as e:
            log.warning(str(e))
            assert(False), str(e)
        except AttributeError as e:
            msg = "Connection error to archive storage.  Use settings menu to configure!"
            logger.warning(msg)
            assert(False), msg
        return filteredList

    def getResults(self, build, repository):
        if repository == "gsa":
            return self.getGSAResults(build)
        elif repository == "local":
            return self.getLocalResults(build)

    def getLocalResults(self, build):
        try:
            localPath = self.__localPath + build + "/"
            putdir = tempfile.mkdtemp(prefix="autoport_")

            # Copy as many files as possible.  Reports use different files
            files = os.listdir(localPath)
            for file in files:
                try:
                    shutil.copyfile(localPath+file, putdir + "/" + file)
                except IOError:
                    pass
            self.__tmpdirs.append(putdir)
            return putdir
        except IOError as e:
            msg = "Exception: " + str(e)
            logger.warning(msg)
            return None
        except Exception,e:
            msg = "Exception: " + str(e)
            logger.warning(msg)
            return None

    def getGSAResults(self, build):
        try:
            putdir = tempfile.mkdtemp(prefix="autoport_")
            self.__archiveFtpClient.chdir(self.__copyPath + build)

            # Copy as many files as possible.  Reports use different files
            files = self.__archiveFtpClient.listdir()
            for file in files:
                try:
                    self.__archiveFtpClient.get(file, putdir + "/" + file)
                except IOError:
                    pass
            self.__tmpdirs.append(putdir)
            return putdir
        except AttributeError:
            msg = "Connection error to archive storage.  Use settings menu to configure!"
            logger.warning(msg)
            assert(False), msg
        except IOError as e:
            msg = "Exception: " + str(e)
            logger.warning(msg)
            return None
        except Exception,e:
            msg = "Exception: " + str(e)
            logger.warning(msg)
            return None

    def archiveResults(self, builds):
        status = "ok"
        errors = []
        alreadyThere = []
        copied = []
        logger.debug("In archiveResults, builds=%s" % str(builds))
        for build in builds:
            remoteBuildPath = self.__copyPath + build
            localBuildPath = self.__localPath + build
            try:
                self.__archiveFtpClient.stat(remoteBuildPath)
                alreadyThere.append(build)
                copied.append(build)
                continue
            except AttributeError:
                status = "failure"
                errors = "Connection error to archive storage.  Use settings menu to configure!"
                return status, errors, alreadyThere
            except IOError:
                pass # Directory's not there, try to add it

            try:
                tmpDir = self.getLocalResults(build)
                if tmpDir == None:
                    logger.warning("Can't fetch jenkins copy of " + build)
                    errors.append(build)
                    continue
                try:
                    self.__archiveFtpClient.mkdir(remoteBuildPath)
                    files = os.listdir(tmpDir)
                    for file in files:
                        self.__archiveFtpClient.put(tmpDir + "/" + file,
                                     remoteBuildPath + "/" + file)
                    copied.append(build)
                except IOError as e:
                    logger.warning("Can't push " + build + " : exception=" + str(e))
                    errors.append(build)
            except IOError:
                logger.warning("Can't fetch jenkins copy of " + build)
            shutil.rmtree(tmpDir, ignore_errors=True)

        # If copy to gsa was successful, then remove the 'local' copy
        for build in copied:
            localBuildPath = self.__localPath + build
            shutil.rmtree(localBuildPath, ignore_errors=True)

        # Remove partial copies to gsa.  Try again later
        for build in errors:
            remoteBuildPath = self.__copyPath + build
            try:
                self.__archiveFtpClient.stat(remoteBuildPath)
            except IOError as e:
                if 'No such file' in str(e):
                    continue
            try:
                files = self.__archiveFtpClient.listdir()
                for file in files:
                    self.__archiveFtpClient.unlink(remoteBuildPath + '/' + file)
                self.__archiveFtpClient.rmdir(remoteBuildPath)
            except IOError as e:
                logger.warning("Can't remove directory " + remoteBuildPath + " : " + str(e))

        return status, errors, alreadyThere

    # Removing projects reports from the local and GSA directories
    def removeProjectsData(self, projects, projectObj):
        for name in projects.keys():
            try:
                if projects[name] == "local":
                    localPath = self.__localPath
                    shutil.rmtree(localPath+name)
                else:
                    projectObj.removeDirFromGSA(self.__archiveSshClient, self.__copyPath+name)
            except IOError as e:
                logger.warning("Can't remove directory " + remoteBuildPath + " : " + str(e))

    def cleanTmp(self):
        for tmpdir in self.__tmpdirs:
            if os.path.exists(tmpdir):
                shutil.rmtree(tmpdir, ignore_errors=True)
        self.__tmpdirs = []

    def close(self):
        try:
            self.cleanTmp()
            self.__archiveFtpClient.close()
            self.__jenkinsFtpClient.close()
        except AttributeError:
            pass

    def __del__(self):
        self.close()
