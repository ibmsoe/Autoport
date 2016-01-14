# Recipe would uninstall/remove protobuf package installed via source.

Chef::Recipe.send(:include, ArchiveLog)

version        = node['buildServer']['protobuf']['version']
source_dir     = node['buildServer']['protobuf']['source_dir']
install_prefix = "#{node['buildServer']['protobuf']['install_prefix']}-#{version}"
protobuf_pkg   = "protobuf-#{version}"
ext            = node['buildServer']['protobuf']['ext']
archive_dir    = node['buildServer']['download_location']
arch           = node['kernel']['machine']

if ext.empty?
  ext = ArchiveLog.getExtension('protobuf', version)
end

[
  "#{install_prefix}/bin/protoc",
  "/etc/profile.d/protobuf.sh"
].each do |fil|
  file fil do
    action :delete
    ignore_failure true
  end
end

directory "#{source_dir}/#{protobuf_pkg}" do
  action :delete
  recursive true
  notifies :delete, "file[#{install_prefix}/bin/protoc]", :immediately
  ignore_failure true
end

record = "protobuf,#{version},protobuf_source,protobuf,#{arch},#{ext},#{protobuf_pkg}#{ext}"
buildServer_log "protobuf" do
  name         "protobuf"
  log_location node['log_location']
  log_record   record
  action       :remove
  ignore_failure true
end
