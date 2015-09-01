# Recipe would uninstall/remove protobuf package installed via source.

version        = node['buildServer']['protobuf']['version']
source_dir     = node['buildServer']['protobuf']['source_dir']
install_prefix = node['buildServer']['protobuf']['install_prefix']
protobuf_pkg   = "protobuf-#{version}"
ext            = node['buildServer']['protobuf']['ext']
archive_dir    = node['buildServer']['download_location']
arch           = node['kernel']['machine']

file "#{archive_dir}/#{protobuf_pkg}#{ext}" do
  action :delete
end

directory "#{source_dir}/#{protobuf_pkg}" do
  action :delete
  recursive true
  notifies :delete, "file[#{install_prefix}/bin/protoc]", :immediately
end

file "#{install_prefix}/bin/protoc" do
  action :nothing
end

record = "protobuf,#{version},protobuf_source,protobuf,#{arch},#{ext},#{protobuf_pkg}#{ext}"
buildServer_log "protobuf" do
  name         "protobuf"
  log_location node['log_location']
  log_record   record
  action       :remove
end