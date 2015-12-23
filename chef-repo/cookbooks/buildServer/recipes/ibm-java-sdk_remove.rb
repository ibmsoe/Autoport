version_arr = node['buildServer']['ibm-java-sdk']['version']

if version_arr.kind_of?(Array) and version_arr.any?
  version_arr.each do |version|
    java_package  = "ibm-java-sdk-#{version}"
    uninstall_dir = "#{java_package}/_uninstall"
    major_version = version.split(".")[0]

    buildServer_ibmjava java_package do
      name            java_package
      version         version
      install_dir     node['buildServer']['ibm-java-sdk']['install_dir']
      uninstall_dir   uninstall_dir
      repo_url        node['buildServer']['repo_url']
      arch            node['kernel']['machine']
      action          :remove
      ignore_failure  true
    end

    record = "ibm-java-sdk-#{major_version},#{version},ibm-java-sdk,ibm-java-sdk,#{arch},.bin,#{java_package}-#{arch}-archive.bin"

    buildServer_log "ibm-java-sdk-#{major_version}" do
      name         "ibm-java-sdk-#{major_version}"
      log_location node['log_location']
      log_record   record
      action       :remove
      ignore_failure true
      only_if { Dir.exist?("#{install_dir}/#{java_package}") }
    end
  end
end
