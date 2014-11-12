import paramiko
import tempfile
import shutil

# host: ausgsa.austin.ibm.com
# user: jenkin01
# pass: 5PtS6dKP12f
# dir: /ausgsa-p14/05/powersoe/autoport/catalog
# http://docs.paramiko.org/en/1.15/api/sftp.html
# http://jessenoller.com/blog/2009/02/05/ssh-programming-with-paramiko-completely-different

# import paramiko
# ssh = paramiko.SSHClient()
# ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# ssh.connect("ausgsa.austin.ibm.com", username="jenkin01", password="5PtS6dKP12f")
# ftp = ssh.open_sftp()
# ftp.chdir("/projects/p/powersoe/autoport/catalog/")
# ftp.listdir()

# TODO change default dir to test_results
class Catalog:
    def __init__(self, hostname, username = "jenkin01",
            password = "5PtS6dKP12f",
            path = "/projects/p/powersoe/autoport/test_results"):
        assert(hostname != None and username != "" and password != "")
        self.__host = hostname
        self.__username = username
        self.__password = password
        self.__path = path
        self.__tmpdirs = []
        try:
            self.__sshClient = paramiko.SSHClient()
            self.__sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.__sshClient.connect(self.__host, username=self.__username, password=self.__password)
            self.__ftpClient = self.__sshClient.open_sftp()
        except IOError:
            assert(False)

    def listJobResults(self):
        try:
            print "Getting list of jenkins job results"
            self.__ftpClient.chdir(self.__path)
            return self.__ftpClient.listdir()
        except IOError:
            return None

    def getResults(self, build):
        try:
            putdir = tempfile.mkdtemp(prefix="autoport_")
            self.__ftpClient.chdir(self.__path+"/"+build)
            self.__ftpClient.get("meta.arti", putdir+"/meta.arti")
            self.__ftpClient.get("dependency.arti", putdir+"/dependency.arti")
            self.__ftpClient.get("test_result.arti", putdir+"/test_result.arti")
            self.__tmpdirs.append(putdir)
            return putdir
        except IOError:
            return None

    def cleanTmp(self):
        for tmpdir in self.__tmpdirs:
            shutil.rmtree(tmpdir)

    def close(self):
        self.__ftpClient.close()
        self.cleanTmp()

    def __del__(self):
        self.close()

