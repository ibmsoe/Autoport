#
# This file manages two types of data:
#
# 1) Data that is shared across all users.  e.g. Chef data.
# 2) User data that needs to persist across autoport sessions.  e.g. Managed List
#
# The data above pertains to the state of build servers and is placed in
# /var/opt/autoport on Jenkins master which makes it persistent.  When autoport
# connects with the Jenkins master it refreshes itself by pulling down the data
# that it needs and it uploads new versions of this data as it is produced by
# the development team via code drops to autoport.
#
# Chef provide package configuration for autoport build slaves.  There is no end
# user component to Chef.  We support two build slave deployment models: user
# dedicated build slaves and user shared build slaves.  This latter case requires
# that Chef data be placed in a fixed central location.
#
# Chef data is located in /var/opt/autoport/chef-repo
#
# The Managed List refers to a list of packages constituting the minimum runtime
# environment.  User's can install and remove packages beyond this set.  The
# list is defined as :
#
# Managed List = <base O/S runtime> + <autoport required pkgs> + <optional user pkgs>
#
# The managed list is located at:
#
#    /var/opt/autoport/user/<username>/  if autoport is invoked as "python main.py -b"
#    /var/opt/autoport/                  if autoport is invoked as "python main.py"
#
#    where <username> comes from config.ini
#
# The autoport command argument -b tells autoport to dynamically allocate Jenkins
# Build Servers on behalf of the user.  This is a cloud feature.
#
# This file provides low level services that may be used to create additional
# shared data files in the future.  The mechanism is based on a json control file,
# which must have the following fields:
#
#    version      defines the format of the data
#    sequence     used to serialize updates at the data set level
#    name         the name of the control file
#
# Note additional fields may be added to the control file.  e.g. chef-cookbook-version
#
# The managed list is divided into two types of lists: static and dynamic.
#
# 1) static lists are 'autoportPackages and autoportChefPackages'
# 2) dynamic list is 'userPackages'
#
# Static lists are updated by dropping code changes to autoport.
#
# Users are not allowed to remove packages from the static lists as that would
# potentially break the tool.  They can only add and remove packages in the
# userPackage list.
#
# The get ML operation is invoked at the start of all build server related tasks.  It
# returns the combination of the latest static data and shared user data.  The shared
# file is updated if it doesn't exist or if it contains downlevel static lists wrt the
# autoport instance performing the get.
#
# IMPORTANT: CODE DROP REQUIREMENT
#
#      if you update the managedList.json file, you need to increment the
#      sequence number in your code drop.
#
#      if you update the chef-repo-version.json file, you need to increment the
#      fields sequence number and cookbook-version in the json control file as
#      well as the version field in the chef-repo/cookbooks/buildServer/metadata.rb file
#
# The sequence number is chronological in nature.  The larger the number the later
# edition of the static list.  If sequence number x > sequence number y, the static
# lists associated with x are used.
#
# A sync operation is a commit.  In general, the flow is get the managed list into memory,
# operate on it in memory, adding and removing packaces from UserPackages, then act on
# the list which is called a sync operation as the list is being applied to build servers
# which involves install operations.  When the list has been applied as a whole, the
# list is said to be in sync with the state of the target server(s).
#

import os
import globals
import paramiko
import tarfile
import zipfile
import re
import shutil
from flask import json
from collections import OrderedDict
from contextlib import closing

