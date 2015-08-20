package = node['buildServer']['ibm-sdk-nodejs']['name']
version = node['buildServer']['ibm-sdk-nodejs']['version']
arch = node['kernel']['machine']
install_dir = node['buildServer']['ibm-sdk-nodejs']['install_dir']
uninstall_dir = "#{install_dir}/#{package}-#{version}/_node_installation"

if node['kernel']['machine'] == 'ppc64le'
  pkg_name = "#{package}-#{version}-linux-ppcle64"
else
  arch = node['kernel']['machine']
  pkg_name = "#{package}-#{version}-linux-#{arch}"
end

execute "Uninstalling ibm nodejs" do
  cwd   uninstall_dir
  command "./uninstall -i silent"
  only_if { File.exist?("#{uninstall_dir}/uninstall") }
end

[
  "#{install_dir}/#{pkg_name}.bin", 
  "#{install_dir}/ibm-nodejs-installer.properties",
  "#{install_dir}/ibm-nodejs-log",
  '/etc/profile.d/ibm-nodejs.sh'
].each do |file|
  file file do
    action :delete
  end
end

directory "#{install_dir}/#{package}-#{version}" do
  action     :delete
  recursive  true
end

buildServer_log package do
  name         package
  log_location node['log_location']
  log_record   "#{package},#{version},ibm-sdk-nodejs,IBM SDK for Node.js,#{pkg_name}"
  action       :remove
end
