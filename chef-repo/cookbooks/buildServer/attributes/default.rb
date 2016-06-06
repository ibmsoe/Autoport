# This file defines the attributes that are used by the recipes in the cookbook.
# Each package(archive) has an associated set of data values which are defined in
# terms of attributes.
# Following are common set of attributes defined for each package:
# NOTE: <pkg-identifier>: This string maps to package name in autoportChefPackages section of ManagedList.json.
# 1. default['buildServer'][<pkg-identifier>]['version']
#    - This specifies the version of the package(archive).
#      There is a default value specified however, this gets overridden at runtime based on ManagedList.json
#      or based on user selection on the single panel.
#      Specifying default is not mandatory. Default values would allow recipes as standalone.
#      Also it ensures that there is a value always available to fallback in case of any errors during overriding.
# 2. default['buildServer'][<pkg-identifier>]['install_dir']
#     - This specifies the path where the package(archive) is installed. By default all the packages
#       are installed in /opt or in subdirectories of /opt. This never gets overridden as there is no provision to change
#       default installation location via autoport tool at runtime.
# 3. default['buildServer'][<pkg-identifier>]['ext']
#     - This specifies the archive ext. There is a default value specified.
#       This value gets overridden at runtime based on package(archive) selected during installation
#       by the user. The default value for the ext is mandatory, since during the synch operation
#       the package ext is not available either via ManagedList.json or via user selection.


# Attributes related to custom repository where rpms, debs and archive files
# are hosted.

default['repo_name'] = ''
default['repo_hostname'] = ''
default['log_location'] = ''
default['buildServer']['repo_url'] = "http://#{node['repo_hostname']}/#{node['repo_name']}"

#Common download location for all the archive files
default['buildServer']['download_location'] =  Chef::Config[:file_cache_path]

# Attributes for protobuf
default['buildServer']['protobuf']['version'] = '2.6.1'
default['buildServer']['protobuf']['install_prefix'] = '/usr/local/protobuf'
default['buildServer']['protobuf']['source_dir'] = '/opt'
default['buildServer']['protobuf']['ext'] = ''

# Attributes for java
default['buildServer']['openjdk']['version'] = ['7']

# Attributes for ibm-java
default['buildServer']['ibm-java-sdk']['version'] = []
default['buildServer']['ibm-java-sdk']['install_dir'] = '/opt/ibm'

# Attributes for apache-ant
default['buildServer']['apache-ant']['source_install'] = 'false'
default['buildServer']['apache-ant']['version'] = '1.9.6'
default['buildServer']['apache-ant']['install_dir'] = '/opt'
default['buildServer']['apache-ant']['ext'] = ''

# Attributes for apache-maven
default['buildServer']['apache-maven']['source_install'] = 'false'
default['buildServer']['apache-maven']['version'] = '3.0.5'
default['buildServer']['apache-maven']['install_dir'] = '/opt'
default['buildServer']['apache-maven']['ext'] = ''

# Attributes for gradle
default['buildServer']['gradle']['source_install'] = 'false'
default['buildServer']['gradle']['version'] = '1.12'
default['buildServer']['gradle']['install_dir'] = '/opt'
default['buildServer']['gradle']['ext'] = ''

# Attributes for ibm-nodejs
default['buildServer']['ibm-sdk-nodejs']['packages'] = {}
default['buildServer']['ibm-sdk-nodejs']['install_dir'] = '/opt/ibm'

# Attributes for scala
default['buildServer']['scala']['source_install'] = 'false'
default['buildServer']['scala']['version'] = '2.9.2'
default['buildServer']['scala']['install_dir'] = '/opt'
default['buildServer']['scala']['ext'] = ''

# Attributes for perl and perl modules
default['buildServer']['perl']['version'] = '5.20.2'
default['buildServer']['perl']['ext'] = ''
default['buildServer']['perl']['extract_location'] = '/opt/perl_modules'
default['buildServer']['perl']['prefix_dir'] = '/usr/local/perl'
default['buildServer']['perl_modules']= {}
default['buildServer']['YAML-Tiny']['version']      = '1.64'
default['buildServer']['YAML-Tiny']['ext']          = ''
default['buildServer']['Test-Strict']['version']    = '0.26'
default['buildServer']['Test-Strict']['ext']        = ''
default['buildServer']['Strict-Perl']['version']    = '2014.10'
default['buildServer']['Strict-Perl']['ext']        = ''
default['buildServer']['File-Remove']['version']    = '1.52'
default['buildServer']['File-Remove']['ext']        = ''
default['buildServer']['Module-Install']['version'] = '1.14'
default['buildServer']['Module-Install']['ext']     = ''


# Attributes for python and python modules
default['buildServer']['python']['extract_location']  = '/opt/python_modules'
default['buildServer']['python_modules']= {}
# Attributes specific for each python module
default['buildServer']['py']['version']      = '1.4.26'
default['buildServer']['py']['ext']          = ''
default['buildServer']['pytest']['version']  = '2.6.4'
default['buildServer']['pytest']['ext']      = ''

# Attributes for userpackages
default['buildServer']['userpackages']={}
default['buildServer']['debs']={}
default['buildServer']['rpms']={}

# Attributes for power advance toolchain
default['at']['version']='9.0'

