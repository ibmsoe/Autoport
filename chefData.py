import globals
from flask import json
from collections import OrderedDict

class ChefData:
    def __init__(self, repoHost):
        self.__repo_hostname = repoHost + ":90"
        self.__repo_name = 'autoport_repo'
        self.__localDataDir = globals.localPathForConfig
        self.__logDir = globals.localTarRepoLocation

    def setRepoHost(self, repoHost):
        self.__repo_hostname = repoHost + ":90"

    def setChefDataForSynch(self, distro, distroVersion, arch):
        # This routine in called during synch, to fill up
        # the chef-attributes (package/versions) based on
        # ManagedList.json

        # DataStructure to hold chefRecipes and chefAttributes
        # as per ManagedList.json
        chefInstallRecipes = []
        chefRemoveRecipes = []
        chefInstallAttrs = {}
        chefRemoveAttrs = {}
        chefInstallAttrs['buildServer'] = {}

        # These will hold os-install pacakages (autoportPackages).
        chefInstallAttrs['buildServer']['debs'] = {}
        chefInstallAttrs['buildServer']['rpms'] = {}
        chefInstallAttrs['buildServer']['userpackages'] = {}

        chefInstallAttrs['repo_hostname'] = self.__repo_hostname
        chefInstallAttrs['repo_name'] = self.__repo_name
        chefInstallAttrs['log_location'] = self.__logDir
        numberOfInstalls = 0
        numberOfUnInstalls = 0
        # Reading ManagedList.json
        try:
            localPath = self.__localDataDir + "ManagedList.json"
            f = open(localPath)
            dataStr = json.load(f, object_pairs_hook=OrderedDict)
            f.close
        except IOError as e:
            print str(e)
            assert(False)

        # Filling up chef attributes and chef run_list from ManagedList
        # based on distro and release.
        try:
            for runtime in dataStr['managedRuntime']:
                if (runtime['distro'] == distro) and (runtime['distroVersion'] == distroVersion):
                    # Filling up chef run_list at the time of synch.
                    # On synch all the recipes mapped to the pacakges in the
                    # ManagedList.json needs to be run.
                    # In expression "recipe[buildServer::default]"
                    # 'buildserver' is the cookbook name and 'default'
                    # is the recipe name.
                    # 'default' is a wrapper recipe which calls rest of all recipes
                    # in the 'buildServer' cookbook
                    chefInstallRecipes = ["recipe[buildServer::default]"]

                    # Filling in autoportPackages (os-installs) per distro.
                    for pkg in runtime['autoportPackages']:
                        if distro in ('UBUNTU', 'Debian'):
                            key = 'debs'
                        elif distro in ('RHEL', 'Fedora', 'openSUSE', 'AIX'):
                            key = 'rpms'
                        pkgKey = pkg['name']
                        numberOfInstalls = numberOfInstalls + 1
                        if 'version' in pkg:
                            chefInstallAttrs['buildServer'][key][pkgKey] = pkg['version']
                        else:
                            chefInstallAttrs['buildServer'][key][pkgKey] = ''
                    # Filling in autoportChefPackages
                    for pkg in runtime['autoportChefPackages']:
                        if 'version' in pkg:
                            if 'tag' in pkg and pkg['tag'] == "ibm-sdk-nodejs":
                                pkgKey = 'ibm-sdk-nodejs'
                                chefInstallAttrs['buildServer'][pkgKey] = {}
                                chefInstallAttrs['buildServer'][pkgKey]['name'] = pkg['name']
                            else:
                                pkgKey = pkg['name']
                                chefInstallAttrs['buildServer'][pkgKey] = {}
                            chefInstallAttrs['buildServer'][pkgKey]['version'] = pkg['version']
                            numberOfInstalls = numberOfInstalls + 1

                    # Filling in userpackages based on current owner
                    # This would change when ManagedList.json will be maintained
                    # per user.
                    for pkg in runtime['userPackages']:
                        if pkg['owner'] == globals.configUsername:
                            if not pkg['type'] and pkg['arch'] == arch:
                                userPackage = {
                                                pkg['name'] : [
                                                                pkg['arch'],
                                                                pkg['version'],
                                                                pkg['action']
                                                              ]
                                              }
                                chefInstallAttrs['buildServer']['userpackages'].update(userPackage)
                                if pkg['action'] == 'install':
                                    numberOfInstalls = numberOfInstalls + 1
                                if pkg['action'] == 'remove':
                                    numberOfUnInstalls = numberOfUnInstalls + 1
                            else:
                                # If a userpackage has a type associated, it signifies
                                # that it is a source install.We need to populate appropriate
                                # chef-attributes and extend default run_list with recipe mapped to
                                # the particular user package.
                                if pkg['action'] == 'install' and pkg['arch'] == arch:
                                    chefInstallAttrs, recipe = self.setChefDataForPackage(pkg['name'],
                                                     pkg['version'], pkg['type'], \
                                                     pkg['action'], pkg['extension'], \
                                                     chefInstallAttrs)
                                    chefInstallRecipes.extend(recipe)
                                    numberOfInstalls = numberOfInstalls + 1
                                elif pkg['action'] == 'remove' and pkg['arch'] == arch:
                                     chefRemoveAttrs, recipe = self.setChefDataForPackage(pkg['name'],
                                                     pkg['version'], pkg['type'], \
                                                     pkg['action'], pkg['extension'], \
                                                     chefRemoveAttrs)
                                     chefRemoveRecipes.extend(recipe)
                                     numberOfUnInstalls = numberOfUnInstalls + 1

            chefAttr = [chefInstallAttrs, chefRemoveAttrs]
            recipes  = [chefInstallRecipes, chefRemoveRecipes]

            return chefAttr,recipes,numberOfInstalls,numberOfUnInstalls
        except KeyError as e:
            print str(e)
            assert(False)

    def setChefDataForPackage(self, name, version, type, action, ext, attributes = {}):
        # This routine is responsible for setting up chef attributes that
        # and run list for a single specific package.
        # The version of the package is passed to this routine based
        # on user selection is not based on version in ManagedList.
        chefAttrs = attributes
        if not chefAttrs:
            chefAttrs['buildServer'] = {}
            chefAttrs['repo_hostname'] = self.__repo_hostname
            chefAttrs['repo_name'] = self.__repo_name
            chefAttrs['log_location'] = self.__logDir

        chefAttrs['buildServer']['perl_modules'] = {}
        chefAttrs['buildServer']['python_modules'] = {}

        if type in ['perl_modules', 'python_modules']:
            name = name
            chefAttrs['buildServer'][type].update({name: version})
        elif type == 'ibm-sdk-nodejs':
            chefAttrs['buildServer'][type] = {'name': name}
            chefAttrs['buildServer'][type].update({'version': version})
        else:
            attribute = name
            chefAttrs['buildServer'][attribute] = {'version': version}
            chefAttrs['buildServer'][attribute].update({'ext': ext})

        if action == 'remove' and type not in ['perl_modules', 'python_modules']:
           type = type.lower() + "_remove"
           chefRecipes = ["recipe[buildServer::" + type + "]"]
        else:
            chefRecipes = ["recipe[buildServer::" + type.lower() + "]"]
        return chefAttrs, chefRecipes
