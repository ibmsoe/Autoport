version       = node['buildServer']['ibm-java-sdk']['version']
arch          = node['kernel']['machine']
java_package  = "ibm-java-sdk-#{version}"
install_dir   = node['buildServer']['ibm-java-sdk']['install_dir']
uninstall_dir = "#{java_package}/_uninstall"

execute "Uninstalling ibm nodejs" do
  cwd   uninstall_dir
  command "./uninstall -i silent"
  only_if { File.exist?("#{uninstall_dir}/uninstall") }
end

[
 "#{install_dir}/#{java_package}-#{arch}-archive.bin",
 "#{install_dir}/ibm-java-installer.properties",
 "#{install_dir}/ibm-java-log",
 "/etc/profile.d/ibm-java.sh"
].each do |file|
  file file do
    action :delete
  end
end

directory "#{install_dir}/#{java_package}" do
  action     :delete
  recursive  true
end

buildServer_log 'ibm-java-sdk' do
  name         'ibm-java-sdk'
  log_location node['log_location']
  log_record   "ibm-java-sdk,#{version},ibm-java-sdk,IBM Java,#{java_package}-#{arch}-archive.bin"
  action       :remove
end
