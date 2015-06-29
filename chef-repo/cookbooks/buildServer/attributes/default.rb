# Attributes related to custom repository where rpms, debs and archive files
# are hosted.
default['buildServer']['repo_name'] = 'autoport_repo'
default['buildServer']['node_ip'] = 'soe-test1.aus.stglabs.ibm.com'
default['buildServer']['repo_url'] = "http://#{node['buildServer']['node_ip']}/#{node['buildServer']['repo_name']}"

# Attributes for protobuf
default['buildServer']['pbuf']['version'] = '2.6.1'
default['buildServer']['pbuf']['install_prefix'] = '/usr/local'
default['buildServer']['pbuf']['download_location'] = Chef::Config[:file_cache_path]
default['buildServer']['pbuf']['source_dir'] = '/opt'

# Attributes for java
default['buildServer']['java']['version'] = '7'

# Attributes for ant
default['buildServer']['ant']['source_install'] = 'false'
default['buildServer']['ant']['version'] = '1.9.3'
default['buildServer']['ant']['install_dir'] = '/opt'
default['buildServer']['ant']['download_location'] = Chef::Config[:file_cache_path]

# Attributes for maven
default['buildServer']['maven']['source_install'] = 'false'
default['buildServer']['maven']['version'] = '3.0.5'
default['buildServer']['maven']['install_dir'] = '/opt'
default['buildServer']['maven']['download_location'] = Chef::Config[:file_cache_path]

# Attributes for gradle
default['buildServer']['gradle']['source_install'] = 'false'
default['buildServer']['gradle']['version'] = '1.12'
default['buildServer']['gradle']['download_location'] = Chef::Config[:file_cache_path]
default['buildServer']['gradle']['install_dir'] = '/opt'

# Attributes for nodejs
default['buildServer']['nodejs']['source_install'] = 'false'
default['buildServer']['nodejs']['version'] = '0.12.4'
default['buildServer']['nodejs']['download_location'] = Chef::Config[:file_cache_path]
default['buildServer']['nodejs']['install_dir'] = '/usr/local/src'

# Attributes for nodejs-ppc
default['buildServer']['nodejs-ppc']['version'] = '0.10.38'
default['buildServer']['nodejs-ppc']['download_location'] = Chef::Config[:file_cache_path]
default['buildServer']['nodejs-ppc']['install_dir'] = '/opt'

# Attributes for scala
default['buildServer']['scala']['source_install'] = 'false'
default['buildServer']['scala']['version'] = '2.9.2'
default['buildServer']['scala']['download_location'] = Chef::Config[:file_cache_path]
default['buildServer']['scala']['install_dir'] = '/opt'
