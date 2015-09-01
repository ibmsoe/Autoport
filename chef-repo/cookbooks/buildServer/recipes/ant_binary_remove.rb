# Recipe would uninstall/remove ant package installed via binary source

version       = node['buildServer']['apache-ant']['version']
install_dir   = node['buildServer']['apache-ant']['install_dir']
ant_pkg       = "apache-ant-#{version}"
archive_dir   = node['buildServer']['download_location']
ext           = node['buildServer']['apache-ant']['ext']
arch          = node['kernel']['machine']

file "#{archive_dir}/#{ant_pkg}-bin#{ext}" do
   action :delete
end

directory "#{install_dir}/#{ant_pkg}" do
  action     :delete
  recursive  true
end

file "/etc/profile.d/ant.sh" do
  action :delete
  only_if "grep -w #{version} /etc/profile.d/ant.sh"
end

buildServer_log "apache-ant" do
  name         "apache-ant"
  log_location node['log_location']
  log_record   "apache-ant,#{version},ant_binary,ant,#{arch},#{ext},#{ant_pkg}-bin#{ext}"
  action       :remove
end
