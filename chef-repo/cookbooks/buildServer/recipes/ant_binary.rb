# This recipe installs ant via tarball hosted over the autoport repository.
# Pre-requiste is to install java.
# This recipe also sets ant_home and sets default path variable for ant.

Chef::Recipe.send(:include, CommandBuilder)
include_recipe 'buildServer::java'

version       = node['buildServer']['apache-ant']['version']
install_dir   = node['buildServer']['apache-ant']['install_dir']
ant_pkg       = "apache-ant-#{version}"
extension     = node['buildServer']['apache-ant']['extension']
archive_dir   = node['buildServer']['download_location']
ant_home      = "#{install_dir}/#{ant_pkg}"
repo_url      = node['buildServer']['repo_url']


remote_file "#{archive_dir}/#{ant_pkg}-bin#{extension}" do
  source "#{repo_url}/archives/#{ant_pkg}-bin#{extension}"
  owner 'root'
  group 'root'
  action :create
  mode '0644'
end

execute "Extracting ant #{version}" do
  cwd install_dir
  user 'root'
  group 'root'
  command <<-EOD
    #{CommandBuilder.command(extension, run_context)} #{archive_dir}/#{ant_pkg}-bin#{extension}
  EOD
  creates "#{install_dir}/#{ant_pkg}"
end

template '/etc/profile.d/ant.sh' do
  owner 'root'
  group 'root'
  source 'ant_source.sh.erb'
  mode '0644'
  variables(
    ant_home: ant_home
  )
end

buildServer_log "apache-ant" do
  name         "apache-ant"
  log_location node['log_location']
  log_record   "apache-ant,#{version},ant_binary,ant,#{ant_pkg}-bin#{extension}"
  action       :add
end
