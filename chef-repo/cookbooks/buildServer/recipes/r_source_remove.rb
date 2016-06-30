# Recipe would uninstall/remove ant package installed via binary source

Chef::Recipe.send(:include, ArchiveLog)

version       = node['buildServer']['R']['version']
install_dir   = node['buildServer']['R']['install_dir']
r_pkg         = "R-#{version}"
archive_dir   = node['buildServer']['download_location']
ext           = node['buildServer']['R']['ext']
arch          = node['kernel']['machine']

if ext.empty?
  ext = ArchiveLog.getExtension('R', version)
end

file "#{archive_dir}/#{r_pkg}#{ext}" do
   action :delete
   ignore_failure true
end

file "/usr/local/bin/R" do
  action :delete
  ignore_failure true
end

directory "#{install_dir}/#{r_pkg}" do
  action     :delete
  recursive  true
  ignore_failure true
end

file "/etc/profile.d/R.sh" do
  action :delete
  only_if "grep -w #{version} /etc/profile.d/R.sh"
  ignore_failure true
end

buildServer_log "r_source" do
  name         "r_source"
  log_location node['log_location']
  log_record   "R,#{version},r_source,R,#{arch},#{ext},#{r_pkg}#{ext}"
  action       :remove
  ignore_failure true
end
