# Recipe would uninstall/remove ant package installed via binary source

version       = node['buildServer']['apache-ant']['version']
install_dir   = node['buildServer']['apache-ant']['install_dir']
ant_pkg       = "apache-ant-#{version}"
archive_dir   = node['buildServer']['download_location']
extension     = node['buildServer']['apache-ant']['extension']

file "#{archive_dir}/#{ant_pkg}-bin#{extension}" do
   action :delete
end

directory "#{install_dir}/#{ant_pkg}" do
  action     :delete
  recursive  true
end

file "/etc/profile.d/ant.sh" do
  action :delete
end

buildServer_log "apache-ant" do
  name         "apache-ant"
  log_location node['log_location']
  log_record   "apache-ant,#{version},ant_binary,ant,#{ant_pkg}-bin#{extension}"
  action       :remove
end
