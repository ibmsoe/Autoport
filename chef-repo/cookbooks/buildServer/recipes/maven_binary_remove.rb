# Recipe would uninstall/remove maven package installed via binary source.

include_recipe 'buildServer::get_log'

version       = node['buildServer']['apache-maven']['version']
install_dir   = node['buildServer']['apache-maven']['install_dir']
maven_pkg     = "apache-maven-#{version}"
ext           = node['buildServer']['apache-maven']['ext']
archive_dir   = node['buildServer']['download_location']
arch          = node['kernel']['machine']

if ext.empty?
  ext = ArchiveLog.getExtension('apache-maven', version)
end

file "#{archive_dir}/#{maven_pkg}-bin#{ext}" do
   action :delete
   ignore_failure true
end

directory "#{install_dir}/#{maven_pkg}" do
  action :delete
  recursive  true
  ignore_failure true
end

file "/etc/profile.d/maven.sh" do
  action :delete
  ignore_failure true
  only_if "grep -w #{version} /etc/profile.d/maven.sh"
end

record = "apache-maven,#{version},maven_binary,maven,#{arch},#{ext},#{maven_pkg}-bin#{ext}"

buildServer_log "apache-maven" do
  name         "apache-maven"
  log_location node['log_location']
  log_record   record
  ignore_failure true
  action       :remove
end
