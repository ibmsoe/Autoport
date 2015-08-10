# Attributes related to custom repository where rpms, debs and archive files
# are hosted.
default['repo_name'] = ''
default['repo_hostname'] = ''
default['log_location'] = ''
default['buildServer']['repo_url'] = "http://#{node['repo_hostname']}/#{node['repo_name']}"

#Common download location for all the source files
default['buildServer']['download_location'] =  Chef::Config[:file_cache_path]

# Attributes for protobuf
default['buildServer']['protobuf']['version'] = '2.6.1'
default['buildServer']['protobuf']['install_prefix'] = '/usr/local'
default['buildServer']['protobuf']['source_dir'] = '/opt'

# Attributes for java
default['buildServer']['java']['version'] = '7'

# Attributes for ibm-java
default['buildServer']['ibm-java']['version'] = ''
default['buildServer']['ibm-java']['install_dir'] = '/opt'

# Attributes for apache-ant
default['buildServer']['apache-ant']['source_install'] = 'false'
default['buildServer']['apache-ant']['version'] = '1.9.3'
default['buildServer']['apache-ant']['install_dir'] = '/opt'

# Attributes for apache-maven
default['buildServer']['apache-maven']['source_install'] = 'false'
default['buildServer']['apache-maven']['version'] = '3.0.5'
default['buildServer']['apache-maven']['install_dir'] = '/opt'

# Attributes for gradle
default['buildServer']['gradle']['source_install'] = 'false'
default['buildServer']['gradle']['version'] = '1.12'
default['buildServer']['gradle']['install_dir'] = '/opt'

# Attributes for nodejs
default['buildServer']['nodejs']['version'] = '0.10.38'
default['buildServer']['nodejs']['install_dir'] = '/opt'

# Attributes for scala
default['buildServer']['scala']['source_install'] = 'false'
default['buildServer']['scala']['version'] = '2.9.2'
default['buildServer']['scala']['install_dir'] = '/opt'

# Attributes for perl and perl modules
default['buildServer']['perl']['version'] = '5.20.2'
default['buildServer']['perl']['extract_location'] = '/opt/perl_modules'
default['buildServer']['perl']['prefix_dir'] = '/usr/local/perl'
default['buildServer']['perl_modules']= {}
default['buildServer']['YAML-Tiny']['version']      = '1.64'
default['buildServer']['Test-Strict']['version']    = '0.26'
default['buildServer']['Strict-Perl']['version']    = '2014.10'
default['buildServer']['File-Remove']['version']    = '1.52'
default['buildServer']['Module-Install']['version'] = '1.14'


# Attributes for python and python modules
default['buildServer']['python']['extract_location']  = '/opt/python_modules'
default['buildServer']['python_modules']= {}
# Attributes specific for each python module
default['buildServer']['py']['version']      = '1.4.26'
default['buildServer']['pytest']['version']  = '2.6.4'

# Attributes for userpackages
default['buildServer']['userpackages']={}
default['buildServer']['debs']={}
default['buildServer']['rpms']={}
