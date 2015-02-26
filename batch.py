import globals
import os
import paramiko
import tempfile
from stat import ST_SIZE, ST_MTIME
from time import localtime, asctime
from flask import json

class Batch:
    def __init__(self):
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(globals.hostname, username=globals.configUsername, \
                password=globals.configPassword)
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
                            filteredList.append(self.parseBatchBuf(globals.localPathForBatchFiles + filename, "local"))
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
                    filteredList.append(self.parseBatchBuf(putdir + "/" + filename, "gsa"))
        except IOError:
            pass
        return filteredList

    def parseBatchBuf(self, filename, location):
        st = os.stat(filename)
        f = open(filename)
        
        size = st[ST_SIZE]
        datemodified = asctime(localtime(st[ST_MTIME]))

        try:
            fileBuf = json.load(f)
        except ValueError:
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
                environment = "System Default"
        except KeyError:
            environment = "System Default"
        
        try:
            owner = fileBuf['config']['owner']
        except KeyError:
            owner = "Anonymous"
                
        return {"location": location, "owner": owner, "name": name, "size": size, \
            "datemodified": datemodified, "environment": environment, "filename": filename}