class SharedData:
    def __init__(self, jenkinsHost,
            jenkinsUser="root",
            jenkinsKey=globals.configJenkinsKey,
            sharedDataDir="/var/opt/autoport/",
            repoPathPrefix="/var/www/autoport_repo"):
        self.__jenkinsHost = jenkinsHost
        self.__jenkinsUser = jenkinsUser
        self.__jenkinsKey = jenkinsKey
        self.__sharedDataDir = sharedDataDir
        self.__repoPathPrefix = repoPathPrefix
        self.__localDataDir = globals.localPathForConfig
        self.__localPackageDir = globals.localPathForPackages
        self.__localHostName = globals.localHostName
        self.__userName = globals.configUsername
        try:
            self.__jenkinsSshClient = paramiko.SSHClient()
            self.__jenkinsSshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.__jenkinsSshClient.connect(self.__jenkinsHost, username=self.__jenkinsUser, key_filename=self.__jenkinsKey)
            self.__jenkinsFtpClient = self.__jenkinsSshClient.open_sftp()
            self.__jenkinsTransportSession = self.__jenkinsSshClient.get_transport()
        except IOError as e:
            print str(e)
            assert(False)

    def getLocalData(self, name):
        localPath = self.__localDataDir + name
        try:
            f = open(localPath)
            dataStr = json.load(f, object_pairs_hook=OrderedDict) # Load the json data maintaining its original order.
            f.close();
        except IOError as e:
            print str(e)
            assert(False)
        return dataStr

    def putLocalData(self, data, prefix):
        localPath = self.__localDataDir + prefix + data['name']
        try:
            f = open(localPath, 'w')
            json.dump(data, f, indent=4, sort_keys=False) # writes back in pretty printed json form
            f.close();
        except IOError as e:
            print str(e)
            assert(False)
        return localPath

    def getSharedData(self, name, path):
        localPath = self.__localDataDir + "getShared" + name
        data = {}
        try:
            self.__jenkinsFtpClient.chdir(self.__sharedDataDir + path)
            self.__jenkinsFtpClient.get(name, localPath)
            f = open(localPath)
            data = json.load(f)
            f.close()
        except IOError as e:
            pass
        return data

    def putSharedData(self, data, oldData, path):

        # path is an optional extension to sharedDataDir.  Enables
        # the caller to place a file anywhere below the base directory.
        # /user/username  --> /var/opt/autoport/user/username

        sharedPath = self.__sharedDataDir + path + data['name']

        # Data is manipulated in memory, written to local, and then ftp'd
        localPath = self.putLocalData(data, "putShared")

        # If autoport directory doesn't exist, create it
        try:
            previousDirectory = self.__sharedDataDir
            self.__jenkinsFtpClient.chdir(previousDirectory)
        except IOError as e:
            self.__jenkinsFtpClient.mkdir(previousDirectory)

        # Create the optional directories provided via path
        directories = path.split("/")
        for directory in directories:
            try:
                previousDirectory = previousDirectory + directory + "/"
                self.__jenkinsFtpClient.chdir(previousDirectory)
            except IOError as e:
                self.__jenkinsFtpClient.mkdir(previousDirectory)

        try:
            # Return an error if shared data was written by another
            # instance of autoport after we read it.  Calling code
            # should start over
            nowData = self.getSharedData(data['name'], path)
            if (nowData and not oldData) or \
               (nowData and nowData['sequence'] != oldData['sequence']):
                return ""

            # Write "putShared" local data to shared location
            self.__jenkinsFtpClient.put(localPath, sharedPath)

            # Read to see if our write was the last one, else return
            # an error for calling code to retry
            afterData = self.getSharedData(data['name'], path)
            if afterData and afterData['sequence'] != data['sequence']:
                return ""

        except IOError as e:
            print str(e)
            assert(False)

        return sharedPath

    def putLocalFile(self, file):
        # Saving file to a local path on the autoport host.
        try:
            localPath = os.path.join(self.__localPackageDir, file.filename)
            file.save(localPath)
        except IOError as e:
            print str(e)
            assert(False)
        return localPath

    def putSharedFile(self, localPath, remotePath, filename):
        # Transfer the file to remote path on Jenkins master that is
        # shared by all autoport instances
        try:
            self.__jenkinsFtpClient.chdir(remotePath)
        except IOError as e:
            self.__jenkinsFtpClient.mkdir(remotePath)
        try:
            remotePath = os.path.join(remotePath, filename)
            self.__jenkinsFtpClient.put(localPath, remotePath)

        except IOError as e:
            print str(e)
            assert(False)

    def executeSharedCommand(self, command):
        # Execute remote commands on Jenkins Master to manipulate shared data
        transport = self.__jenkinsTransportSession
        try:
            channel = transport.open_channel(kind = "session")
            channel.exec_command(command)
            exit_status = channel.recv_exit_status()
            if exit_status != 0:
                stderr = channel.makefile_stderr('rb', -1).readlines()
                print stderr
                assert(False)
        except IOError as e:
            print str(e)
            assert(False)

    def allowedRepoPkgExtensions(self, filename):
        # Check the valid file types to be uploaded to repository
        # based on the extensions.

        # Add extra extensions to the list if required in future.

        EXTENSIONS = ['.rpm', '.deb', '.zip', '.tar', '.tgz', '.tar.gz', '.tar.bz2']
        return any([filename.endswith(x) for x in EXTENSIONS])

    def getRepoDetails(self, localPath, filename, sourceType):
        # Framing remotepath and command, to transfer the file
        # and update the custom repository
        # based on type (rpm/deb/tar.gz)
        repoPath = ""
        command  = ""
        repo_base_dir = self.__repoPathPrefix
        name, extension = os.path.splitext(localPath)
        if extension == '.rpm':
            repoPath = "%s/rpms" % (repo_base_dir)
            command = "createrepo --update -v %s" % (repoPath)
        elif extension == '.deb':
            repoPath = "%s/debs/" % (repo_base_dir)
            command = "reprepro -V -b %s includedeb autoport_repo \
                       %s/%s" % (repoPath, repoPath, filename)
        elif tarfile.is_tarfile(localPath) or zipfile.is_zipfile(localPath):
            repoPath = "%s/archives/" % (repo_base_dir)
            # archive.log holds tar filename, version and sourceType CSV
            archiveLogPath = "%s/archives/archive.log" % (repo_base_dir)

            # Extracting source filename
            sourceName = re.findall("(?:)[\(a-z),(A-Z),-]+",filename)[0]
            if sourceName[len(sourceName)-1] == "-":
                sourceName = sourceName[:sourceName.rfind('-')]

            # Extracting source file version
            sourceVersion = re.findall("(?:)[\d.]+",filename)[0]

            # If source file doesn't have version associated, regex returns a dot(.)
            if sourceVersion == ".":
                sourceVersion = ""
            elif sourceVersion[len(sourceVersion)-1] == "." :
                sourceVersion = sourceVersion[:sourceVersion.rfind('.')]

            # Command which writes the source filename, version and
            # sourceType CSV into archive.log. Command also avoids duplicate entries
            logEntry = sourceName + "," + sourceVersion +"," + sourceType + "," + sourceName
            command = "touch " + archiveLogPath + "; grep -q -F \"" + logEntry + \
               "\" "+ archiveLogPath + " || echo \"" + logEntry + "\" >> " + archiveLogPath
        return repoPath, command

    def buildTarFile(self, output_filename, source_dir):
        # Routine to create tar file
        with closing(tarfile.open(output_filename, "w:gz")) as tar:
            tar.add(source_dir, arcname=os.path.basename(source_dir))

    def uploadPackage(self, file, sourceType):

        # Saving the file to a local path on autoport host
        localPath = self.putLocalFile(file)

        # Based on the file type, deciding the remote path where the file is
        # to be saved and framing the appropriate command to add it to custom repository.
        remotePath, command  = self.getRepoDetails(localPath, file.filename, sourceType)

        # If no remotePath is returned , file is not a valid rpm/deb or archive
        # hence deleting the package uploaded to temporary location
        if not remotePath:
            os.remove(localPath)
            return "Inappropriate or Invalid file-type"

        # Saving the file to remote path on the custom repository
        self.putSharedFile(localPath, remotePath, file.filename)

        # After the file is sucessfully saved to the remote location, deleting
        # the file from local path on autoport host.
        os.remove(localPath)

        # Executing the command on the custom repository to add the file to
        # existing repository.
        self.executeSharedCommand(command)

    def uploadChefData(self):
        # This routine is responsible for uploading chef-data to Jenkins Master
        # and also uploading the latest cookbook to chef-server.

        # Fetching version from this autoport instance
        localData = self.getLocalData("chef-repo-version.json")
        localSequence = int(localData['sequence'])
        localVersion = int(localData['version'])

        # Fetching version from jenkins Master
        sharedData = self.getSharedData("chef-repo-version.json", "")
        try:
            sharedSequence = int(sharedData['sequence'])
            sharedVersion = int(sharedData['version'])
        except KeyError:
            sharedSequence = 0
            sharedVersion = 0

        # Upload local copy if it is more recent
        if localVersion > sharedVersion or \
           (localVersion == sharedVersion and localSequence > sharedSequence):

            # Upload local chef-repo-version.json
            self.putSharedData(localData, sharedData, "")

            # For debugging / validation purposes, let's copy the control file
            # into the Chef data as this is a 2 step update.  Also identify
            # which node made the update.

            try:
                localData['username'] = self.__userName
                localData['hostname'] = self.__localHostName
                localPath = self.putLocalData(localData, "")
                shutil.copyfile(localPath, "chef-repo/autoport-chef-repo-version.json")
            except IOError:
                pass

            filename = "chef-repo.tar.gz"
            localPath = self.__localDataDir + filename
            remotePath = self.__sharedDataDir

            # Building tar file of the chef-repo and placing in local config dir
            self.buildTarFile(localPath, "chef-repo")

            # Transfer the chef tar file to the shared location on Jenkins Master
            self.putSharedFile(localPath, remotePath, filename)

            command = "cd " + remotePath + " && tar -xvf " + filename + \
                      " && cd chef-repo && knife ssl fetch && knife upload /"
            self.executeSharedCommand(command)

            print "chef upload 1"
            print "Before local data=", localData
            print "Before shared data=", sharedData

            # Read the shared control data again and validate that we are still latest
            sharedData = self.getSharedData("chef-repo-version.json", "")
            try:
                sharedSequence = int(sharedData['sequence'])
                sharedVersion = int(sharedData['version'])
            except KeyError:
                sharedSequence = 0
                sharedVersion = 0

            print "After shared data=", sharedData

            # Somebody else has updated the repository
            if sharedSequence != localSequence and sharedVersion != localVersion:
                return

            # Validate that the chef-repo data contains the expected version or a newer one
            newSharedData = self.getSharedData("autoport-chef-repo-version.json", "/chef-repo")

            print "chef-repo data=", newSharedData

            try:
                newSharedSequence = int(newSharedData['sequence'])
                newSharedVersion = int(newSharedData['version'])
            except KeyError:
                newSharedSequence = 0
                newSharedVersion = 0

            # Try it again once
            if localVersion > newSharedVersion or \
               (localVersion == newSharedVersion and localSequence > newSharedSequence):
                print "Updating chef-repo data again"
                self.executeSharedCommand(command)

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

        print "allocBuildServers=", globals.allocBuildServers
        if globals.allocBuildServers:
            sharedPath = "/user/" + self.__userName + "/"
        else:
            sharedPath = ""

        sharedData = self.getSharedData("ManagedList.json", sharedPath)

        saveShared = sharedData

        if not sharedData:
            path = self.putSharedData(localData, saveShared, sharedPath)
            if not path:
                return ""
            return localData

        localSequence = int(localData['sequence'])
        localVersion = int(localData['version'])

        sharedSequence = int(sharedData['sequence'])
        sharedVersion = int(sharedData['version'])

        # Upload local copy if it is more recent after merging user data from shared
        if localVersion > sharedVersion or \
           (localVersion == sharedVersion and localSequence > sharedSequence):
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
                path = self.putSharedData(localData, saveShared, sharedPath)
                if not path:
                    return ""
            data = localData
        else:
            data = self.mergeManagedLists(localData, sharedData)

        return data


    def getManagedPackage(self, managedList, pkg, node):
        # Allow user to pass in managedList in case he needs to perform multiple lookups
        if not managedList:
            managedList = topology.getManagedList()

        distroName, distroRel, distroVersion = self.getDistro(node)

        # The version becomes managed version if it satisfies the below cases
        # case 1: If the jenkins returned package arch matches with arch of ManagedList and version
        #         available in ManagedList then the version from ManagedList becomes the Managed Version
        # case 2: If the jenkins returned package has the arch but not in ManagedList and version
        #         available in ManagedList then the version from ManagedList becomes the Managed Version
        # case 3: If in the above two cases the ManagedList doesn't contain version for given package
        #         then installedVersion becomes the managed version
        packageName = pkg["packageName"]
        pkgVersion = ""
        userAddedVersion = "No"
        removablePackage = "Yes"
        for runtime in managedList['managedRuntime']:
            if runtime['distro'] != distroName:
                continue
            if runtime['distroVersion'] != distroRel and runtime['distroVersion'] != distroVersion:
                continue
            for package in runtime['autoportChefPackages']:
                if package['name'] == pkg['packageName'] or \
                   ("tagName" in package and package["tagName"] == pkg['packageName']):
                    removablePackage = "No"
                    if "arch" in package and package['arch'] == pkg['arch']:
                        if "version" in package:
                            pkgVersion = package['version']
                        else:
                            pkgVersion = pkg['updateVersion']
                    else:
                        if "version" in package:
                            pkgVersion = package['version']
                        else:
                            pkgVersion = pkg['updateVersion']
                if pkgVersion:
                    break
            if not pkgVersion:
                for package in runtime['autoportPackages']:
                    if package['name'] == pkg['packageName']:
                        removablePackage = "No"
                        if "arch" in package and package['arch'] == pkg['arch']:
                            if "version" in package:
                                pkgVersion = package['version']
                            else:
                                pkgVersion = pkg['updateVersion']
                        else:
                            if "version" in package:
                                pkgVersion = package['version']
                            else:
                                pkgVersion = pkg['updateVersion']
                    if pkgVersion:
                        break
            for package in runtime['userPackages']:
                if package['name'] == packageName and \
                   package['owner'] == self.__userName and \
                   "arch" in package and package['arch'] == pkg['arch']:
                    try:
                        removablePackage = "Yes"
                        userAddedVersion = package['version']
                    except KeyError:
                        break
        if not pkgVersion:
            pkgVersion="N/A"
        return packageName, pkgVersion, userAddedVersion, removablePackage

    def addToManagedList(self, packageDataList, action): # packageName, packageVersion, distro, arch, action):
        # Read the file in memory
        localManagedListFileData = self.getLocalData("ManagedList.json")

        # Perform additions to memory list
        for pkgData in packageDataList:
            packageName = pkgData['package_name']
            packageVersion = pkgData['package_version']
            distro = pkgData['distro']
            arch = pkgData['arch']
            packageType = pkgData['package_type']  if 'package_type' in pkgData else ''

            for sharedRuntime in localManagedListFileData['managedRuntime']:
                if pkgData['removable'] == 'No':
                    continue
                if sharedRuntime['distro'] == distro:
                    addFlag = True
                    for package in sharedRuntime['userPackages']:
                        if package['name'] == packageName and \
                           package['arch'] == arch and \
                           package['owner'] == self.__userName:
                            # If package is already present for the current user,
                            # check its version and update the version if they are different
                            if package['version'] != packageVersion:
                                package['version'] = packageVersion
                            addFlag = False
                            break
                    if addFlag == True:
                        sharedRuntime['userPackages'].append({"owner":self.__userName, "name":packageName,
                                  "version":packageVersion, "arch":arch, "action":action, "type": packageType})
                        break
        # Write back to the local managed list file
        localPath = self.putLocalData(localManagedListFileData, "")

    def removeFromManagedList(self, packageDataList, action):
        # Read the file in memory
        localManagedListFileData = self.getLocalData("ManagedList.json")

        # Perform deletion to memory list
        for pkgData in packageDataList:
            for sharedRuntime in localManagedListFileData['managedRuntime']:
                packageName = pkgData['package_name']
                packageVersion =  pkgData['package_version']
                distro = pkgData['distro']
                arch =  pkgData['arch']
                packageType = pkgData['package_type']  if 'package_type' in pkgData else ''
                if pkgData['removable'] == 'No':
                  continue
                if sharedRuntime['distro'] == distro:
                    addFlag = True
                    for package in sharedRuntime['userPackages']:
                        if package['name'] == packageName and \
                           package['arch'] == arch and \
                           package['owner'] == self.__userName:
                            # If package is present for the current user, update action
                            if "installed_version" in pkgData and pkgData["installed_version"]!="N/A":
                                package['action'] = action
                                addFlag = False
                            break
                    if addFlag == True:
                        sharedRuntime['userPackages'].append({"owner":self.__userName,
                        "name":packageName, "version":packageVersion, "arch":arch,
                        "action":action, "type": packageType})

        # Write back to the local managed list file
        localPath = self.putLocalData(localManagedListFileData, "")

    # Synchronize and commit the managed list in shared location with the changes done in local list
    def synchManagedPackageList(self):
        if globals.allocBuildServers:
            sharedPath = "/user/" + self.__userName + "/"
        else:
            sharedPath = ""

        localData = self.getLocalData("ManagedList.json")
        sharedData = self.getSharedData("ManagedList.json", sharedPath)

        if not sharedData:
            data = localData
        else:
            data = self.mergeManagedLists(localData, sharedData)

        path = self.putSharedData(localData, sharedData, sharedPath)

        return path

    # Merges the local and shared Managed Lists, taking the static data from
    # shared and merging the userPackages from both locations
    def mergeManagedLists(self, localData, sharedData):
        mergedData = sharedData

        for localRuntime in localData['managedRuntime']:
            for sharedRuntime in mergedData['managedRuntime']:
                if localRuntime['distro'] == sharedRuntime['distro']:
                    if localRuntime['distroVersion'] == sharedRuntime['distroVersion']:
                        # For each userPackage in localData belonging to the current user, iterate over
                        # the shared userPackages and if no match is found append it. In case a match
                        # is found with difference in versions, use the version from localData
                        for localPackage in localRuntime['userPackages']:
                            if localPackage['owner'] == self.__userName:
                                addLocalPackage = True
                                for sharedPackage in sharedRuntime['userPackages']:
                                    if localPackage['name'] == sharedPackage['name'] and \
                                       localPackage['owner'] == sharedPackage['owner']:
                                        if localPackage['version'] != sharedPackage['version']:
                                            sharedPackage['version'] = localPackage['version']
                                        addLocalPackage = False
                                        break
                                if addLocalPackage == True:
                                    sharedRuntime['userPackages'].append(localPackage)
                        # For each userPackage in sharedData belonging to the current user, iterate over
                        # the local userPackages and remove the ones present in shared but not in localData.
                        # This is the case when user has removed a previously added and synched package
                        # from the UI but not done a re-synch.
                        for sharedPackage in sharedRuntime['userPackages']:
                            if sharedPackage['owner'] == self.__userName:
                                removePackage = True
                                for localPackage in localRuntime['userPackages']:
                                    if sharedPackage['owner'] == localPackage['owner'] and \
                                       sharedPackage['name'] == localPackage['name'] and \
                                       sharedPackage['version'] == localPackage['version']:
                                        removePackage = False
                                        break
                                if removePackage == True:
                                    sharedRuntime['userPackages'].remove(sharedPackage)

        return mergedData
