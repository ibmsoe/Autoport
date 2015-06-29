# Installs protobuf using source/build method, using the tarball maintained in autoport_repo.

version        = node['buildServer']['pbuf']['version']
source_dir     = node['buildServer']['pbuf']['source_dir']
install_prefix = node['buildServer']['pbuf']['install_prefix']
repo_url       = node['buildServer']['repo_url']
protobuf_pkg   = "protobuf-#{version}"
archive_dir    = node['buildServer']['pbuf']['download_location']

remote_file "#{archive_dir}/#{protobuf_pkg}.tar.gz" do
  source "#{repo_url}/archives/#{protobuf_pkg}.tar.gz"
  owner 'root'
  group 'root'
  action :create
  mode '0644'
end

execute "Extracting protobuf #{version}" do
  cwd source_dir
  command "tar -vxf #{archive_dir}/#{protobuf_pkg}.tar.gz"
  creates "#{source_dir}/#{protobuf_pkg}"
end

execute "Building profobuf #{version}" do
  cwd "#{source_dir}/#{protobuf_pkg}"
  command "./configure --prefix=#{install_prefix} && make && make check && make install"
  creates '{install_prefix}/bin/protoc'
  action :run
  notifies :run, 'execute[ldconfig]', :immediately
end

execute 'ldconfig' do
  command 'ldconfig'
  action :nothing
end
