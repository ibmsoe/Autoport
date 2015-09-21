import globals
import os
import re
import paramiko
import tempfile
import ntpath
from buildAnalyzer import inferBuildSteps
from stat import ST_SIZE, ST_MTIME
from time import localtime, asctime
from flask import json
from project import Project

projectResultPattern = re.compile('(.*?)\.(.*?)\.(.*?)\.(.*?)\.N-(.*?)\.(.*?)\.(\d\d\d\d-\d\d-\d\d-h\d\d-m\d\d-s\d\d)')

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
            print str(e)

    def listBatchFiles(self, repoType, filt):
        res = []
        try:
            if repoType == "local" or repoType == "all":
                res = self.listLocalBatchFiles(filt)

            if repoType == "gsa" or repoType == "all":
                res = res + self.listGSABatchFiles(filt)
        except Exception as e:
            assert(False), str(e)

        return res

    def listLocalBatchFiles(self, filt):
        filteredList = []
        try:
            for dirname, dirnames, filenames in os.walk(globals.localPathForBatchFiles):
                for filename in sorted(filenames):
                    if filt in filename.lower() or filt == "":
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
                if filt in filename.lower() or filt == "":
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
        reportData = []
        try:
            if repoType == "local" or repoType == "all":
                reportData = self.listLocalBatchReports(filt)

            if repoType == "gsa" or repoType == "all":
                reportData = reportData.extend(self.listGSABatchReports(filt))
        except Exception as e:
            assert(False), str(e)

        return reportData

    def listLocalBatchReports(self, filt):
        filteredList = []
        try:
            for dirname, dirnames, filenames in os.walk(globals.localPathForBatchTestResults):
                for filename in sorted(filenames):
                    absoluteFilePath = "%s/%s" % (dirname, filename)
                    if filt in filename.lower() or filt == "":
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
                if filt in filename.lower() or filt == "":
                    try:
                        putdir = tempfile.mkdtemp(prefix="autoport_")
                        self.ftp_client.get(filename, putdir + "/" + filename)
                        filteredList.append(self.parseBatchReportList(putdir + "/" + filename, "gsa"))
                    except Exception, ex:
                        print "Error: ", str(ex)
        except Exception as e:
            print "Error: ", str(e)
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
        except AttributeError as e:
            return {"error": "Connection error to archive storage.  Use settings menu to configure!" }
        except:
            return {"error": "Could not archive batch file " + filename }

    # Parses given batch file and returns data in JSON format.
    def parseBatchReportList(self, filename, location):
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
            buildAndTestLogs = self.getLocalBuildAndTestLogs(jobNames)
            project_count = len(jobNames)
            if len(jobNames):
                # All the jobs will be for same build server, hence only checking for the first entry
                buildServer = projectResultPattern.match(jobNames[0]).group(4)

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
        except Exception, ex:
            print "Error: ", str(ex)
        finally:
            if isinstance(batchFile, file):
                batchFile.close()
        return return_data

    # Gets number of build logs and test logs for given batch,
    # by traversing through the individual projects associated with the batch job
    def getLocalBuildAndTestLogs(self, jobNames = [], repo = 'local'):
        build_logs = 0
        test_logs = 0
        if repo == 'local':
            project_path = globals.localPathForTestResults
        else:
            project_path = globals.pathForTestResults
        for jobName in jobNames:
            if os.path.exists('%s%s/%s' % (project_path, jobName.strip(), 'test_result.arti')):
                test_logs += 1

            if os.path.exists('%s%s/%s' % (project_path, jobName.strip(), 'build_result.arti')):
                build_logs += 1

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
            print str(ex)
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
            print str(e)

    # @TODO Below code for getting Batch Test Details and other functionality is in progress. 
    def getBatchTestDetails(self, batchList, catalog):
        out = []
        # Get the project Names and fetch test details from them.
        projects = self.getLocalProjectForGivenBatch(batchList.get('local', []))
        project = Project(catalog)
        return project.getTestDetails(projects, 'local')
        # @TODO add code for GSA/archived jobs too.
        # Now from the projects associated with Batch Get the info and send to requesting call.

    # Fetch all the info related to local projects for given batch job.
    def getLocalProjectForGivenBatch(self, batchList):
        # Strip batch name from given batch file path in the list batchList
        batchNames = [str(ntpath.basename(i)) for i in batchList]
        projects = []
        # Walk through directories and search for the batch related projects to fetch info.
        try:
            for dirname, dirnames, filenames in os.walk(globals.localPathForBatchTestResults):
                for filename in sorted(filenames):
                    actualFilePath = "%s/%s" % (dirname, filename)
                    if filename != ".gitignore" and filename in batchNames:
                        batchFile = open(actualFilePath)
                        projects.extend([i.strip() for i in batchFile.readlines()])
                        batchFile.close()
        except Exception, ex:
            print str(ex)
        return projects
