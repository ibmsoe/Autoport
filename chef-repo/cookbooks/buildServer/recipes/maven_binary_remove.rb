# Recipe would uninstall/remove maven package installed via binary source.

version       = node['buildServer']['apache-maven']['version']
install_dir   = node['buildServer']['apache-maven']['install_dir']
maven_pkg     = "apache-maven-#{version}"
extension     = node['buildServer']['apache-maven']['extension']
archive_dir   = node['buildServer']['download_location']

file "#{archive_dir}/#{maven_pkg}-bin#{extension}" do
   action :delete
end

directory "#{install_dir}/#{maven_pkg}" do
  action :delete
  recursive  true
end

file "/etc/profile.d/maven.sh" do
  action :delete
end

buildServer_log "apache-maven" do
  name         "apache-maven"
  log_location node['log_location']
  log_record   "apache-maven,#{version},maven_binary,maven,#{maven_pkg}-bin#{extension}"
  action       :remove
end
