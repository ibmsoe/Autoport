# Recipe would uninstall/remove scala package installed via binary source

Chef::Recipe.send(:include, ArchiveLog)

version       = node['buildServer']['scala']['version']
install_dir   = node['buildServer']['scala']['install_dir']
scala_pkg     = "scala-#{version}"
ext           = node['buildServer']['scala']['ext']
archive_dir   = node['buildServer']['download_location']
arch          = node['kernel']['machine']

if ext.empty?
  ext = ArchiveLog.getExtension('scala', version)
end

file "#{archive_dir}/#{scala_pkg}#{ext}" do
  action :delete
  ignore_failure true
end

directory "#{install_dir}/#{scala_pkg}" do
  action :delete
  recursive true
  ignore_failure true
end

file '/etc/profile.d/scala.sh' do
  action :delete
  only_if "grep -w #{version} /etc/profile.d/scala.sh"
  ignore_failure true
end

buildServer_log 'scala' do
  name         'scala'
  log_location node['log_location']
  log_record   "scala,#{version},scala_binary,scala,#{arch},#{ext},#{scala_pkg}#{ext}"
  action       :remove
  ignore_failure true
end
