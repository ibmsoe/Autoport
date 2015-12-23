# This recipe is a wrapper, which takes care of installing openjdk and ibm-java.
# It also creates a generic java.sh file in order to set JAVA_HOME and add it to PATH settings.

if node['buildServer']['openjdk']['version'].any?
   default_version = node['buildServer']['openjdk']['version'][0]
end

install_dir = node['buildServer']['ibm-java-sdk']['install_dir']

include_recipe 'buildServer::openjdk'
include_recipe 'buildServer::ibm-java-sdk'

template '/etc/profile.d/java.sh' do
  owner 'root'
  group 'root'
  source 'java.sh.erb'
  mode '0644'
  variables(
    version: default_version,
    install_dir: install_dir,
    type: 'openjdk'
  )
  only_if { default_version }
  ignore_failure true
end
