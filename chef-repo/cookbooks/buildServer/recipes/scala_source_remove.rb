# Recipe would uninstall/remove scala package installed via binary source

version       = node['buildServer']['scala']['version']
install_dir   = node['buildServer']['scala']['install_dir']
scala_pkg    = "scala-#{version}"
archive_dir   = node['buildServer']['download_location']

file "#{archive_dir}/#{scala_pkg}.tgz" do
  action :delete
end

directory "#{install_dir}/#{scala_pkg}" do
  action :delete
  recursive true
end

file '/etc/profile.d/scala.sh' do
  action :delete
end

buildServer_log 'scala' do
  name         'scala'
  log_location node['log_location']
  log_record   "scala,#{version},scala_source,scala"
  action       :remove
end
