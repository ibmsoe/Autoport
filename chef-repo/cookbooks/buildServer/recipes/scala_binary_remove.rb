# Recipe would uninstall/remove scala package installed via binary source

version       = node['buildServer']['scala']['version']
install_dir   = node['buildServer']['scala']['install_dir']
scala_pkg     = "scala-#{version}"
ext           = node['buildServer']['scala']['ext']
archive_dir   = node['buildServer']['download_location']
arch          = node['kernel']['machine']

file "#{archive_dir}/#{scala_pkg}#{ext}" do
  action :delete
end

directory "#{install_dir}/#{scala_pkg}" do
  action :delete
  recursive true
end

file '/etc/profile.d/scala.sh' do
  action :delete
  only_if "grep -w #{version} /etc/profile.d/scala.sh"
end

buildServer_log 'scala' do
  name         'scala'
  log_location node['log_location']
  log_record   "scala,#{version},scala_binary,scala,#{arch},#{ext},#{scala_pkg}#{ext}"
  action       :remove
end
