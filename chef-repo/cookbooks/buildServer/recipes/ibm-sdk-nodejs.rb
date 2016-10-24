include_recipe 'buildServer::get_log'

packages = node['buildServer']['ibm-sdk-nodejs']['packages']
install_dir = node['buildServer']['ibm-sdk-nodejs']['install_dir']
arch = node['kernel']['machine']

if packages.kind_of?(Hash) and packages.any?
  default_version, default_name = packages.first
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
      action          :install
      ignore_failure  true
    end

    record = "#{pkg_name},#{version},ibm-sdk-nodejs,ibm-sdk-nodejs,#{arch},.bin,#{archive_name}"
    buildServer_log pkg_name do
      name         pkg_name
      log_location node['log_location']
      log_record   record
      action       :add
      ignore_failure true
      only_if { Dir.exist?("#{install_dir}/#{pkg_name}#{version}") }
    end

    template '/etc/profile.d/nodejs.sh' do
      owner 'root'
      group 'root'
      source 'nodejs.sh.erb'
      mode '0644'
      variables(
        install_dir: "#{install_dir}/#{default_name}#{default_version}"
      )
      ignore_failure true
      only_if { File.exist?("#{install_dir}/#{default_name}#{default_version}") }
    end
  end
end
