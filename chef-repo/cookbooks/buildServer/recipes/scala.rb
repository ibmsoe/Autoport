# Installs scala using binary source on ppc64le rhel node.
# On rest of the nodes it is installed using package manager.
# scala deb and rpm are hosted over autoport_repo.

include_recipe 'buildServer::java'
arch  = node['kernel']['machine']
distro = node['platform']
src_install = node['buildServer']['scala']['source_install']
opt = ''
opt = '--force-yes' if distro == 'ubuntu'

if (arch == 'ppc64le' && distro == 'redhat') || src_install == 'true'
  include_recipe 'buildServer::scala_source'
else
  package 'scala' do
    action :upgrade
    options opt
  end
end
