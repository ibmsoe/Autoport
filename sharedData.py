# The managed list is divided into two types of lists: static and dynamic.
#
# 1) static lists are 'autoport[Chef]packages'
# 2) dynamic list is 'userPackages'
#
# Static lists are updated by dropping code changes to autoport.  The user can add
# new packages and remove them through via the tool in the Build Servers tab.  These
# packages are added and removed from the 'userPackages' list.  The user can update
# the version of a static package.  It would go into the 'userPackage' with the
# new version and it would also be included in the static list with the original
# version.   For example, python 2.7 static and python 3.3 dynamic.  The user interface
# code needs to make a special case for this as both cannot be in the master list.
# the static lists as that would break the tool. The user cannot remove packages from
# the static lists as these are needed for the correct operation of the tool.
#
# The get operation is invoked at the start of all build server related tasks.  It
# returns the combination of the latest static data and shared user data.  The shared
# file is updated if it doesn't exist or if it contains downlevel static lists wrt the
# autoport instance performing the get.
#
# IMPORTANT: CODE DROP REQUIREMENT
#
#      if you update the managedList.json file, you need to increment the
#      the sequence number in your code drop.
#
# The sequence number is chronological in nature.  The larger the number the later
# edition of the static list.  If sequence number x > sequence number y, the static
# lists associated with x are used.
#
# A sync operation is a commit.  In general, the flow is get the managed list into memory,
# operate on it in memory, adding and removing packaces from UserPackages, then sync it.
# The memory copy is written to the local file, and then to the shared file.

import os
import globals
import paramiko
from flask import json

class SharedData:
    def __init__(self, jenkinsHost,
            jenkinsUser="root",
            jenkinsKey=globals.configJenkinsKey,
            sharedDataDir="/var/opt/autoport/"):
        self.__jenkinsHost = jenkinsHost
        self.__jenkinsUser = jenkinsUser
        self.__jenkinsKey = jenkinsKey
        self.__sharedDataDir = sharedDataDir
        self.__localDataDir = globals.localPathForConfig
        try:
            self.__jenkinsSshClient = paramiko.SSHClient()
            self.__jenkinsSshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.__jenkinsSshClient.connect(self.__jenkinsHost, username=self.__jenkinsUser, key_filename=self.__jenkinsKey)
            self.__jenkinsFtpClient = self.__jenkinsSshClient.open_sftp()
        except IOError as e:
            print str(e)
            assert(False)

    def getLocalData(self, name):
        localPath = self.__localDataDir + name
        try:
            f = open(localPath)
            dataStr = json.load(f)
            f.close();
        except IOError as e:
            print str(e)
            assert(False)
        return dataStr

    def putLocalData(self, data, prefix):
        localPath = self.__localDataDir + "putShared" + data['name']
        try:
            f = open(localPath, 'w')
            dataStr = json.dumps(data)
            f.write(dataStr);
            f.close();
        except IOError as e:
            print str(e)
            assert(False)
        return localPath

    def getSharedData(self, name):
        localPath = self.__localDataDir + "getShared" + name
        dataStr = ""
        try:
            self.__jenkinsFtpClient.chdir(self.__sharedDataDir)
            self.__jenkinsFtpClient.get(name, localPath)
            f = open(localPath)
            dataStr = json.load(f)
            f.close()
        except IOError as e:
            pass
        return dataStr

    def putSharedData(self, data, oldData):
        sharedPath = self.__sharedDataDir + data['name']

        # Data is manipulated in memory, written to local, and then ftp'd
        localPath = self.putLocalData(data, "putShared")

        try:
            self.__jenkinsFtpClient.chdir(self.__sharedDataDir)
        except IOError as e:
            self.__jenkinsFtpClient.mkdir(self.__sharedDataDir)

        try:
            # Return an error if shared data was written by another 
            # instance of autoport after we read it.  Calling code
            # should start over
            nowData = self.getSharedData(data['name'])
            if (nowData and not oldData) or (nowData and nowData['sequence'] != oldData['sequence']):
                return ""

            # Write "putShared" local data to shared location
            self.__jenkinsFtpClient.put(localPath, sharedPath)

            # Read to see if our write was the last one, else return
            # an error for calling code to retry
            afterData = self.getSharedData(data['name'])
            if afterData and afterData['sequence'] != data['sequence']:
                return ""

        except IOError as e:
            print str(e)
            assert(False)

        return sharedPath

    def getDistro(self, buildServer):
        distroName = ""
        distroRelease = ""
        distroVersion = ""
        for node in globals.nodeDetails:
            if node['nodelabel'] == buildServer:
                distroName = node['distro']
                distroRelease = node['rel']
                distroVersion = node['version']
                break

        return (distroName, distroRelease, distroVersion)

    def getManagedList(self):
        localData = self.getLocalData("ManagedList.json")
        sharedData = self.getSharedData("ManagedList.json")

        saveShared = sharedData

        if not sharedData:
            path = self.putSharedData(localData, saveShared)
            if not path:
                return ""
            return localData

        localSequence = int(localData['sequence'])
        sharedSequence = int(sharedData['sequence'])

        if localSequence <= sharedSequence:
            data = sharedData
        else:
            update = False
            for sharedRuntime in sharedData['managedRuntime']:
                for localRuntime in localData['managedRuntime']:
                    if localRuntime['distro'] != sharedRuntime['distro']:
                        continue
                    if localRuntime['distroVersion'] != sharedRuntime['distroVersion']:
                        continue
                    localRuntime['userPackages'] = sharedRuntime['userPackages']
                    update = True
            if update:
                path = self.putSharedData(localData, saveShared)
                if not path:
                    return ""
            data = localData

        return data

    def getManagedPackage(self, managedList, packageName, node):
        # Allow user to pass in managedList in case he needs to perform multiple lookups
        if not managedList:
            managedList = topology.getManagedList()

        distroName, distroRel, distroVersion = self.getDistro(node)

        pkgName = ""
        pkgVersion = ""
        for runtime in managedList['managedRuntime']:
            if runtime['distro'] != distroName:
                continue
            if runtime['distroVersion'] != distroRel and runtime['distroVersion'] != distroVersion:
                continue
            for package in runtime['autoportPackages']:
                if package['name'] == packageName:
                    try:
                        pkgName = package['name']
                        pkgVersion = package['version']
                    except KeyError:
                        break
            break

        return pkgName, pkgVersion
