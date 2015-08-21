import globals
import os
import paramiko
import tempfile
import ntpath
from buildAnalyzer import inferBuildSteps
from stat import ST_SIZE, ST_MTIME
from time import localtime, asctime
from flask import json

class Batch:
    def __init__(self):
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(globals.hostname, username=globals.configUsername, \
                password=globals.configPassword, port=globals.port)
            self.ftp_client = self.ssh_client.open_sftp()
        except IOError as e:
            print str(e)
            assert(False)

    def listBatchFiles(self, repoType, filt):
        res = []
        if repoType == "gsa" or repoType == "all":
            res = self.listGSABatchFiles(filt)
        if repoType == "local" or repoType == "all":
            res = res + self.listLocalBatchFiles(filt)
        return res

    def listLocalBatchFiles(self, filt):
        filteredList = []
        try:
            for dirname, dirnames, filenames in os.walk(globals.localPathForBatchFiles):
                for filename in sorted(filenames):
                    if filt in filename.lower() or filt == "":
                        if filename != ".gitignore":
                            filteredList.append(self.parseBatchFileList(globals.localPathForBatchFiles + filename, "local"))
        except IOError:
            pass
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
        except IOError:
            pass
        return filteredList

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
        except:
            return {"error": "Could not archive batch file " + filename }

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
        except ValueError:
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
