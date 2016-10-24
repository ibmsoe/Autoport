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

file "#{archive_dir}/#{cmake_pkg}#{ext}" do
  action :delete
  ignore_failure true
end

execute "Uninstalling cmake #{version}" do
  cwd "#{source_dir}/#{cmake_pkg}"
  command "make uninstall"
  action :run
  ignore_failure true
  only_if {Dir.exist?("#{source_dir}/#{cmake_pkg}")}
end

directory "#{source_dir}/#{cmake_pkg}" do
  action     :delete
  recursive  true
  ignore_failure true
end

directory install_prefix do
  action     :delete
  recursive  true
  ignore_failure true
end

# Reverting back cmake_env variables.
# Variables will be set as per cmake distro installation.
cmake_data_path = [
                    '/usr/share/cmake',
                    '/usr/share/cmake-*'

                  ]
cmake_root = []

template '/etc/profile.d/cmake.sh' do
  owner 'root'
  group 'root'
  source 'cmake_source.sh.erb'
  mode '0644'
  variables(
    lazy {
      { 
        cmake_root: cmake_root[0], 
        install_prefix: ""
      }
    }
  )
  ignore_failure true
  only_if do
    cmake_root = Dir.glob(cmake_data_path)
    cmake_root.kind_of?(Array) and cmake_root.any?
  end
end

record = "cmake,#{version},cmake_source,cmake,#{arch},#{ext},#{cmake_pkg}#{ext}"
buildServer_log "cmake" do
  name         "cmake"
  log_location node['log_location']
  log_record   record
  action       :remove
  ignore_failure true
end
