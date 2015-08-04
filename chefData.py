import globals
from flask import json
from collections import OrderedDict

class ChefData:
    def __init__(self, repoHost):
        self.__repo_hostname = repoHost + ":90"
        self.__repo_name = 'autoport_repo'
        self.__localDataDir = globals.localPathForConfig
        self.__logDir = '/var/opt/autoport/'

    def setChefDataForSynch(self, distro, distroVersion):
        # This routine in called during synch, to fill up
        # the chef-attributes (package/versions) based on
        # ManagedList.json

        # DataStructure to hold chefRecipes and chefAttributes
        # as per ManagedList.json
        chefRecipes = []
        chefAttrs = {}
        chefAttrs['buildServer'] = {}

        # These will hold os-install pacakages (autoportPackages).
        chefAttrs['buildServer']['debs'] = {}
        chefAttrs['buildServer']['rpms'] = {}
        chefAttrs['buildServer']['userpackages'] = {}

        chefAttrs['repo_hostname'] = self.__repo_hostname
        chefAttrs['repo_name'] = self.__repo_name
        chefAttrs['log_location'] = self.__logDir
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
                    chefRecipes = ["recipe[buildServer::default]"]

                    # Filling in autoportPackages (os-installs) per distro.
                    for pkg in runtime['autoportPackages']:
                        if distro == 'UBUNTU':
                            key = 'debs'
                        elif distro == 'RHEL':
                            key = 'rpms'
                        pkgKey = pkg['name']
                        if 'version' in pkg:
                            chefAttrs['buildServer'][key][pkgKey] = pkg['version']
                        else:
                            chefAttrs['buildServer'][key][pkgKey] = ''
                    # Filling in autoportChefPackages
                    for pkg in runtime['autoportChefPackages']:
                        if 'version' in pkg:
                            pkgKey = pkg['name']
                            chefAttrs['buildServer'][pkgKey] = {}
                            chefAttrs['buildServer'][pkgKey]['version'] = pkg['version']

                    # Filling in userpackages based on current owner
                    # This would change when ManagedList.json will be mainatined
                    # per user.
                    for pkg in runtime['userPackages']:
                        if pkg['owner'] == globals.localHostName:
                            if not pkg['type']:
                                userPackage = {
                                                pkg['name'] : [
                                                                pkg['arch'],
                                                                pkg['version'],
                                                                pkg['action']
                                                              ]
                                              }
                                chefAttrs['buildServer']['userpackages'].update(userPackage)
                            else:
                                # If a userpackage has a type associated, it signifies
                                # that it is a source install.We need to populate appropriate
                                # chef-attributes and extend default run_list with recipe mapped to
                                # the particular user pacakge.
                                chefAttrs, recipe = self.setChefDataForPackage(pkg['name'],
                                                        pkg['version'], pkg['type'], chefAttrs)
                                chefRecipes.extend(recipe)
            return chefAttrs, chefRecipes
        except KeyError as e:
            print str(e)
            assert(False)

    def setChefDataForPackage(self, name, version, type, attributes = {}):
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
        else:
            attribute = name
            chefAttrs['buildServer'][attribute] = {'version': version}

        chefRecipes = ["recipe[buildServer::" + type.lower() + "]"]
        return chefAttrs, chefRecipes
