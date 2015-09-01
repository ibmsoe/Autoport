package = node['buildServer']['ibm-sdk-nodejs']['name']
version = node['buildServer']['ibm-sdk-nodejs']['version']
install_dir = node['buildServer']['ibm-sdk-nodejs']['install_dir']
repo_url = node['buildServer']['repo_url']
arch = node['kernel']['machine']

if node['kernel']['machine'] == 'ppc64le'
  pkg_name = "#{package}#{version}-linux-ppcle64"
else
  arch = node['kernel']['machine']
  pkg_name = "#{package}#{version}-linux-#{arch}"
end

directory "Creating install directory for ibm-nodejs" do
  path   install_dir
  action :create
  owner 'root'
  group 'root'
  mode  '0755'
end

remote_file "#{install_dir}/#{pkg_name}.bin" do
  source "#{repo_url}/archives/#{pkg_name}.bin"
  owner 'root'
  group 'root'
  action :create
  mode '0777'
end

template "#{install_dir}/ibm-nodejs-installer.properties" do
  source "ibm-nodejs-installer.properties.erb"
  owner 'root'
  group 'root'
  action :create
  mode '0777'
  variables(
    install_dir: "#{install_dir}/#{package}#{version}"
  )
end

execute "Executing ibm nodejs sdk binary" do
  cwd     install_dir
  command "./#{pkg_name}.bin -f ./ibm-nodejs-installer.properties -i silent 1>ibm-nodejs-log 2>&1"
  environment(
     '_JAVA_OPTIONS' => '-Dlax.debug.level=3 -Dlax.debug.all=true',
     'LAX_DEBUG' => '1'
    )
  creates "#{install_dir}/#{package}#{version}"
end

template '/etc/profile.d/ibm-nodejs.sh' do
  owner 'root'
  group 'root'
  source 'ibm-nodejs.sh.erb'
  mode '0644'
  variables(
    install_dir:"#{install_dir}/#{package}#{version}"
  )
end

record = "#{package},#{version},ibm-sdk-nodejs,ibm-sdk-nodejs,#{arch},.bin,#{pkg_name}.bin"
buildServer_log package do
  name         package
  log_location node['log_location']
  log_record   record
  action       :add
end
