# Installs scala using binary source on ppc64le rhel node.
# On rest of the nodes it is installed using package manager.
# scala deb and rpm are hosted over autoport_repo.

arch  = node['kernel']['machine']
distro = node['platform']
src_install = node['buildServer']['scala']['source_install']
opt = ''
opt = '--force-yes' if distro == 'ubuntu'

if (arch == 'ppc64le' && [ 'redhat', 'centos' ].include?(distro)) || src_install == 'true'
  include_recipe 'buildServer::scala_binary'
else
  package 'scala' do
    action :upgrade
    options opt
    ignore_failure true
  end

  buildServer_log 'scala' do
    name         'scala'
    log_location node['log_location']
    log_record   "scala"
    action       :remove
    ignore_failure true
  end
end
