# This recipe is used to install maven package , either via binary source or via package manager.
# It also sets maven_home using maven.sh in profile.d.
# The pre-requiste to install maven is to configure java environment.
# By default node attribute 'source_install' is to false.
# Default behaviour is to install maven using package manager , except over x_86 rhel nodes
# where installation is done via tarball.
# If we need to install it via archive file over other distros and arch, override 'source_install' attribute to 'true'

include_recipe 'buildServer::java'
arch  = node['kernel']['machine']
distro = node['platform']
src_install = node['buildServer']['apache-maven']['source_install']
opt = ''
opt = '--force-yes' if distro == 'ubuntu'

if (distro == 'redhat') || src_install == 'true'
  include_recipe 'buildServer::maven_binary'
else
  maven_basedir = '/usr/share/maven'

  package 'maven' do
    action :upgrade
    options opt
  end

  template '/etc/profile.d/maven.sh' do
    owner 'root'
    group 'root'
    source 'maven.sh.erb'
    mode '0644'
    variables(
      maven_home: maven_basedir
    )
  end
end
