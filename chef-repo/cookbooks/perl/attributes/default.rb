# Attributes for perl

default['perl']['version'] = '5.20.2'  # downlaoded from http://www.perl.org/get.html#unix_like
default['perl']['download_location'] =  Chef::Config[:file_cache_path]
default['perl']['archive_location'] = '/opt/perl_modules'
default['perl']['prefix_dir'] = '/usr/local/perl'
default['perl']['repo_name'] = 'autoport_repo'
default['perl']['node_ip']  = 'soe-test1.aus.stglabs.ibm.com'
default['perl']['repo_url'] = "http://#{node['perl']['node_ip']}/#{node['perl']['repo_name']}/archives/"

# Attributes for  perl modules

default['perl']['yaml_tiny']['version']      = '1.64'
default['perl']['test-strict']['version']    = '0.26'
default['perl']['strict-perl']['version']    = '2014.10'
default['perl']['file-remove']['version']    = '1.52'
default['perl']['module-install']['version'] = '1.14'
