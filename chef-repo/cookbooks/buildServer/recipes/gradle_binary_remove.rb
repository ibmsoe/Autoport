# Recipe would uninstall/remove gradle package installed via binary source.

version      = node['buildServer']['gradle']['version']
install_dir  = node['buildServer']['gradle']['install_dir']
install_path = "#{install_dir}/packages/gradle"
extension    = node['buildServer']['gradle']['extension']
gradle_pkg   = "gradle-#{version}-bin#{extension}"
archive_dir  = node['buildServer']['download_location']
gradle_home  = "#{install_dir}/gradle"

link gradle_home do
  action :delete
end

[
  "#{install_dir}/packages",
  "#{install_path}/gradle-#{version}",
  install_path
].each do |pkg|
  directory pkg do
    action :delete
    recursive true
  end
end

file "#{archive_dir}/#{gradle_pkg}" do
  action :delete
end

file '/etc/profile.d/gradle.sh' do
  action :delete
end

buildServer_log 'gradle' do
  name         'gradle'
  log_location node['log_location']
  log_record   "gradle,#{version},gradle_binary,gradle,#{gradle_pkg}"
  action       :remove
end
