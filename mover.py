import globals
import paramiko
from threading import Thread, local
from log import logger
from threadpool import ThreadPool, makeRequests
from time import sleep
from urlparse import urlparse

th = local()

class Mover:
    def start(self, jenkinsHost,
            jenkinsUser="root",
            jenkinsKey=globals.configJenkinsKey):

        self.__jenkinsHost = jenkinsHost
        self.__jenkinsUser = jenkinsUser
        self.__jenkinsKey = jenkinsKey

        # Keep startup times short.  Only connect a few threads to Jenkins upfront.  The rest
        # will be dynamically added as required.  This also enables authentication issues to be
        # resolved by the system admin or developer without taking the tool down

        for i in range(globals.threadPoolSize):
            threadRequests = makeRequests(self.connectInit, [((i,), {})])
            [globals.threadPool.putRequest(req) for req in threadRequests]

        # Do 1 to validate the connection.  This is synchronous
        for i in range(1):
            threadRequests = makeRequests(self.connect, [((i,), {})])
            [globals.threadPool.putRequest(req) for req in threadRequests]
        globals.threadPool.wait()

        # Thread queueing results in new thread connections later, so do them all now
        # asynchronously so that they are ready when needed without having to wait.  This is
        # the connectRetry logic, so all paths are used during startup
        for i in range(globals.threadPoolSize - 1):
            threadRequests = makeRequests(self.connectRetry, [((), {})])
            [globals.threadPool.putRequest(req) for req in threadRequests]

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
                    msg="Thread[%s] Please provide valid Jenkins credentials (%s) in settings menu!" % (str(th.__id), self.__jenkinsHost)
                    logger.debug(msg)
                    logger.debug(str(e))
                except paramiko.SSHException as e:
                    msg="Thread[%s] SSH connection error to Jenkins.  You may need to authenticate.  Check networking!" % str(th.__id)
                    logger.debug(msg)
                    logger.debug(str(e))
                except Exception as e:
                    msg = "Thread[%s] connect Error: %s" % (str(th.__id), str(e))
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

    # Resetting threadpool
    def resetConnection(self):
        try:
            # Gain control over each thread
            for i in range(globals.threadPoolSize):
                threadRequests = makeRequests(self.close, [((), {})])
                [globals.threadPool.putRequest(req) for req in threadRequests]
            globals.threadPool.wait()

            globals.threadPool.dismissWorkers(globals.threadPoolSize)
            globals.threadPool.joinAllDismissedWorkers()
            globals.threadPool = ThreadPool(globals.threadPoolSize)
        except Exception as e:
            logger.error("mover.resetConnection: " + str(e))

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
            if not th.__status:
                th.__jenkinsFtpClient.close()
                th.__status = -1
                logger.info("Thread[%s] closed connection to Jenkins master" % str(th.__id))
            sleep(4)
        except Exception as e:
            logger.error("mover.close: " + str(e))
