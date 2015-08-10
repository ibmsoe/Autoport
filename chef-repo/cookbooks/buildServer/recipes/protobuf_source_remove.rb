# Recipe would uninstall/remove protobuf package installed via source.

version        = node['buildServer']['protobuf']['version']
source_dir     = node['buildServer']['protobuf']['source_dir']
install_prefix = node['buildServer']['protobuf']['install_prefix']
protobuf_pkg   = "protobuf-#{version}"
archive_dir    = node['buildServer']['download_location']

file "#{archive_dir}/#{protobuf_pkg}.tar.gz" do
  action :delete
end

directory "#{source_dir}/#{protobuf_pkg}" do
  action :delete
  recursive true
end

file "#{install_prefix}/bin/protoc" do
  action :delete
end

buildServer_log "protobuf" do
  name         "protobuf"
  log_location node['log_location']
  log_record   "protobuf,#{version},protobuf_source,protobuf"
  action       :remove
end
