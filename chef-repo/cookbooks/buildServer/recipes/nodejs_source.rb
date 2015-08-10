# Installs nodejs via source/build method using archive maintained in autoport_repo.

version       = node['buildServer']['nodejs']['version']
install_dir   = node['buildServer']['nodejs']['install_dir']
nodejs_pkg    = "node-v#{version}"
archive_dir   = node['buildServer']['download_location']
repo_url      = node['buildServer']['repo_url']

directory "#{install_dir}/node" do
  action :create
  owner 'root'
  group 'root'
end

remote_file "#{archive_dir}/#{nodejs_pkg}.tar.gz" do
  source "#{repo_url}/archives/#{nodejs_pkg}.tar.gz"
  owner 'root'
  group 'root'
  action :create
  mode '0644'
end

execute "Extracting nodejs #{version}" do
  cwd "#{install_dir}/node"
  user 'root'
  group 'root'
  command "tar -xvf #{archive_dir}/#{nodejs_pkg}.tar.gz"
  creates "#{install_dir}/node/#{nodejs_pkg}"
end

execute "Building nodejs #{version}" do
  cwd "#{install_dir}/node/#{nodejs_pkg}"
  command './configure && make && make install'
end

buildServer_log 'node-v' do
  name         'node-v'
  log_location node['log_location']
  log_record   "node-v,#{version},nodejs_source,nodejs"
  action       :add
end
