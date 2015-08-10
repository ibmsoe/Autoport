# This recipe installs gradle via tarball hosted over the autoport repository.
# Pre-requiste is to install java.
# This recipe also sets gradle_home and sets default path variable for gradle.

version      = node['buildServer']['gradle']['version']
install_dir  = node['buildServer']['gradle']['install_dir']
install_path = "#{install_dir}/packages/gradle"
gradle_pkg   = "gradle-#{version}-bin.zip"
archive_dir  = node['buildServer']['download_location']
gradle_home  = "#{install_dir}/gradle"
repo_url     = node['buildServer']['repo_url']

include_recipe 'buildServer::java'

package 'unzip'

[
  "#{install_dir}/packages",
  install_path
].each do |pkg|
  directory pkg do
    mode '0755'
    owner 'root'
    group 'root'
    action :create
  end
end

remote_file "#{archive_dir}/#{gradle_pkg}" do
  source "#{repo_url}/archives/#{gradle_pkg}"
  owner 'root'
  group 'root'
  action :create
end

bash 'Extracting the archive' do
  user 'root'
  cwd install_path
  code <<-EOD
    unzip #{archive_dir}/#{gradle_pkg}
    EOD
  creates "#{install_path}/gradle-#{version}/bin/gradle"
end

link gradle_home do
  to "#{install_path}/gradle-#{version}"
  action :create
end

template '/etc/profile.d/gradle.sh' do
  source 'gradle_source.sh.erb'
  owner 'root'
  group 'root'
  mode '0644'
  variables(
    gradle_home: gradle_home
  )
end

buildServer_log 'gradle' do
  name         'gradle'
  log_location node['log_location']
  log_record   "gradle,#{version},gradle_source,gradle"
  action       :add
end
