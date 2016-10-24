# This recipe to install cmake using package manager and set CMAKE_ROOT env variable.

case node['platform']
when 'ubuntu'
  opt = '--force-yes'
when 'redhat', 'centos'
  opt = ''
end

package "Installing cmake" do
  package_name   'cmake'
  action         :upgrade
  options        opt
  ignore_failure true
end

cmake_data_path = [
                    '/usr/share/cmake',
                    '/usr/share/cmake-*'

                  ]
cmake_root = []

template '/etc/profile.d/cmake.sh' do
  owner 'root'
  group 'root'
  source 'cmake.sh.erb'
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
    # Extract the exact name of cmake folder located in /usr/share directory.
    # On RHEL it appears to be created with name 'cmake' whereas on ubuntu 'cmake-<version>'
    cmake_root = Dir.glob(cmake_data_path)
    cmake_root.kind_of?(Array) and cmake_root.any?
  end
end

buildServer_log "cmake" do
  name         "cmake"
  log_location node['log_location']
  log_record   "cmake"
  action       :remove
  ignore_failure true
  only_if { Dir.exist?(cmake_root[0])}
end
