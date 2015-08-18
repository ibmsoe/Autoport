# This recipe is used to install gradle package , either via binary source or via package manager.
# It also sets gradle_home using gradle.sh in profile.d.
# The pre-requiste to install gradle is to configure java environment.
# By default node attribute 'source_install' is to false.
# Default behaviour is to install gradle using package manager on ubuntu and via tarball on rhel.
# If we need to install it via archive file over other distros and arch, override 'source_install' attribute to 'true'

include_recipe 'buildServer::java'
distro = node['platform']
src_install = node['buildServer']['gradle']['source_install']

if distro == 'redhat' || src_install == 'true'
  include_recipe 'buildServer::gradle_binary'
else
  opt = ''
  opt = '--force-yes' if distro == 'ubuntu'

  gradle_basedir = '/usr/share/gradle'

  package 'gradle' do
    action :upgrade
    options opt
  end

  template '/etc/profile.d/gradle.sh' do
    owner 'root'
    group 'root'
    source 'gradle_source.sh.erb'
    mode '0644'
    variables(
      gradle_home: gradle_basedir
    )
  end
end
