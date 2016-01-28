import globals
import os
import re
import paramiko
from flask import json
from catalog import Catalog
from resultParser import ResultParser
from stat import S_ISDIR
import posixpath
from log import logger

class Project:
    """
    Project class will be handling various functionalities associated with Projects.
    """
    def __init__(self, catalog):
        self.catalog = catalog
        self.resParser = ResultParser()
        self.projectResultPattern = re.compile('(.*?)\.(.*?)\.(.*?)\.N-(.*?)\.(.*?)\.(\d\d\d\d-\d\d-\d\d-h\d\d-m\d\d-s\d\d)')

    def getTestDetail(self, projectName, repo):
        """
        This function will return detail for the given project
        Args:
            projects(str):  Project Names for getting details
            repo(str):      Repository location gsa/local

        Returns:
            Dictionary with project detail.
        """
        res = {}
        resultDir = None
        try:
            resultDir = self.catalog.getResults(projectName, repo)
            try:
                if resultDir and os.path.isfile(resultDir+"/test_result.arti"):
                    res = self.resParser.resultParser(resultDir+"/test_result.arti")
            except Exception as ex:
                logger.debug("In getTestDetail, Project %s failed with error \"%s\"" % (projectName, str(ex)))
        except Exception as ex:
            logger.debug("In getTestDetail, repo=%s file=%s/test_result.arti file error " % (repo, projectName))
            logger.debug("Error \"%s\"" % (str(ex)))

        # We may be able to do without meta.arti as most of the data can be derived from
        # the project name itself, but it may provide an indication that a build was successful
        # as this file is produced by Jenkins as opposed to the buildAnalyzer
        meta = {}
        if resultDir:
            try:
                meta_file = open(resultDir+"/meta.arti")
                meta = json.load(meta_file)
                meta_file.close()
            except Exception as ex:
                # If meta.arti is not found just continue with what is available.
                logger.debug("In getTestDetail, repo=%s file=%s/meta.arti file error " % (repo, projectName))
                logger.debug("Error \"%s\"" % (str(ex)))

        # Validate that the directory looks like a test result
        project_info = self.projectResultPattern.match(projectName)
        try:
            pkg = project_info.group(4)                         # ie. N-junit
            ver = project_info.group(5)                         # ie. current
        except AttributeError:
            pkg = ""
            ver = ""

        #self.catalog.cleanTmp()
        # not cleaning /tmp folder as this is required for showing build logs and test logs
        # Instead will be clearing when next request for comparison is done.

        return { "job": projectName, "pkg" : pkg or '-', "ver": ver or '-',
                 "results": res, "project": meta, "repository": repo }

    def getTestDetails(self, projects = [], repo = 'local'):
        """
        This function will return details for the list of projects
        Args:
            projects(list): List of project Names for getting details
            repo(str):      Repository location gsa/local

        Returns:
            Dictionary with project details.
        """
        if repo not in ('gsa', 'local'):
            return {
                status: "failure",
                error: "Invalid repository location specified"
            }
        project_test_result = []
        response_data = []
        for projectName in projects:
            project_test_result.append(self.getTestDetail(projectName, repo))

        if not response_data:
            response_data = {
                "status": "ok",
                "results": project_test_result
            }

        return response_data

    # Sub-Routine which deletes files and folders recursively from remote directory
    # @Param - remotepath, which represents the GSA folder
    # @Param - ftp_client, which represents paramiko SFTP object
    def removeDirFromGSA(self, ftpClient, remotepath):
        logger.debug("In removeDirFromGSA, remotepath=%s" % remotepath)
        ftp_client = ftpClient.open_sftp()
        try:
            for file in ftp_client.listdir(remotepath):
                try:
                    filepath = os.path.join(remotepath, file)
                    if S_ISDIR(ftp_client.stat(filepath).st_mode):
                        removeDirFromGSA(ftp_client, filepath)
                    else:
                        ftp_client.remove(filepath)
                except IOError as e:
                    logger.warning("Can't remove file %s" % filepath)
            ftp_client.rmdir(remotepath)
        except IOError as e:
            logger.warning("Can't remove directory" + str(e))
        finally:
            try:
                ftp_client.close()
            except Exception as e:
                logger.warning('project:removeDirFromGSA, Error=%s' % str(e))

    def stripDataFromJobName(self, jobFileName):
        jobName = self.projectResultPattern.match(jobFileName).group(2)                     # uuid field
        jobNode = self.projectResultPattern.match(jobFileName).group(3)                     # build server
        jobPkg = self.projectResultPattern.match(jobFileName).group(4)                      # project name
        jobPkgVer = self.projectResultPattern.match(jobFileName).group(5)                   # project version
        jobDate = self.projectResultPattern.match(jobFileName).group(6)                     # build date

        return (jobName, jobNode, jobPkg, jobPkgVer, jobDate)

    def getDiffLogResult(self, logFile, leftBuild, rightBuild, leftRepo, rightRepo):
        """
        This function will read given logfile and generate a comparison diff data.
        Args:
            logfile(str): which log file to use test_result.arti or build_result.arti
            leftBuild(str):         First Build job Name
            rightBuild(str):        Second Build job Name
            leftRepo(str):          First Build job Repo Name for comparison
            rightRepo(str):         Second Build job Repo Name for comparison

        Returns:
            Dictionary with comparison data for given projects.
        """

        if (not (leftBuild and rightBuild)):
            return {"error": "Invalid argument", "http_code": 400}

        leftDir = self.catalog.getResults(leftBuild, leftRepo)
        rightDir = self.catalog.getResults(rightBuild, rightRepo)

        if not leftDir:
            return {"error": leftBuild + "/" + logFile + " not found", "http_code": 401}

        if not rightDir:
            return {"error": rightBuild + "/" + logFile + " not found", "http_code": 401}

        try:
            rightName, rightNode, rightPkg, rightPkgVer, rightDate = self.stripDataFromJobName(rightBuild)
        except AttributeError:
            return {"error": "Invalid job name" + rightBuild, "http_code": 402}

        try:
            leftName, leftNode, leftPkg, leftPkgVer, leftDate = self.stripDataFromJobName(leftBuild)
        except AttributeError:
            return {"error": "Invalid job name" + leftBuild, "http_code": 402}

        try:
            res = self.resParser.ResLogCompare(logFile, leftName, leftDir, rightName, rightDir)
        except BaseException as e:
            return {"error": str(e), "http_code": 500}

        leftCol = {
            'log': logFile,
            'job': leftBuild,
            'repo': leftRepo,
            'pkgname': leftPkg,
            'pkgver': leftPkgVer,
            'date': leftDate,
            'diffName': leftName
        }

        try:
            # Build server may be unknown to us
            i = globals.nodeLabels.index(leftNode)
            leftCol['distro'] = globals.nodeOSes[i]
        except ValueError:
            leftCol['distro'] = leftNode

        rightCol = {
            'log': logFile,
            'job': rightBuild,
            'repo': rightRepo,
            'pkgname': rightPkg,
            'pkgver': rightPkgVer,
            'date': rightDate,
            'diffName': rightName
        }

        try:
            # Build server may be unknown to us
            i = globals.nodeLabels.index(rightNode)
            rightCol['distro'] = globals.nodeOSes[i]
        except ValueError:
            rightCol['distro'] = rightNode

        return {
            "leftCol": leftCol,
            "rightCol": rightCol,
            "results": res,
            "http_code": 200
        }
