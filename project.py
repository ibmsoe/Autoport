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
                if(os.path.isfile(resultDir+"/test_result.arti")):
                    res = self.resParser.MavenBuildSummary(resultDir+"/test_result.arti")
            except Exception, ex:
                logger.info(str(ex))
        except Exception, ex:
            logger.warning("Error: Project %s failed with error \"%s\"" % (projectName, str(ex)))

        # We may be able to do without meta.arti as most of the data can be derived from
        # the project name itself, but it may provide an indication that a build was successful
        # as this file is produced by Jenkins as opposed to the buildAnalyzer
        try:
            meta_file = open(resultDir+"/meta.arti")
            meta = json.load(meta_file)
            meta_file.close()
        except Exception, ex:
            # If meta.arti is not found just continue with what is available.
            print "Error", str(ex)
            meta = []

        # Validate that the directory looks like a test result
        project_info = self.projectResultPattern.match(projectName)
        try:
            pkg = project_info.group(5)                         # ie. N-junit
            ver = project_info.group(6)                         # ie. current
        except AttributeError:
            pass

        self.catalog.cleanTmp()

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
    def removeDirFromGSA(self, ftp_client, remotepath):
        ftp_client = ftp_client.open_sftp()
        try:
            for file in ftp_client.listdir(remotepath):
                try:
                    filepath = os.path.join(remotepath, file)
                    if S_ISDIR(ftp_client.stat(filepath).st_mode):
                        removeDirFromGSA(ftp_client, filepath)
                    else:
                        ftp_client.remove(filepath)
                except IOError as e:
                    logger.warning("Can't remove file")
            ftp_client.rmdir(remotepath)
        except IOError as e:
            logger.warning("Can't remove directory" + str(e))
