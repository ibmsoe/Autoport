import globals
import paramiko
from threading import Thread, local
from log import logger
from threadpool import ThreadPool, makeRequests
from time import sleep
from urlparse import urlparse

th = local()

class Mover:
    def __init__(self):
        self.__jenkinsHost = urlparse(globals.jenkinsUrl).hostname
        self.__jenkinsUser = "root"
        self.__jenkinsKey = globals.configJenkinsKey

        # Keep startup times short.  Only connect a few threads to Jenkins upfront.  The rest
        # will be dynamically added as required.  This also enables authentication issues to be
        # resolved by the system admin or developer without taking the tool down

        for i in range(globals.threadPoolSize):
            threadRequests = makeRequests(self.connectInit, [((i,), {})])
            [globals.threadPool.putRequest(req) for req in threadRequests]

        # Do 1 to validate the connection.  This guarantees that config.ini data / globals is correct  
        for i in range(1):
            threadRequests = makeRequests(self.connect, [((i,), {})])
            [globals.threadPool.putRequest(req) for req in threadRequests]
            globals.threadPool.wait()

        # Do 2 more to validate reconnect logic.  Has to be 2 as the same thread may be re-scheduled
        for i in range(2):
            threadRequests = makeRequests(self.connectRetry, [((), {})])
            [globals.threadPool.putRequest(req) for req in threadRequests]

        # Uncomment this if you want to connect all up front.  
#       for i in range(globals.threadPoolSize):
#           threadRequests = makeRequests(self.connectValidate, [((i,), {})])
#           [globals.threadPool.putRequest(req) for req in threadRequests]

    def connectInit(self, i):
        th.__status = -1
        th.__id = i
        sleep(3)                              # Increase the odds that each thread will run

    def connect(self, i):
        try:
            if th.__status:
                try:
                    th.__jenkinsSshClient = paramiko.SSHClient()
                    th.__jenkinsSshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    th.__jenkinsSshClient.connect(self.__jenkinsHost, username=self.__jenkinsUser,
                                                  key_filename=self.__jenkinsKey)
                    th.__jenkinsFtpClient = th.__jenkinsSshClient.open_sftp()
                    th.__jenkinsTransportSession = th.__jenkinsSshClient.get_transport()
                except paramiko.AuthenticationException as e:
                    msg="Thread[%s] Please provide valid Jenkins credentials in settings menu!" % str(th.__id)
                    logger.debug(msg)
                    logger.debug(str(e))
                except paramiko.SSHException as e:
                    msg="Thread[%s] SSH connection error to Jenkins.  You may need to authenticate.  Check networking!" % str(th.__id)
                    logger.debug(msg)
                    logger.debug(str(e))
                except IOError as e:
                    msg = "Thread[%s] Please ensure that the host associated with the Jenkins URL is reachable!"
                    logger.debug(msg)
                    logger.debug(str(e))
                else:
                    th.__status = 0
                    logger.info("Thread[%s] connected to Jenkins master" % str(th.__id))
                    sleep(4)
        except:
            th.__status = -1
            th.__id = -i
        else:
            sleep(3)

    def connectRetry(self):
        for j in range(3):
            try:
                if th.__status:
                    try:
                        logger.debug("Thread[%s] Attempting to connect" % (str(th.__id)))
                        self.connect(th.__id)
                        if th.__status:    # failed retry
                            sleep(4)       # sleep to give target server a chance to free resources, etc
                            continue
                    except:
                        th.__status = -1
            except:
                logger.debug("Thread state not set in initialization phase.  Initializing now")
                th.__id = -1
                th.__status = -1
                self.connect(th.__id)
            if not th.__status:
                sleep(4)                  # Sleep so it is not rescheduled immediately, let others run to retry connect
                break                     # Thread is connected

    def connectValidate(self, i):
        if th.__status:
            msg = "Thread[%s] failed to connected to Jenkins master" % str(th.__id)
            logger.error(msg)
            assert(False), msg 
        sleep(3)                            # Sleep just to make sure no thread is scheduled twice

    def mkdir(self, path):
        try:
            th.__jenkinsFtpClient.mkdir(path)
        except Exception as e:
            th.__status = -1
            self.connectRetry()
            try:
                th.__jenkinsFtpClient.mkdir(path)
            except Exception as e:
                logger.error("mover.mkdir: " + str(e))

    def chdir(self, path):
        try:
            th.__jenkinsFtpClient.chdir(path)
        except Exception as e:
            th.__status = -1
            self.connectRetry()
            try:
                th.__jenkinsFtpClient.chdir(path)
            except Exception as e:
                logger.error("mover.chdir: " + str(e))

    def listdir(self):
        flist = []
        try:
            flist = th.__jenkinsFtpClient.listdir()
        except Exception as e:
            th.__status = -1
            self.connectRetry()
            try:
                flist = th.__jenkinsFtpClient.listdir()
            except Exception as e:
                logger.error("mover.listdir: " + str(e))
        return flist

    def get(self, remotefile, localpath):
        try:
            th.__jenkinsFtpClient.get(remotefile, localpath)
        except Exception as e:
            th.__status = -1
            self.connectRetry()
            try:
                th.__jenkinsFtpClient.get(remotefile, localpath)
            except Exception as e:
                logger.error("mover.get: " + str(e))

    def put(self, localpath, remotepath):
        try:
            th.__jenkinsFtpClient.put(localpath, remotepath)
        except Exception as e:
            th.__status = -1
            self.connectRetry()
            try:
                th.__jenkinsFtpClient.put(localpath, remotepath)
            except Exception as e:
                logger.error("mover.put: " + str(e))

    def rmdir(self, remotepath):
        try:
            th.__jenkinsFtpClient.rmdir(remotepath)
        except Exception as e:
            th.__status = -1
            self.connectRetry()
            try:
                th.__jenkinsFtpClient.rmdir(remotepath)
            except Exception as e:
                logger.error("mover.rmdir: " + str(e))

    def stat(self, remotepath):
        stats = []
        try:
            stats = th.__jenkinsFtpClient.stat(remotepath)
        except Exception as e:
            th.__status = -1
            self.connectRetry()
            try:
                stats = th.__jenkinsFtpClient.stat(remotepath)
            except Exception as e:
                logger.error("mover.stat: " + str(e))
        return stats

    def unlink(self, remotepath):
        try:
            th.__jenkinsFtpClient.unlink(remotepath)
        except Exception as e:
            th.__status = -1
            self.connectRetry()
            try:
                th.__jenkinsFtpClient.unlink(remotepath)
            except Exception as e:
                logger.error("mover.unlink: " + str(e))

    def close(self):
        try:
            th.__jenkinsFtpClient.close()
        except Exception as e:
            th.__status = -1
            self.connectRetry()
            try:
                th.__jenkinsFtpClient.close()
            except Exception as e:
                logger.error("mover.close: " + str(e))
