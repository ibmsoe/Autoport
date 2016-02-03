import globals
import os
import re
import paramiko
import tempfile
import ntpath
import errno
from log import logger
from buildAnalyzer import inferBuildSteps
from stat import ST_SIZE, ST_MTIME
from time import localtime, asctime, strftime, strptime
from flask import json
from project import Project
import shutil
from stat import S_ISDIR

from catalog import Catalog

projectResultPattern = re.compile('(.*?)\.(.*?)\.(.*?)\.N-(.*?)\.(.*?)\.(\d\d\d\d-\d\d-\d\d-h\d\d-m\d\d-s\d\d)')

class Batch:
    def __init__(self, catalog):
        self.catalog = catalog

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
            logger.warning("batch connect Error=%s" % str(e))

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
        logger.debug("Leaving listBatchFiles: res[%d]" % len(res))
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
                    self.catalog.newTmpDirectoryAdded(putdir)
                    self.ftp_client.get(filename, putdir + "/" + filename)
                    filteredList.append(self.parseBatchFileList(putdir + "/" + filename, "gsa"))
        except IOError as e:
            # if the directory doesn't exist, return null
            if e.errno == errno.ENOENT:
                return filteredList
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

        logger.debug("Leaving listBatchReports: reportData[%d]" % len(reportData))
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
                            parsedResult = self.parseBatchReportList(
                                absoluteFilePath,
                                "local"
                            )
                            if parsedResult:
                                filteredList.append(parsedResult)
        except IOError:
            assert(False), "Please provide valid local batch files path in settings menu!"
        return filteredList

    def listGSABatchReports(self, filt):
        filteredList = []
        try:
            self.ftp_client.chdir(globals.pathForBatchTestResults)
            flist = self.ftp_client.listdir()
            for filename in sorted(flist):
                logger.debug("listGSABatchReports: file=%s" % filename)
                if not filt or filt in filename.lower():
                    try:
                        putdir = tempfile.mkdtemp(prefix="autoport_")
                        self.catalog.newTmpDirectoryAdded(putdir)
                        self.copyRemoteDirToLocal(globals.pathForBatchTestResults + "/" + filename, putdir)
                        for batchFilePath in os.listdir(putdir + "/" + filename):
                        #batchFilePath = os.listdir(putdir + "/" + filename)[0]
                            logger.debug("listGSABatchReports: batchFilePath=%s" % batchFilePath)
                            batchTestReportFile = open("%s/%s/%s" % (putdir, filename, batchFilePath), 'r')
                            dataFile = batchTestReportFile.readlines()
                            for projectsReport in dataFile:
                                logger.debug("listGSABatchReports: projectsReport=%s" % projectsReport)
                                try:
                                    self.copyRemoteDirToLocal(globals.pathForTestResults + projectsReport.split('/')[0], putdir)
                                except Exception as ex:
                                    # Project results may be missing
                                    logger.debug("listGSABatchReports: Error in copying project %s" % projectsReport.split('/')[0] + str(ex))
                            parsedResult = self.parseBatchReportList(
                                os.path.join(putdir,filename,batchFilePath),
                                "gsa",
                                putdir
                            )
                            if parsedResult:
                                filteredList.append(parsedResult)
                    except Exception as ex:
                        logger.warning("listGSABatchReports: Error=%s" % str(ex))
                    finally:
                        if isinstance(batchTestReportFile, file):
                            batchTestReportFile.close()
                        self.catalog.cleanTmp()
        except AttributeError:
            assert(False), "Connection error to archive storage.  Use settings menu to configure!"
        except IOError as e:
            # if the directory doesn't exist, return null
            if e.errno == errno.ENOENT:
                return filteredList
        except Exception as e:
            logger.warning("listGSABatchReports: Error=%s" % str(e))
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
            self.ftp_client.stat(globals.pathForBatchFiles)
        except AttributeError:
            return {"error": "Connection error to archive storage.  Use settings menu to configure!" }
        except IOError as e:
            if e.errno == errno.ENOENT:
                try:
                    self.ftp_client.mkdir(globals.pathForBatchFiles)
                except:
                    return {"error": "Could not mkdir %s on archive storage " % (globals.pathForBatchFiles)  }

        try:
            self.ftp_client.chdir(globals.pathForBatchFiles)
            self.ftp_client.put(filename, ntpath.basename(filename))
        except:
            return {"error": "Could not archive batch file " + filename }

    # Parses given batch file and returns data in JSON format.
    def parseBatchReportList(self, filename, location, tmpDir = None):
        logger.debug("In parseBatchReportList, filename=%s location=%s tmpDir=%s" % (filename, location, tmpDir))
        batchFile = None
        return_data = {
            "batch_name": "INVALID BATCH FILE",
            "build_server": "-",
            "repo": "-",
            "jobNames": "-",
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
            batchList = ntpath.basename(filename).split('.')
            batchSubmissionTimeObj = batchList[-1]
            batchName = ".".join(batchList[:-2])

            # knowing that date format will be "%Y-%m-%d-h%H-m%M-s%S"
            # Converting it to "%Y-%m-%d-%H-%M-%S"
            batchSubmissionTime = asctime(strptime(batchSubmissionTimeObj, "%Y-%m-%d-h%H-m%M-s%S"))

            batchFile = open(filename)
            jobNames = batchFile.readlines()
            buildAndTestLogs = self.getLocalBuildAndTestLogs(jobNames, location, tmpDir)
            project_count = len(jobNames)

            buildServer = None
            if len(jobNames):
                # All the jobs will be for same build server, hence only checking for the first entry
                buildServer = projectResultPattern.match(jobNames[0]).group(3)

            if not project_count and not buildServer:
                logger.debug("parseBatchReportList: skipping batchFile: \"%s\" as there is no build server or projects in the batch.", filename)
                return None

            return_data.update({
                "batch_name": batchName,
                "build_server": buildServer or '-',
                "project_count": project_count,
                "repo": location,
                "jobNames": jobNames,
                "date_submitted": batchSubmissionTime,
                "filename": filename,
                "build_log_count": buildAndTestLogs['build_logs'] or 'Not Available',
                "test_log_count": buildAndTestLogs['test_logs'] or 'Not Available'
            })
        except Exception as ex:
            logger.warning("parseBatchReportList Error=%s" % str(ex))
        finally:
            if isinstance(batchFile, file):
                batchFile.close()

        return return_data

    # Gets number of build logs and test logs for given batch,
    # by traversing through the individual projects associated with the batch job
    def getLocalBuildAndTestLogs(self, jobNames = [], repo = 'local', tmpDir = None):
        build_logs = 0
        test_logs = 0
        logger.debug("In getLocalBuildAndTestLogs, repo=%s" % (repo))
        if tmpDir:
            project_path = tmpDir + '/'
        elif repo == 'local':
            project_path = globals.localPathForTestResults
        else:
            project_path = globals.pathForTestResults
        for jobName in jobNames:
            logger.debug("getLocalBuildAndTestLogs , pathtotest=%s/%s/%s" % (project_path, jobName.strip(), 'test_result.arti'))
            if os.path.exists('%s%s/%s' % (project_path, jobName.strip(), 'test_result.arti')):
                test_logs += 1

            if os.path.exists('%s%s/%s' % (project_path, jobName.strip(), 'build_result.arti')):
                build_logs += 1

        logger.debug("Leaving getLocalBuildAndTestLogs, Count jobNames[%d] build_logs=%s test_logs=%s" %
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
            environment = fileBuf['config']['java']
        except KeyError:
            environment = "openjdk 7"

        try:
            env = fileBuf['config']['javascript']
            if not env:
                env = "nodejs"
            environment += ", " + env
        except KeyError:
            environment += ", nodejs"

        try:
            owner = fileBuf['config']['owner']
            if owner == "" or "<" in owner:
                owner = "Anonymous"
        except KeyError:
            owner = "Anonymous"

        self.catalog.cleanTmp()

        return {"location": location, "owner": owner, "name": name, "size": size, \
            "datemodified": datemodified, "environment": environment, "filename": filename}

    # Full verification of batch file including generation of build command if not specified
    def parseBatchFile(self, filename):
        logger.debug("In parseBatchFile, filename=%s" % filename)
        f = open(filename)
        try:
            fileBuf = json.load(f)
        except ValueError, ex:
            logger.warning("parseBatchFile: Error=%s" % str(ex))
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
            packages = fileBuf['packages']
        except KeyError:
            return {"error": "Missing 'packages' section in batch file" }

        try:
            owner = fileBuf['config']['owner']
            if owner == "":
                fileBuf['config']['owner'] = "Anonymous"
        except KeyError:
            fileBuf['config']['owner'] = "Anonymous"

        try:
            env = fileBuf['config']['java']
            if env == "":
                fileBuf['config']['java'] = "openjdk 7"
        except KeyError:
            fileBuf['config']['java'] = "openjdk 7"

        try:
            env = fileBuf['config']['javascript']
            if env == "":
                fileBuf['config']['javascript'] = "nodejs"
        except KeyError:
            fileBuf['config']['javascript'] = "nodejs"

        logger.debug("parseBatchFile: file['config']['java']=%s" % fileBuf['config']['java'])
        logger.debug("parseBatchFile: file['config']['javascript']=%s" % fileBuf['config']['javascript'])

        try:
            tst = fileBuf['config']['includeTestCmds']
            if tst == "":
                fileBuf['config']['includeTestCmds'] = "True"
        except KeyError:
            fileBuf['config']['includeTestCmds'] = "True"

        try:
            tst = fileBuf['config']['includeInstallCmds']
            if tst == "":
                fileBuf['config']['includeInstallCmds'] = "False"
        except KeyError:
            fileBuf['config']['includeInstallCmds'] = "False"

        logger.debug("parseBatchFile: file['config']['includeTestCmds']=%s" % fileBuf['config']['includeTestCmds'])
        logger.debug("parseBatchFile: file['config']['includeInstallCmds']=%s" % fileBuf['config']['includeInstallCmds'])

        for package in fileBuf['packages']:
            try:
                name = package['name']
            except KeyError:
                return { "error": "Missing project name" }

            try:
                idStr = package['id']
                repo = globals.cache.getRepo(int(idStr))
                if repo == None:
                    return { "error": "batch file invalid project " + name }
            except KeyError:
                return { "error": "Missing id field for project " + name }

            try:
                tag = package['tag']
            except KeyError:
                package['tag'] = "current"

            # Build information is calculated just in time to facilitate testing
            # of master branch as the source code and build instructions may
            # change daily.

            buildInfo = {}
            try:
                selectedBuild = package['build']['selectedBuild']
            except KeyError:
                buildInfo = inferBuildSteps(globals.cache.getDir(repo), repo)
                package['build'] = {}
                if buildInfo:
                    package['build']['artifacts'] = buildInfo['artifacts']
                    package['build']['selectedBuild'] = buildInfo['selectedBuild']
                    package['build']['selectedEnv'] = buildInfo['selectedEnv']
                    package['build']['selectedTest'] = buildInfo['selectedTest']
                    package['build']['selectedInstall'] = buildInfo['selectedInstall']
                    package['build']['primaryLang'] = buildInfo['primaryLang']

            # Trust data provided by inferBuildSteps
            if not buildInfo:
                package['build']['userDefined'] = "True"

                try:
                    selectedBuild = package['build']['selectedBuild']
                except KeyError:
                    package['build']['selectedBuild'] = ""

                try:
                    selectedTest = package['build']['selectedTest']
                except KeyError:
                    package['build']['selectedTest'] = ""

                try:
                    selectedInstall = package['build']['selectedInstall']
                except KeyError:
                    package['build']['selectedInstall'] = ""

                try:
                    selectedEnv = package['build']['selectedEnv']
                except KeyError:
                    package['build']['selectedEnv'] = ""

                try:
                    artifacts = package['build']['artifacts']
                except KeyError:
                    package['build']['artifacts'] = ""

                try:
                    primaryLang = package['build']['primaryLang']
                except KeyError:
                    # Lang is not set if project is a book, tar file, etc.
                    if repo.language:
                        package['build']['primaryLang'] = repo.language
                    else:
                        package['build']['primaryLang'] = ""

            # Not provided by inferBuildSteps and not included in batch file

            try:
                package['build']['owner_url'] = repo.owner.html_url
            except Exception as e:
                package['build']['owner_url'] = ""

        return { "status": "ok", "fileBuf": fileBuf }

    # Closing the SSHClient
    def disconnect(self):
        try:
            self.ftp_client.close()
        except Exception as e:
            logger.warning("In batch:disconnect, Error=%s" %  str(e))

    # @TODO Below code for getting Batch Test Details and other functionality is in progress.
    def getBatchTestDetails(self, batchList, catalog, type):
        # clear old records and continue with fresh data.
        catalog.cleanTmp()
        out = []
        repos = {}
        # Get the project Names and fetch test details from them.
        if batchList.get('local'):
            repos["local"] = self.getLocalProjectForGivenBatch(batchList.get('local', []), 'local')
        if batchList.get('gsa'):
            repos["gsa"] = self.getLocalProjectForGivenBatch(batchList.get('gsa', []), 'gsa')

        repoData = repos[repos.keys()[0]]
        batchNamesData = repoData.keys()
        if type == "compare":
            leftProjectslist = []
            rightProjectslist = []
            if len(repos.keys()) == 2:
                i = repos[repos.keys()[0]].values()[0]
                j = repos[repos.keys()[1]].values()[0]
            elif len(repos.keys()) == 1:
                if len( repos[repos.keys()[0]].keys()) == 2:
                    i = repos[repos.keys()[0]].values()[0]
                    j = repos[repos.keys()[0]].values()[1]
            leftProjectslist =  map(lambda x:projectResultPattern.match(x).group(4) , i)
            rightProjectslist =  map(lambda x:projectResultPattern.match(x).group(4) ,j)
            if len( set(leftProjectslist).intersection(rightProjectslist)) == 0:
                return "No common projects available"

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
            logger.warning("getLocalProjectForGivenBatch: Error=%s" % str(ex))

        return projects

    # Remove Batch Reports Data from local or GSA
    def removeBatchReportsData(self, reports, catalog):
        logger.debug("In removeBatchReportsData, reports[%d]" % len(reports))
        project = Project(catalog)
        for name in reports.keys():
            try:
                if reports[name] == "local":
                    logger.debug("removeBatchReportsData: local filepath=%s" % name)
                    os.remove(name)
                    if len(os.listdir(os.path.dirname(name))) == 0:
                        shutil.rmtree(os.path.dirname(name), ignore_errors=True)
                else:
                    filepath = globals.pathForBatchTestResults + \
                               os.path.basename(os.path.dirname(name)) + "/" + os.path.basename(name)
                    logger.debug("removeBatchReportsData: archive filepath=%s" % (filepath))
                    projects = {}
                    batchTestReportFile = self.ftp_client.open(filepath,'r')
                    dataFile = batchTestReportFile.readlines()
                    for line in dataFile:
                        if line:
                            projects[line.strip()] = 'gsa'
                    # Projects report removal from GSA
                    catalog.removeProjectsData(projects, project)

                    self.ftp_client.remove(filepath)
                    if len(self.ftp_client.listdir(os.path.dirname(filepath))) == 0:
                        # Batch report removal from GSA
                        self.ftp_client.rmdir(os.path.dirname(filepath))
            except IOError as e:
                logger.debug("removeBatchReportsData: I/O Error=%s" % str(e))
            except Exception as e:
                logger.debug("removeBatchReportsData: Error=%s" % str(e))
        logger.debug("Leaving removeBatchReportsData")

    # Archive Batch Reports Data to GSA
    def archiveBatchReports(self, report):
        batchReportDir = globals.pathForBatchTestResults + os.path.basename(os.path.dirname(report))
        batchReportName = os.path.basename(report)
        logger.debug("In archiveBatchReports, report=%s batchReportDir=%s batchreportName=%s"
                     % (str(report), batchReportDir, batchReportName))
        try:
            self.ftp_client.stat(batchReportDir)
            self.ftp_client.put(report, batchReportDir + '/' + batchReportName)
            os.remove(report)
            if len(os.listdir(os.path.dirname(report))) == 0:
                shutil.rmtree(os.path.dirname(report), ignore_errors=True)
            return "Success"
        except AttributeError:
            msg = "Connection error to archive storage.  Use settings menu to configure!"
            assert(False), msg
        except IOError as e:
            pass # Directory's not there, try to add it

        try:
            self.ftp_client.mkdir(batchReportDir)
            self.ftp_client.put(report, batchReportDir + '/' + batchReportName)
            # Cleaning-up local batch_test_report after archival
            os.remove(report)
            if len(os.listdir(os.path.dirname(report))) == 0:
                shutil.rmtree(os.path.dirname(report), ignore_errors=True)
            return "Success"
        except IOError as e:
            logger.warning("archiveBatchReports: Can't push " + batchReportName + ": Error=" + str(e))
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

        batchNames = []
        batchNames.extend(left_projects.keys())
        batchNames.extend(right_projects.keys())

        for proj1 in left_projects[batchNames[0]]:
            isMatchAvailable = False
            proj1Name = projectResultPattern.match(proj1).group(4)
            for proj2 in right_projects[batchNames[1]]:
                proj2Name = projectResultPattern.match(proj2).group(4)
                if proj1Name == proj2Name:
                    isMatchAvailable = True
                if right_projects[batchNames[1]].index(proj2) == len(right_projects[batchNames[1]])-1 and not isMatchAvailable:
                    right_projects[batchNames[1]].remove(proj2)
            if not isMatchAvailable:
                left_projects[batchNames[0]].remove(proj1)

        if len(left_projects[batchNames[0]]) == 0 or len(right_projects[batchNames[1]]) == 0:
            return "No common projects available"

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
                logger.debug("getBatchDiffLogResults: leftArch=%s parent_name=%s project=%s" % (leftArch, batchName, project))

        for batchName in right_projects:
            newBatchName = final_response.keys()[0]
            if not final_response.has_key(newBatchName):
                final_response[newBatchName] = {}
            for project in right_projects[batchName]:
                projectName = projectResultPattern.match(project).group(4)
                if projectName not in final_response[newBatchName].keys():
                    continue
                if not rightArch:
                    rightArch = projectResultPattern.match(project).group(3)
                if not final_response[newBatchName].has_key(projectName):
                    final_response[newBatchName][projectName] = {}
                final_response[newBatchName][projectName]["right"] = project
                final_response[newBatchName][projectName]["right_parent_name"] = batchName
                final_response[newBatchName][projectName]["right_version"] = projectResultPattern.match(project).group(5)
                logger.debug("getBatchDiffLogResults: rightArch=%s parent_name=%s project=%s" % (rightArch, batchName, project))

        # We have paired jobs now call project_obj.getDiffLogResult recursively and get data.
        logger.debug("getBatchDiffLogResults: here leftRepo=%s rightRepo=%s" % (leftRepo, rightRepo))
        for batchName in final_response:
            for project in final_response[batchName]:
                if final_response[batchName][project].has_key("left") and final_response[batchName][project].has_key("right"):
                    diffData = project_obj.getDiffLogResult(
                        logfile,
                        final_response[batchName][project]["left"],
                        final_response[batchName][project]["right"],
                        leftRepo,
                        rightRepo
                    )
                    if diffData.has_key('error'):
                        logger.debug("getBatchDiffLogResults: skipping project error=%s" % diffData['error'])
                    else:
                        final_response[batchName][project]["diff"] = diffData

        final_response["left_arch"] = leftArch
        final_response["right_arch"] = rightArch
        return final_response

    # Updates local batch file or archived.
    # If batch file exists in local / archive already this will overwrite it.
    def updateBatchFile(self, filePath, fileContent, location):
        logger.debug("In updateBatchFile, filename = %s" % str(filePath))
        batch_detail_file = None
        if location=="local":
            try:
                batch_detail_file = open(filePath, 'w')
                batch_detail_file.write(fileContent)
            except Exception as e:
                logger.debug("updateBatchFile: Error=%s" % str(e))
                assert(False), str(e)
            finally:
                if isinstance(batch_detail_file, file):
                    batch_detail_file.close();
        elif location=="gsa":
            try:
                gsafilePath = globals.pathForBatchFiles + ntpath.basename(filePath)
                f = self.ftp_client.open(gsafilePath, 'w')
                f.write(fileContent)
            except Exception as e:
                logger.debug("updateBatchFile: Error=%s" % str(e))
                assert(False), str(e)
            finally:
                if isinstance(f, file):
                    f.close();
            # if update is successful then update the local copy in /tmp folder
            try:
                batch_detail_file = open(filePath, 'w')
                batch_detail_file.write(fileContent)
            except Exception as e:
                logger.debug("updateBatchFile: Error=%s" % str(e))
                assert(False), str(e)
            finally:
                if isinstance(batch_detail_file, file):
                    batch_detail_file.close();

    def close(self):
        try:
            self.ssh_client.close()
        except Exception as e:
            logger.warning("In batch:close, Error=%s" % str(e))

    def __del__(self):
        self.close()
