# This recipe installs ant via tarball hosted over the autoport repository.
# Pre-requiste is to install java.
# This recipe also sets ant_home and sets default path variable for ant.

Chef::Recipe.send(:include, CommandBuilder)
include_recipe 'buildServer::java'

version       = node['buildServer']['apache-ant']['version']
install_dir   = node['buildServer']['apache-ant']['install_dir']
ant_pkg       = "apache-ant-#{version}"
ext           = node['buildServer']['apache-ant']['ext']
archive_dir   = node['buildServer']['download_location']
ant_home      = "#{install_dir}/#{ant_pkg}"
repo_url      = node['buildServer']['repo_url']
arch          = node['kernel']['machine']

remote_file "#{archive_dir}/#{ant_pkg}-bin#{ext}" do
  source "#{repo_url}/archives/#{ant_pkg}-bin#{ext}"
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
    #{CommandBuilder.command(ext, run_context)} #{archive_dir}/#{ant_pkg}-bin#{ext}
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
  log_record   "apache-ant,#{version},ant_binary,ant,#{arch},#{ext},#{ant_pkg}-bin#{ext}"
  action       :add
end