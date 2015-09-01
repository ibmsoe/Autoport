# Installs protobuf using source/build method, using the tarball maintained in autoport_repo.

Chef::Recipe.send(:include, CommandBuilder)

version        = node['buildServer']['protobuf']['version']
source_dir     = node['buildServer']['protobuf']['source_dir']
install_prefix = node['buildServer']['protobuf']['install_prefix']
repo_url       = node['buildServer']['repo_url']
protobuf_pkg   = "protobuf-#{version}"
ext            = node['buildServer']['protobuf']['ext']
archive_dir    = node['buildServer']['download_location']
arch           = node['kernel']['machine']

remote_file "#{archive_dir}/#{protobuf_pkg}#{ext}" do
  source "#{repo_url}/archives/#{protobuf_pkg}#{ext}"
  owner 'root'
  group 'root'
  action :create
  mode '0644'
end

execute "Extracting protobuf #{version}" do
  cwd source_dir
  command <<-EOD
    #{CommandBuilder.command(ext, run_context)} #{archive_dir}/#{protobuf_pkg}#{ext}
  EOD
  creates "#{source_dir}/#{protobuf_pkg}"
end

execute "Building profobuf #{version}" do
  cwd "#{source_dir}/#{protobuf_pkg}"
  command "./configure --prefix=#{install_prefix} && make && make check && make install"
  creates "#{install_prefix}/bin/protoc"
  action :run
  notifies :run, 'execute[ldconfig]', :immediately
end

execute 'ldconfig' do
  command 'ldconfig'
  action :nothing
end

record = "protobuf,#{version},protobuf_source,protobuf,#{arch},#{ext},#{protobuf_pkg}#{ext}"
buildServer_log "protobuf" do
  name         "protobuf"
  log_location node['log_location']
  log_record   record
  action       :add
end
