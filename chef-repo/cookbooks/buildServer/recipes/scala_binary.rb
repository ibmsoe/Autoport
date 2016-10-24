# Install scala using tarball hosted over autoport_repo.

Chef::Recipe.send(:include, CommandBuilder)
include_recipe 'buildServer::get_log'

version       = node['buildServer']['scala']['version']
install_dir   = node['buildServer']['scala']['install_dir']
scala_pkg     = "scala-#{version}"
archive_dir   = node['buildServer']['download_location']
scala_home    = "#{install_dir}/#{scala_pkg}"
ext           = node['buildServer']['scala']['ext']
repo_url      = node['buildServer']['repo_url']
arch          = node['kernel']['machine']

if ext.empty?
  ext = ArchiveLog.getExtension('scala', version)
end

remote_file "#{archive_dir}/#{scala_pkg}#{ext}" do
  source "#{repo_url}/archives/#{scala_pkg}#{ext}"
  owner 'root'
  group 'root'
  action :create
  mode '0755'
  ignore_failure true
end

execute "Extracting scala #{version}" do
  cwd install_dir
  user 'root'
  group 'root'
  command <<-EOD
    #{CommandBuilder.command(ext, run_context)} #{archive_dir}/#{scala_pkg}#{ext}
  EOD
  ignore_failure true
  creates "#{install_dir}/#{scala_pkg}"
  only_if { File.exist?("#{archive_dir}/#{scala_pkg}#{ext}") }
end

template '/etc/profile.d/scala.sh' do
  owner 'root'
  group 'root'
  source 'scala_source.sh.erb'
  mode '0644'
  variables(
    scala_home: scala_home
  )
  ignore_failure true
  only_if {  Dir.exist?(scala_home) }
end

buildServer_log 'scala' do
  name         'scala'
  log_location node['log_location']
  log_record   "scala,#{version},scala_binary,scala,#{arch},#{ext},#{scala_pkg}#{ext}"
  action       :add
  ignore_failure true
  only_if {  Dir.exist?(scala_home) }
end
