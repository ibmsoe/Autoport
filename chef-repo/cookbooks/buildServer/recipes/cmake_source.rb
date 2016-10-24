# Installs cmake using source/build method, using the tarball maintained in autoport_repo.

Chef::Recipe.send(:include, CommandBuilder)
include_recipe 'buildServer::get_log'

version        = node['buildServer']['cmake']['version']
source_dir     = node['buildServer']['cmake']['source_dir']
install_prefix = "#{node['buildServer']['cmake']['install_prefix']}/cmake-#{version}"
repo_url       = node['buildServer']['repo_url']
cmake_pkg      = "cmake-#{version}"
ext            = node['buildServer']['cmake']['ext']
archive_dir    = node['buildServer']['download_location']
arch           = node['kernel']['machine']

if ext.empty?
  ext = ArchiveLog.getExtension('cmake', version)
end

remote_file "#{archive_dir}/#{cmake_pkg}#{ext}" do
  source "#{repo_url}/archives/#{cmake_pkg}#{ext}"
  owner 'root'
  group 'root'
  action :create
  mode '0755'
  ignore_failure true
end

execute "Extracting cmake #{version}" do
  cwd source_dir
  command <<-EOD
    #{CommandBuilder.command(ext, run_context)} #{archive_dir}/#{cmake_pkg}#{ext}
  EOD
  ignore_failure true
  creates "#{source_dir}/#{cmake_pkg}"
  only_if { File.exist?("#{archive_dir}/#{cmake_pkg}#{ext}") }
end

execute "Building cmake #{version}" do
  cwd "#{source_dir}/#{cmake_pkg}"
  command "./configure --prefix=#{install_prefix} && make clean && make && make install"
  action :run
  creates "#{install_prefix}/bin/cmake"
  ignore_failure true
  only_if { File.exist?("#{source_dir}/#{cmake_pkg}/configure") }
end

execute 'Setting permissions for cmake directory' do
  command "chmod -R 755 #{install_prefix}/"
  ignore_failure true
  only_if { Dir.exist?("#{install_prefix}") }
end

template '/etc/profile.d/cmake.sh' do
  source 'cmake_source.sh.erb'
  owner 'root'
  group 'root'
  mode '0644'
  variables(
    install_prefix: install_prefix,
    cmake_root: "#{install_prefix}/share/cmake-#{version}"
  )
  ignore_failure true
  only_if { File.exist?("#{install_prefix}/bin/cmake") }
end

record = "cmake,#{version},cmake_source,cmake,#{arch},#{ext},#{cmake_pkg}#{ext}"
buildServer_log "cmake" do
  name         "cmake"
  log_location node['log_location']
  log_record   record
  action       :add
  ignore_failure true
  only_if { File.exist?("#{install_prefix}/bin/cmake") }
end
