version       = node['buildServer']['ibm-java-sdk']['version']
arch          = node['kernel']['machine']
java_package  = "ibm-java-sdk-#{version}"
install_dir   = node['buildServer']['ibm-java-sdk']['install_dir']
uninstall_dir = "#{java_package}/_uninstall"
arch          = node['kernel']['machine']

execute "Uninstalling ibm nodejs" do
  cwd   uninstall_dir
  command "./uninstall -i silent"
  only_if { File.exist?("#{uninstall_dir}/uninstall") }
end

[
 "#{install_dir}/#{java_package}-#{arch}-archive.bin",
 "#{install_dir}/ibm-java-installer.properties",
 "#{install_dir}/ibm-java-log"
].each do |file|
  file file do
    action :delete
  end
end

file "/etc/profile.d/ibm-java.sh" do
  action :delete
  only_if "grep -w #{version} /etc/profile.d/ibm-java.sh"
end

directory "#{install_dir}/#{java_package}" do
  action     :delete
  recursive  true
end

record = "ibm-java-sdk,#{version},ibm-java-sdk,\
ibm-java-sdk,#{arch},.bin,#{java_package}-#{arch}-archive.bin"

buildServer_log 'ibm-java-sdk' do
  name         'ibm-java-sdk'
  log_location node['log_location']
  log_record   record
  action       :remove
end
