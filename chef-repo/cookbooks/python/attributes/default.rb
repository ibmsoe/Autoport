# Attributes common for python modules

default['python']['download_location'] =  Chef::Config[:file_cache_path]
default['python']['archive_location']  = '/opt/python_modules'
default['python']['repo_name'] = 'autoport_repo'
default['python']['node_ip']  = 'soe-test1.aus.stglabs.ibm.com'
default['python']['repo_url'] = "http://#{node['python']['node_ip']}/#{node['python']['repo_name']}/archives/"

# Attributes specific for each python module

default['python']['py']['version']      = '1.4.26'
default['python']['pytest']['version']  = '2.6.4'
