# This recipe installs gradle via tarball hosted over the autoport repository.
# Pre-requiste is to install java.
# This recipe also sets gradle_home and sets default path variable for gradle.

Chef::Recipe.send(:include, CommandBuilder)
Chef::Recipe.send(:include, ArchiveLog)

version      = node['buildServer']['gradle']['version']
install_dir  = node['buildServer']['gradle']['install_dir']
install_path = "#{install_dir}/packages/gradle"
ext          = node['buildServer']['gradle']['ext']
archive_dir  = node['buildServer']['download_location']
repo_url     = node['buildServer']['repo_url']
arch         = node['kernel']['machine']

if ext.empty?
  ext = ArchiveLog.getExtension('gradle', version)
end

gradle_pkg   = "gradle-#{version}-bin#{ext}"

include_recipe 'buildServer::java'

[
  "#{install_dir}/packages",
  install_path
].each do |pkg|
  directory pkg do
    mode '0755'
    owner 'root'
    group 'root'
    action :create
    ignore_failure true
  end
end

remote_file "#{archive_dir}/#{gradle_pkg}" do
  source "#{repo_url}/archives/#{gradle_pkg}"
  owner 'root'
  group 'root'
  action :create
  mode   '0755'
  ignore_failure true
end

bash 'Extracting the archive' do
  user 'root'
  cwd install_path
  code <<-EOD
    #{CommandBuilder.command(ext, run_context)} #{archive_dir}/#{gradle_pkg}
  EOD
  creates "#{install_path}/gradle-#{version}/bin/gradle"
  ignore_failure true
  only_if { File.exist?("#{archive_dir}/#{gradle_pkg}") }
end

template '/etc/profile.d/gradle.sh' do
  source 'gradle_source.sh.erb'
  owner 'root'
  group 'root'
  mode '0644'
  variables(
    gradle_home: "#{install_path}/gradle-#{version}"
  )
  ignore_failure true
  only_if { Dir.exist?("#{install_path}/gradle-#{version}") }
end

buildServer_log 'gradle' do
  name         'gradle'
  log_location node['log_location']
  log_record   "gradle,#{version},gradle_binary,gradle,#{arch},#{ext},#{gradle_pkg}"
  action       :add
  ignore_failure true
  only_if { Dir.exist?("#{install_path}/gradle-#{version}") }
end
