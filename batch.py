import globals
import os
import re
import paramiko
import tempfile
import ntpath
from log import logger
from buildAnalyzer import inferBuildSteps
from stat import ST_SIZE, ST_MTIME
from time import localtime, asctime
from flask import json
from project import Project
import shutil
from stat import S_ISDIR

projectResultPattern = re.compile('(.*?)\.(.*?)\.(.*?)\.N-(.*?)\.(.*?)\.(\d\d\d\d-\d\d-\d\d-h\d\d-m\d\d-s\d\d)')

class Batch:
    # Connecting to SSHClient using GSA credentials
    def connect(self, archiveHost=globals.hostname,
                archivePort=globals.port,
                archiveUser=globals.configUsername,
                archivePassword=globals.configPassword):
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(archiveHost, username=archiveUser, \
                password=archivePassword, port=archivePort)
            self.ftp_client = self.ssh_client.open_sftp()
        except paramiko.AuthenticationException:
            pass                  # error message already displayed in catalog.py
        except paramiko.SSHException:
            pass                  # error message already displayed in catalog.py
        except IOError as e:
            logger.warning("batch connect exception=" + str(e))

    def listBatchFiles(self, repoType, filt):
        logger.debug("In listBatchFiles: repoType=%s filt=%s" % (repoType, filt))
        res = []
        try:
            if repoType == "local" or repoType == "all":
                res = self.listLocalBatchFiles(filt)

            if repoType == "gsa" or repoType == "all":
                res = res + self.listGSABatchFiles(filt)
        except Exception as e:
            assert(False), str(e)
        logger.debug("Leaving listBatchFiles: res=" + str(res))
        return res

    def listLocalBatchFiles(self, filt):
        filteredList = []
        try:
            for dirname, dirnames, filenames in os.walk(globals.localPathForBatchFiles):
                for filename in sorted(filenames):
                    if not filt or filt in filename.lower():
                        if filename != ".gitignore":
                            filteredList.append(self.parseBatchFileList(globals.localPathForBatchFiles \
                                               + filename, "local"))
        except IOError:
            assert(False), "Please provide valid local batch files path in settings menu!"
        return filteredList

    def listGSABatchFiles(self, filt):
        filteredList = []
        try:
            self.ftp_client.chdir(globals.pathForBatchFiles)
            flist = self.ftp_client.listdir()
            for filename in sorted(flist):
                if not filt or filt in filename.lower():
                    putdir = tempfile.mkdtemp(prefix="autoport_")
                    self.ftp_client.get(filename, putdir + "/" + filename)
                    filteredList.append(self.parseBatchFileList(putdir + "/" + filename, "gsa"))
        except IOError as e:
            assert(False), str(e)
        except AttributeError:
            assert(False), "Connection error to archive storage.  Use settings menu to configure!"
        return filteredList

    ########### Listing of Batch Results starts #######

    def listBatchReports(self, repoType, filt):
        logger.debug("In listBatchReports: repoType=%s filt=%s" % (repoType, filt))
        reportData = []
        try:
            if repoType == "local" or repoType == "all":
                reportData = self.listLocalBatchReports(filt)

            if repoType == "gsa" or repoType == "all":
                reportData.extend(self.listGSABatchReports(filt))
        except Exception as e:
            assert(False), str(e)

        logger.debug("Leaving listBatchReports: reportData=" + str(reportData))
        return reportData

    def listLocalBatchReports(self, filt):
        filteredList = []
        try:
            for dirname, dirnames, filenames in os.walk(globals.localPathForBatchTestResults):
                logger.debug("dirname=%s dirnames=%s filenames=%s" % (dirname, dirnames, filenames))
                for filename in sorted(filenames):
                    absoluteFilePath = "%s/%s" % (dirname, filename)
                    logger.debug("absoluteFilePath=" + absoluteFilePath)
                    if not filt or filt in filename.lower():
                        if filename != ".gitignore":
                            filteredList.append(self.parseBatchReportList(
                                absoluteFilePath,
                                "local"
                            ))
        except IOError:
            assert(False), "Please provide valid local batch files path in settings menu!"
        return filteredList

    def listGSABatchReports(self, filt):
        filteredList = []
        try:
            self.ftp_client.chdir(globals.pathForBatchTestResults)
            flist = self.ftp_client.listdir()
            for filename in sorted(flist):
                if not filt or filt in filename.lower():
                    try:
                        putdir = tempfile.mkdtemp(prefix="autoport_")
                        self.copyRemoteDirToLocal(globals.pathForBatchTestResults + "/" +filename, putdir)
                        batchFilePath = os.listdir(putdir + "/" + filename)[0]
                        batchTestReportFile = self.ftp_client.open(globals.pathForBatchTestResults + filename + "/" + batchFilePath,'r')
                        dataFile = batchTestReportFile.readlines()
                        for projectsReport in dataFile:
                            self.copyRemoteDirToLocal(globals.pathForTestResults + projectsReport.strip(), putdir)
                        batchTestReportFile.close()
                        filteredList.append(
                            self.parseBatchReportList(
                                os.path.join(putdir,filename,batchFilePath),
                                "gsa",
                                putdir
                            )
                        )
                    except Exception as ex:
                        logger.warning("listGSABatchReports Error: " + str(ex))
        except AttributeError:
            assert(False), "Connection error to archive storage.  Use settings menu to configure!"
        except Exception as e:
            logger.warning("In listGSABatchReports Error: "+ str(e))
            assert(False), str(e)
        return filteredList

    ########### Listing of Batch Results ends #######

    def removeBatchFile(self, filename, location):
        if location == "gsa":
            res = self.removeArchivedBatchFile(filename)
        elif location == "local":
            res = self.removeLocalBatchFile(filename)
        return res

    def removeArchivedBatchFile(self, filename):
        try:
            self.ftp_client.chdir(globals.pathForBatchFiles)
            self.ftp_client.remove(ntpath.basename(filename))
        except:
            return {"error": "Could not remove archived batch file " + filename }

    def removeLocalBatchFile(self, filename):
        try:
            os.remove(filename)
        except:
            return {"error": "Could not remove batch local file " + filename }

    # Uploads local batch file to archive. If batch file exists in the archive already
    # this will overwrite it.
    # TODO - Give the user a popup to confirm overwrite
    def archiveBatchFile(self, filename):
        try:
            self.ftp_client.chdir(globals.pathForBatchFiles)
            self.ftp_client.put(filename, ntpath.basename(filename))
        except AttributeError:
            return {"error": "Connection error to archive storage.  Use settings menu to configure!" }
        except:
            return {"error": "Could not archive batch file " + filename }

    # Parses given batch file and returns data in JSON format.
    def parseBatchReportList(self, filename, location, tmpDir = None):
        logger.debug("In parseBatchReportList, filename=%s location=%s" % (filename, location))
        batchFile = None
        return_data = {
            "batch_name": "INVALID BATCH FILE",
            "build_server": "-",
            "repo": "-",
            "date_submitted": "-",
            "filename": "-",
            "build_log_count": 'Not Available',
            "test_log_count": 'Not Available'
        }
        try:
            batchStats = os.stat(filename)
            batchCreationTime = asctime(localtime(batchStats[ST_MTIME]))
        except OSError:
            batchCreationTime = "-"
        try:
            batchFile = open(filename)
            batchName, batchUID, batchSubmissionTime = ntpath.basename(filename).split('.')
            jobNames = batchFile.readlines()
            buildAndTestLogs = self.getLocalBuildAndTestLogs(jobNames, location, tmpDir)
            project_count = len(jobNames)
            buildServer = None
            if len(jobNames):
                # All the jobs will be for same build server, hence only checking for the first entry
                buildServer = projectResultPattern.match(jobNames[0]).group(3)

            return_data.update({
                "batch_name": batchName,
                "build_server": buildServer or '-',
                "project_count": project_count,
                "repo": location,
                "date_submitted": batchSubmissionTime,
                "filename": filename,
                "build_log_count": buildAndTestLogs['build_logs'] or 'Not Available',
                "test_log_count": buildAndTestLogs['test_logs'] or 'Not Available'
            })
        except Exception as ex:
            logger.warning("parseBatchReportList Error: " + str(ex))
        finally:
            if isinstance(batchFile, file):
                batchFile.close()
        return return_data

    # Gets number of build logs and test logs for given batch,
    # by traversing through the individual projects associated with the batch job
    def getLocalBuildAndTestLogs(self, jobNames = [], repo = 'local', tmpDir = None):
        build_logs = 0
        test_logs = 0
        if tmpDir:
            project_path = tmpDir + '/'
        elif repo == 'local':
            project_path = globals.localPathForTestResults
        else:
            project_path = globals.pathForTestResults
        for jobName in jobNames:
            if os.path.exists('%s%s/%s' % (project_path, jobName.strip(), 'test_result.arti')):
                test_logs += 1

            if os.path.exists('%s%s/%s' % (project_path, jobName.strip(), 'build_result.arti')):
                build_logs += 1

        logger.debug("Leaving getLocalBuildAndTestLogs, Count jobNames[]=%s build_logs=%s test_logs=%s" %
                     (len(jobNames), build_logs, test_logs))
        return {'build_logs': build_logs, 'test_logs': test_logs}

    # Fast look up for listing of all Batch Files.  Upon user selection of batch build and test,
    # the full contents of file are checked.  See parseBatchFile below
    def parseBatchFileList(self, filename, location):
        st = os.stat(filename)
        f = open(filename)

        size = st[ST_SIZE]
        size = str(size) + " Bytes"
        datemodified = asctime(localtime(st[ST_MTIME]))

        try:
            fileBuf = json.load(f)
        except ValueError:
            f.close()
            return {"location": "-", "owner": "-", "name": "INVALID BATCH FILE", "size": "-", \
                "datemodified": "-", "environment": "-", "filename": "-"}
        f.close()

        try:
            name = fileBuf['config']['name']
        except KeyError:
            name = "{ MISSING NAME }"

        try:
            env = fileBuf['config']['java']
            if env == "ibm":
                environment = "IBM Java"
            else:
                environment = "OpenJDK"
        except KeyError:
            environment = "OpenJDK"

        try:
            owner = fileBuf['config']['owner']
            if owner == "":
                owner = "Anonymous"
        except KeyError:
            owner = "Anonymous"

        return {"location": location, "owner": owner, "name": name, "size": size, \
            "datemodified": datemodified, "environment": environment, "filename": filename}

    # Full verification of batch file including generation of build command if not specified
    def parseBatchFile(self, filename):
        f = open(filename)
        try:
            fileBuf = json.load(f)
        except ValueError, ex:
            logger.warning("parseBatchFile error: " + str(ex))
            f.close()
            return {"error": "Could not read file" + filename }
        f.close()

        try:
            config = fileBuf['config']
        except KeyError:
            return {"error": "Missing 'config' section in batch file" }

        try:
            name = fileBuf['config']['name']
        except KeyError:
            return {"error": "Missing 'name' field in config section in batch file" }

        try:
            owner = fileBuf['config']['owner']
            if owner == "":
                fileBuf['config']['owner'] = "Anonymous"
        except KeyError:
            fileBuf['config']['owner'] = "Anonymous"

        try:
            env = fileBuf['config']['java']
            if env == "":
                fileBuf['config']['java'] = "OpenJDK"
        except KeyError:
            fileBuf['config']['java'] = "OpenJDK"

        try:
            package = fileBuf['packages']
        except KeyError:
            return {"error": "Missing packages section in batch file" }

        for package in fileBuf['packages']:
            try:
                name = package['name']
            except KeyError:
                return { "error": "Missing project name" }

            try:
                idStr = package['id']
            except KeyError:
                return { "error": "Missing id field for project " + name }

            try:
                tag = package['tag']
            except KeyError:
                package['tag'] = "Current"

            # Build information is lazily calculated for searches that yield multiple
            # projects to ensure fast searches.
            try:
                selectedBuild = package['build']['selectedBuild']
            except KeyError:
                repo = globals.cache.getRepo(int(idStr))
                if repo == None:
                    return { "error": "batch file invalid project " + name }
                package['build'] = inferBuildSteps(globals.cache.getDir(repo), repo)

            try:
                selectedTest = package['build']['selectedTest']
            except KeyError:
                package['build']['selectedTest'] = ""

            try:
                selectedEnv = package['build']['selectedEnv']
            except KeyError:
                package['build']['selectedEnv'] = ""

            try:
                artifacts = package['build']['artifacts']
            except KeyError:
                package['build']['artifacts'] = ""

        return { "status":"ok", "fileBuf":fileBuf }

    # Closing the SSHClient
    def disconnect(self):
        try:
            self.ftp_client.close()
        except Exception as e:
            logger.warning("disconnect error: " +  str(e))

    # @TODO Below code for getting Batch Test Details and other functionality is in progress.
    def getBatchTestDetails(self, batchList, catalog):
        # clear old records and continue with fresh data.
        catalog.cleanTmp()
        out = []
        repos = {}
        # Get the project Names and fetch test details from them.
        if batchList.get('local'):
            repos["local"] = self.getLocalProjectForGivenBatch(batchList.get('local', []), 'local')
        if batchList.get('gsa'):
            repos["gsa"] = self.getLocalProjectForGivenBatch(batchList.get('gsa', []), 'gsa')

        project = Project(catalog)
        final_response = {"status": "ok"}
        for repo in repos:
            projects = repos[repo]
            for batchName in projects:
                results = project.getTestDetails(projects[batchName], repo)
                final_response[batchName] = results.get("results")
        return final_response

    # Fetch all the info related to local projects for given batch job.
    def getLocalProjectForGivenBatch(self, batchList, repo):
        # Strip batch name from given batch file path in the list batchList
        batchNames = [str(ntpath.basename(i)) for i in batchList]
        pathsToWalk = []
        projects = {}
        for batchName in batchNames:
            projects[batchName] = [];
        # Walk through directories and search for the batch related projects to fetch info.
        if repo == 'local':
            pathsToWalk = [globals.localPathForBatchTestResults]
        else:
            pathsToWalk = [os.path.dirname(batchFile) for batchFile in batchList]

        pathsToWalk = set(pathsToWalk)

        try:
            for path in pathsToWalk:
                for dirname, dirnames, filenames in os.walk(path):
                    for filename in sorted(filenames):
                        actualFilePath = "%s/%s" % (dirname, filename)
                        if filename != ".gitignore" and filename in batchNames:
                            batchFile = open(actualFilePath)
                            if not projects.has_key(filename):
                                projects[filename] = []
                            projects[filename].extend([i.strip() for i in batchFile.readlines()])
                            batchFile.close()
        except Exception as ex:
            logger.warning("getLocalProjectForGivenBatch error: " +  str(ex))

        return projects

    # Remove Batch Reports Data from local or GSA
    def removeBatchReportsData(self, reports, catalog):
        project = Project(catalog)
        for name in reports.keys():
            try:
                if reports[name] == "local":
                    shutil.rmtree(os.path.dirname(name))
                else:
                    filepath = globals.pathForBatchTestResults + \
                               os.path.basename(os.path.dirname(name)) + "/" + os.path.basename(name)
                    logger.debug("In removeBatchReportsData, filepath=%s" % (filepath))
                    projects = {}
                    batchTestReportFile = self.ftp_client.open(filepath,'r')
                    dataFile = batchTestReportFile.readlines()
                    for line in dataFile:
                        if line:
                            projects[line.strip()] = 'gsa'
                    # Projects report removal from GSA
                    catalog.removeProjectsData(projects, project)

                    # Batch report removal from GSA
                    project.removeDirFromGSA(self.ssh_client, os.path.dirname(filepath))
            except IOError as e:
                logger.warning("Can't remove directory" + name + ": " + str(e))

    # Archive Batch Reports Data to GSA
    def archiveBatchReports(self, report):
        batchReportDir = globals.pathForBatchTestResults + os.path.basename(os.path.dirname(report)) 
        batchReportName = os.path.basename(report) 
        logger.debug("In archiveBatchReports, report=%s batchReportDir=%s batchreportName=%s"
                     % (str(report), batchReportDir, batchReportName))
        try:
            self.ftp_client.stat(batchReportDir)
            return "Already Exists"
        except AttributeError:
            msg = "Connection error to archive storage.  Use settings menu to configure!"
            assert(False), msg
        except IOError as e:
            pass # Directory's not there, try to add it

        try:
            self.ftp_client.mkdir(batchReportDir)
            self.ftp_client.put(report,batchReportDir + '/' + batchReportName)
            # Cleaning-up local batch_test_report after archival
            shutil.rmtree(os.path.dirname(report))
            return "Success"
        except IOError as e:
            logger.warning("Can't push " + batchReportName + ": exception=" + str(e))
            return "Failed - " + str(e)

    # Recursively download a full directory, since paramiko won't walk
    def copyRemoteDirToLocal(self, remotepath, localpath):
        logger.debug("In copyRemoteDirToLocal: remotepath=%s localpath=%s" % (remotepath, localpath))
        self.ftp_client.chdir(os.path.split(remotepath)[0])
        parent=os.path.split(remotepath)[1]
        for walker in self.remotePathWalker(parent):
            try:
                os.mkdir(os.path.join(localpath,walker[0]))
            except:
                pass
            for file in walker[2]:
                self.ftp_client.get(os.path.join(walker[0],file),os.path.join(localpath,walker[0],file))

    def remotePathWalker(self, remotepath):
        path=remotepath
        files=[]
        folders=[]
        for f in self.ftp_client.listdir_attr(remotepath):
            if S_ISDIR(f.st_mode):
                folders.append(f.filename)
            else:
                files.append(f.filename)
        yield path,folders,files
        logger.debug("In remotePathWalker: path=%s folders=%s files=%s" % (path,folders,files))
        for folder in folders:
            new_path=os.path.join(remotepath,folder)
            for x in self.remotePathWalker(new_path):
                yield x
                logger.debug("Second yield - %s" % str(x))

    def getBatchDiffLogResults(self, leftBatch, rightBatch, leftRepo, rightRepo, catalog, logfile = 'test_result.arti'):
        """
        This function will read given logfile and generate a comparison diff data.
        Args:
            leftBatch(str):         First Batch Name for comparison
            rightBatch(str):        Second Batch Name for comparison
            leftRepo(str):          First Batch Repo Name for comparison
            rightRepo(str):         Second Batch Repo Name for comparison
            catalog(Catalog):       Catalog object
            logfile(str)(Optional): which log file to use test_result.arti or build_result.arti

        Returns:
            Dictionary with comparison details for given batch jobs
        """
        final_response = {}
        final_data = {}
        project_obj = Project(catalog)
        leftArch = None
        rightArch = None

        # call project getDiffLogResult recursively for each project in batch and append output
        # get list of projects in a batch
        left_projects = self.getLocalProjectForGivenBatch([leftBatch], leftRepo)
        right_projects = self.getLocalProjectForGivenBatch([rightBatch], rightRepo)

        # Assuming both left and right project names will be same set of project names, only job names will differ.
        for batchName in left_projects:
            newBatchName = batchName.split('.')[0]
            if not final_response.has_key(newBatchName):
                final_response[newBatchName] = {}
            for project in left_projects[batchName]:
                projectName = projectResultPattern.match(project).group(4)
                if not leftArch:
                    leftArch = projectResultPattern.match(project).group(3)
                if not final_response[newBatchName].has_key(projectName):
                    final_response[newBatchName][projectName] = {}
                final_response[newBatchName][projectName]["left"] = project
                final_response[newBatchName][projectName]["left_parent_name"] = batchName
                final_response[newBatchName][projectName]["left_version"] = projectResultPattern.match(project).group(5)

        for batchName in right_projects:
            newBatchName = batchName.split('.')[0]
            if not final_response.has_key(newBatchName):
                final_response[newBatchName] = {}
            for project in right_projects[batchName]:
                projectName = projectResultPattern.match(project).group(4)
                if not rightArch:
                    rightArch = projectResultPattern.match(project).group(3)
                if not final_response[newBatchName].has_key(projectName):
                    final_response[newBatchName][projectName] = {}
                final_response[newBatchName][projectName]["right"] = project
                final_response[newBatchName][projectName]["right_parent_name"] = batchName
                final_response[newBatchName][projectName]["right_version"] = projectResultPattern.match(project).group(5)

        # We have paired jobs now call project_obj.getDiffLogResult recursively and get data.
        for batchName in final_response:
            for project in final_response[batchName]:
                if final_response[batchName][project].has_key("left") and final_response[batchName][project].has_key("right"):
                    final_response[batchName][project]["diff"] = project_obj.getDiffLogResult(                
                        logfile,
                        final_response[batchName][project]["left"],
                        final_response[batchName][project]["right"],
                        leftRepo,
                        rightRepo
                    )

        final_response["left_arch"] = leftArch
        final_response["right_arch"] = rightArch
        return final_response
