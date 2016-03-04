import paramiko
import tempfile
import shutil
import os
import re
import shutil
import time
import errno
import globals
from stat import S_ISDIR
from log import logger

resultPattern = re.compile('(.*?)\.(.*?)\.(.*?)\.N-(.*?)\.(.*?)\.(\d\d\d\d-\d\d-\d\d-h\d\d-m\d\d-s\d\d)')

class Catalog:
    def __init__(self):
        globals.init()

    def connect(self, archiveHost,
            archivePort=globals.configPort,
            archiveUser=globals.configUsername,
            archivePassword=globals.configPassword,
            copyPath=globals.pathForTestResults,
            localPath=globals.localPathForTestResults):
        self.__archiveHost = archiveHost
        self.__archivePort = archivePort
        self.__archiveUser = archiveUser
        self.__archivePassword = archivePassword
        self.__copyPath = copyPath
        self.__localPath = localPath
        self.__tmpdirs = []

        logger.debug("In catalog.connect, connecting to archived storage at " + archiveHost)
        logger.debug("catalog.connect: username=%s, port=%d" % (self.__archiveUser, self.__archivePort))

        try:
            globals.sftpConnected = False
            self.__archiveSshClient = paramiko.SSHClient()
            self.__archiveSshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.__archiveSshClient.connect(self.__archiveHost, username=self.__archiveUser,\
                                            password=self.__archivePassword, port=self.__archivePort)
            self.__archiveFtpClient = self.__archiveSshClient.open_sftp()
            logger.debug("catalog.connect: Connected to archived storage")
            globals.sftpConnected = True
        # Error handling
        except paramiko.AuthenticationException as ae:
            logger.warning("Connection error to archive storage")
            logger.warning("Use settings menu to specify your user credentials!")
        except paramiko.SSHException as se:
            logger.warning("SSH connection error to archive storage")
            logger.warning("You may need to authenticate.  Check networking!")
        except IOError as e:
            logger.warning("Please ensure that the archive hostname is correct in the settings menu!")
            logger.warning(str(e))

    def listJobResults(self, repoType, filt):
        results = []

        jobs = []
        try:
            if repoType == "local" or repoType == "all":
                jobs = self.listLocalJobResults(filt)

            if repoType == "sftp" or repoType == "all":
                jobs = jobs + self.listSFTPJobResults(filt)
        except Exception as e:
            msg = str(e)
            logger.debug("listJobResults: " + msg)
            assert(False), msg

        for jobDesc in jobs:
            try:
                job = jobDesc[0]
                repo = jobDesc[1]

                # Validate that the directory looks like a test result
                try:
                    nodeLabel = resultPattern.match(job).group(3)
                    pkgName = resultPattern.match(job).group(4)
                    pkgVer = resultPattern.match(job).group(5)
                    date = time.asctime(time.strptime(resultPattern.match(job).group(6),"%Y-%m-%d-h%H-m%M-s%S"))
                except AttributeError:
                    continue

                # The node may not be known to this autoport instance.  Jobs
                # are aggregated in sftp.  Jenkin build nodes may be retired
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
            except IndexError as e:
                # Log and propagate the error with message to be displayed on UI.
                logger.warning('In listJobResults: %s' % str(e))
                raise IndexError, "Cannot display the list, please try again."
        logger.debug("Leaving listJobResults: results[0..3]=%s" % str(results[:3]))
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

    def listSFTPJobResults(self, filt):
        filteredList = []
        try:
            self.__archiveFtpClient.chdir(self.__copyPath)
            fullList = self.__archiveFtpClient.listdir()
            for item in fullList:
                if filt in item.lower() or filt == "":
                    filteredList.append([item, "sftp"])
        except IOError as e:
            # if the directory doesn't exist, return null
            if e.errno == errno.ENOENT:
                return filteredList
            msg = "listSFTPJobResults: " + str(e)
            logger.warning(msg)
            msg = "Connection error to archive storage.  Use settings menu to configure!"
            assert(False), msg
        except AttributeError as e:
            msg = "Connection error to archive storage.  Use settings menu to configure!"
            logger.warning(msg)
            assert(False), msg
        return filteredList

    def getResults(self, build, repository):
        if repository == "sftp":
            return self.getSFTPResults(build)
        elif repository == "local":
            return self.getLocalResults(build)

    def getLocalResults(self, build):
        try:
            logger.debug("In getLocalResult build=%s " % (build))
            localPath = self.__localPath + build + "/"
            tmpPath = tempfile.mkdtemp(prefix="autoport_")
            putdir = tmpPath + "/" + build
            if not os.path.exists(putdir):
                os.makedirs(putdir)
            logger.debug("Catalog getLocalResults: putdir=%s remoteDir=%s"
                         % (putdir, localPath))
            # Copy as many files as possible.  Reports use different files
            files = os.listdir(localPath)
            for file in files:
                try:
                    shutil.copyfile(localPath + file, putdir + "/" + file)
                except IOError:
                    pass
            self.__tmpdirs.append(tmpPath)
            return putdir
        except IOError as e:
            msg = "getLocalResults: " + str(e)
            logger.warning(msg)
            return None
        except Exception as e:
            msg = "getLocalResults: " + str(e)
            logger.debug(msg)
            return None

    def getSFTPResults(self, build):
        try:
            logger.debug("Catalog getSFTPResult: build=%s" % (build))
            tmpPath = tempfile.mkdtemp(prefix="autoport_")
            putdir = tmpPath + "/" + build
            if not os.path.exists(putdir):
                os.makedirs(putdir)
            logger.debug("Catalog getSFTPResult: putdir=%s remoteDir=%s" % (putdir, self.__copyPath + build))
            self.__archiveFtpClient.chdir(self.__copyPath + build)

            # Copy as many files as possible.  Reports use different files
            files = self.__archiveFtpClient.listdir()
            for file in files:
                try:
                    logger.debug("Catalog getSFTPResult: Downloading, sourceFile=%s Destination=%s" % (file, putdir + "/" + file))
                    self.__archiveFtpClient.get(file, putdir + "/" + file)
                except IOError:
                    pass
            self.__tmpdirs.append(tmpPath)
            return putdir
        except AttributeError:
            msg = "Connection error to archive storage.  Use settings menu to configure!"
            logger.warning(msg)
            assert(False), msg
        except IOError as e:
            msg = "getSFTPResults: IOError " + str(e)
            logger.warning(msg)
            return None
        except Exception as e:
            msg = "getSFTPResults: Exception " + str(e)
            logger.debug(msg)
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
                    logger.debug("Can't fetch local copy of " + build)
                    errors.append(build)
                    continue
                try:
                    paths = remoteBuildPath.split('/')
                    curPath = '/'
                    for path in paths:
                        if (path == ""):
                            continue
                        if (curPath == "/"):
                            curPath = '/%s'% (path)
                        else:
                            curPath = '%s/%s'% (curPath, path)
                        try:
                            self.__archiveFtpClient.stat(curPath)
                        except IOError as e:
                            if e.errno == errno.ENOENT:
                                self.__archiveFtpClient.mkdir(curPath)
                    files = os.listdir(tmpDir)
                    for file in files:
                        self.__archiveFtpClient.put(tmpDir + "/" + file,
                                     remoteBuildPath + "/" + file)
                    copied.append(build)
                except IOError as e:
                    logger.warning("Can't push " + build + " : exception=" + str(e))
                    errors.append(build)
            except IOError:
                logger.warning("Can't fetch local copy of " + build)
            shutil.rmtree(tmpDir, ignore_errors=True)

        # If copy to sftp was successful, then remove the 'local' copy
        for build in copied:
            localBuildPath = self.__localPath + build
            shutil.rmtree(localBuildPath, ignore_errors=True)

        # Remove partial copies to sftp.  Try again later
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
                logger.debug("Can't remove directory " + remoteBuildPath + " : " + str(e))

        return status, errors, alreadyThere

    # Removing projects reports from the local and SFTP directories
    def removeProjectsData(self, projects, projectObj):
        for name in projects.keys():
            try:
                if projects[name] == "local":
                    localPath = self.__localPath
                    shutil.rmtree(localPath+name)
                else:
                    projectObj.removeDirFromSFTP(self.__archiveSshClient, self.__copyPath+name)
            except IOError as e:
                logger.warning("Can't remove directory " + remoteBuildPath + " : " + str(e))

    def cleanTmp(self):
        total_dir_to_clean = len(self.__tmpdirs)
        file_position_cleared = []
        try:
            for i in range(total_dir_to_clean):
                if os.path.exists(self.__tmpdirs[i]):
                    # check if data expired
                    last_modified_time = os.path.getmtime(self.__tmpdirs[i])
                    current_time = time.time()

                    if (current_time - last_modified_time) > float(globals.expiryForTmp):
                        shutil.rmtree(self.__tmpdirs[i], ignore_errors=True)
                        file_position_cleared.append(i)

            # Flush removed folders from list.
            for i in file_position_cleared:
                logger.info("Clearing directory: " + self.__tmpdirs[0])
                del self.__tmpdirs[0]

        except ValueError as ex:
            logger.warning("CleanTmp: " + str(ex))
        except IndexError as indexError:
            logger.warning("CleanTmp: " + str(indexError))

    def newTmpDirectoryAdded(self, dirname = None):
        if dirname:
            self.__tmpdirs.append(dirname)

    def close(self):
        try:
            self.cleanTmp()
            self.__archiveFtpClient.close()
        except AttributeError:
            pass

    def __del__(self):
        self.close()
