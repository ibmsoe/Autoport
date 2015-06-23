# Installs scala using source/build method on ppc64le rhel node.
# On rest of the nodes it is installed using package manager.
# scala deb and rpm are hosted over autoport_repo.

include_recipe 'buildServer::java'
arch  = node['kernel']['machine']
distro = node['platform']
src_install = node['scala']['source_install']

if (arch == 'ppc64le' && distro == 'rhel') || src_install == 'true'
  include_recipe 'buildServer::scala_source'
else
  package 'scala' do
    action :install
    options '--force-yes'
  end
end
