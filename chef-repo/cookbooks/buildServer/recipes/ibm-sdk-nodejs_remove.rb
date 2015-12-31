packages = node['buildServer']['ibm-sdk-nodejs']['packages']
install_dir = node['buildServer']['ibm-sdk-nodejs']['install_dir']
arch = node['kernel']['machine']

if packages.kind_of?(Hash) and packages.any?
  packages.each do |version, pkg_name|

    if arch == 'ppc64le'
      archive_name = "#{pkg_name}#{version}-linux-ppcle64.bin"
    elsif arch == 'x86_64'
      archive_name = "#{pkg_name}#{version}-linux-x64.bin"
    end

    uninstall_dir = "#{install_dir}/#{pkg_name}#{version}/_node_installation"

    buildServer_ibmnodejs pkg_name do
      name            pkg_name
      version         version
      install_dir     install_dir
      uninstall_dir   uninstall_dir
      repo_url        node['buildServer']['repo_url']
      archive_name    archive_name
      action          :remove
      ignore_failure  true
    end

    record = "#{pkg_name},#{version},ibm-sdk-nodejs,ibm-sdk-nodejs,#{arch},.bin,#{archive_name}"
    buildServer_log pkg_name do
      name         pkg_name
      log_location node['log_location']
      log_record   record
      action       :remove
      ignore_failure true
    end
  end
end
