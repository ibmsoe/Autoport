# This recipe is used to install "R"
# "R" runtime is directly available over ubuntu 14.04 via package manager
# "R" will be installed on RHEL/CentOS using source/build method

distro = node['platform']
src_install = node['buildServer']['R']['source_install']

if [ 'redhat', 'centos' ].include?(distro) || src_install == 'true'
  include_recipe 'buildServer::r_source'
elsif distro == 'ubuntu'
  opt = '--force-yes'
  package 'r-base' do
    action :upgrade
    options opt
    ignore_failure true
  end
end

