package = node['buildServer']['ibm-sdk-nodejs']['name']
version = node['buildServer']['ibm-sdk-nodejs']['version']
arch = node['kernel']['machine']
install_dir = node['buildServer']['ibm-sdk-nodejs']['install_dir']
uninstall_dir = "#{install_dir}/#{package}-#{version}/_node_installation"
arch = node['kernel']['machine']

if node['kernel']['machine'] == 'ppc64le'
  pkg_name = "#{package}#{version}-linux-ppcle64"
elsif node['kernel']['machine'] == 'x86_64'
  pkg_name = "#{package}#{version}-linux-x64"
else
  arch = node['kernel']['machine']
  pkg_name = "#{package}#{version}-linux-#{arch}"
end

execute "Uninstalling ibm nodejs" do
  cwd   uninstall_dir
  command "./uninstall -i silent"
  ignore_failure true
  only_if { File.exist?("#{uninstall_dir}/uninstall") }
end

[
  "#{install_dir}/#{pkg_name}.bin",
  "#{install_dir}/ibm-nodejs-installer.properties",
  "#{install_dir}/ibm-nodejs-log",
].each do |file|
  file file do
    action :delete
    ignore_failure true
  end
end

file "/etc/profile.d/ibm-nodejs.sh" do
  action :delete
  ignore_failure true
  only_if "grep -w #{version} /etc/profile.d/ibm-nodejs.sh"
end

directory "#{install_dir}/#{package}#{version}" do
  action     :delete
  recursive  true
  ignore_failure true
end

record = "#{package},#{version},ibm-sdk-nodejs,ibm-sdk-nodejs,#{arch},.bin,#{pkg_name}.bin"

buildServer_log package do
  name         package
  log_location node['log_location']
  log_record   record
  action       :remove
  ignore_failure true
end
