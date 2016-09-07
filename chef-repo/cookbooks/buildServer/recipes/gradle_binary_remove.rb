# Recipe would uninstall/remove gradle package installed via binary source.

include_recipe 'buildServer::get_log'

version      = node['buildServer']['gradle']['version']
install_dir  = node['buildServer']['gradle']['install_dir']
install_path = "#{install_dir}/packages/gradle"
ext          = node['buildServer']['gradle']['ext']
gradle_pkg   = "gradle-#{version}-bin#{ext}"
archive_dir  = node['buildServer']['download_location']
gradle_home  = "#{install_dir}/gradle"
arch         = node['kernel']['machine']

if ext.empty?
  ext = ArchiveLog.getExtension('gradle', version)
end

link gradle_home do
  action :delete
  ignore_failure true
end

[
  "#{install_path}/gradle-#{version}",
].each do |pkg|
  directory pkg do
    action :delete
    recursive true
    ignore_failure true
  end
end

file "#{archive_dir}/#{gradle_pkg}" do
  action :delete
  ignore_failure true
end

file '/etc/profile.d/gradle.sh' do
  action :delete
  ignore_failure true
  only_if "grep -w #{version} /etc/profile.d/gradle.sh"
end

buildServer_log 'gradle' do
  name         'gradle'
  log_location node['log_location']
  log_record   "gradle,#{version},gradle_binary,gradle,#{arch},#{ext},#{gradle_pkg}"
  action       :remove
  ignore_failure true
end
