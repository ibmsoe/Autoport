# This recipe installs java package using package manager.
# It is also responsible to configure java_home using java.sh in profile.d.

version = node['buildServer']['ibm-java']['version']
arch = node['kernel']['machine']
java_package = "ibm-java-#{arch}-sdk-#{version}.0-1.1"
install_dir   = node['buildServer']['ibm-java']['install_dir']
repo_url      = node['buildServer']['repo_url']

remote_file "#{install_dir}/#{java_package}.bin" do
  source "#{repo_url}/archives/#{java_package}.bin"
  owner 'root'
  group 'root'
  action :create
  mode '0777'
end

cookbook_file "#{install_dir}/installer.properties" do
  source "installer.properties"
  owner 'root'
  group 'root'
  action :create
  mode '0777'
end

execute "Executing Java Binary" do
  cwd     install_dir
  command "./#{java_package}.bin -f ./installer.properties -i silent 1>console.txt 2>&1"
  environment(
     '_JAVA_OPTIONS' => '-Dlax.debug.level=3 -Dlax.debug.all=true',
     'LAX_DEBUG' => '1'
    )
end
