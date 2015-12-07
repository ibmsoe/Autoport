# This recipe installs maven via tarball hosted over the autoport repository.
# Pre-requiste is to install java.
# This recipe also sets maven_home and sets default path variable for maven.

include_recipe 'buildServer::java'
Chef::Recipe.send(:include, CommandBuilder)

version       = node['buildServer']['apache-maven']['version']
install_dir   = node['buildServer']['apache-maven']['install_dir']
maven_pkg     = "apache-maven-#{version}"
ext           = node['buildServer']['apache-maven']['ext']
archive_dir   = node['buildServer']['download_location']
maven_home    = "#{install_dir}/#{maven_pkg}"
repo_url      = node['buildServer']['repo_url']
arch          = node['kernel']['machine']

remote_file "#{archive_dir}/#{maven_pkg}-bin#{ext}" do
  source "#{repo_url}/archives/#{maven_pkg}-bin#{ext}"
  owner 'root'
  group 'root'
  action :create
  mode '0644'
  ignore_failure true
end

execute "Extracting maven #{version}" do
  cwd install_dir
  user 'root'
  group 'root'
  command <<-EOD
    #{CommandBuilder.command(ext, run_context)} #{archive_dir}/#{maven_pkg}-bin#{ext}
  EOD
  ignore_failure true
  creates "#{install_dir}/#{maven_pkg}"
  only_if { File.exist?("#{archive_dir}/#{maven_pkg}-bin#{ext}") }
end

template '/etc/profile.d/maven.sh' do
  owner 'root'
  group 'root'
  source 'maven_source.sh.erb'
  mode '0644'
  variables(
    maven_home: maven_home
  )
  ignore_failure true
  only_if { Dir.exist?(maven_home) }
end

record = "apache-maven,#{version},maven_binary,maven,#{arch},#{ext},#{maven_pkg}-bin#{ext}"
buildServer_log "apache-maven" do
  name         "apache-maven"
  log_location node['log_location']
  log_record   record
  action       :add
  ignore_failure true
  only_if { Dir.exist?(maven_home) }
end
