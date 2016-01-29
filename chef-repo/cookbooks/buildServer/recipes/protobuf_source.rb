# Installs protobuf using source/build method, using the tarball maintained in autoport_repo.

Chef::Recipe.send(:include, CommandBuilder)
Chef::Recipe.send(:include, ArchiveLog)

version        = node['buildServer']['protobuf']['version']
source_dir     = node['buildServer']['protobuf']['source_dir']
install_prefix = "#{node['buildServer']['protobuf']['install_prefix']}-#{version}"
repo_url       = node['buildServer']['repo_url']
protobuf_pkg   = "protobuf-#{version}"
ext            = node['buildServer']['protobuf']['ext']
archive_dir    = node['buildServer']['download_location']
arch           = node['kernel']['machine']

if ext.empty?
  ext = ArchiveLog.getExtension('protobuf', version)
end

remote_file "#{archive_dir}/#{protobuf_pkg}#{ext}" do
  source "#{repo_url}/archives/#{protobuf_pkg}#{ext}"
  owner 'root'
  group 'root'
  action :create
  mode '0655'
  ignore_failure true
end

execute "Extracting protobuf #{version}" do
  cwd source_dir
  command <<-EOD
    #{CommandBuilder.command(ext, run_context)} #{archive_dir}/#{protobuf_pkg}#{ext}
  EOD
  ignore_failure true
  creates "#{source_dir}/#{protobuf_pkg}"
  only_if { File.exist?("#{archive_dir}/#{protobuf_pkg}#{ext}") }
end

execute "Running autogen" do
  cwd "#{source_dir}/#{protobuf_pkg}"
  command "./autogen.sh"
  action :run
  ignore_failure true
  creates "#{source_dir}/#{protobuf_pkg}/configure"
  only_if { File.exist?("#{source_dir}/#{protobuf_pkg}/autogen.sh") }
end


execute "Building profobuf #{version}" do
  cwd "#{source_dir}/#{protobuf_pkg}"
  command "./configure --prefix=#{install_prefix} && make clean && make && make install"
  action :run
  notifies :run, 'execute[ldconfig]', :immediately
  creates "#{install_prefix}/bin/protoc"
  ignore_failure true
  only_if { File.exist?("#{source_dir}/#{protobuf_pkg}/configure") }
end

execute 'ldconfig' do
  command 'ldconfig'
  action :nothing
  ignore_failure true
  only_if { Dir.exist?("#{source_dir}/#{protobuf_pkg}") }
end

execute 'Setting permissions' do
  command "chmod -R 755 #{install_prefix}/"
  ignore_failure true
  only_if { Dir.exist?("#{install_prefix}") }
end

template '/etc/profile.d/protobuf.sh' do
  source 'protobuf_source.sh.erb'
  owner 'root'
  group 'root'
  mode '0644'
  variables(
    install_prefix: install_prefix
  )
  ignore_failure true
  only_if { File.exist?("#{install_prefix}/bin/protoc") }
end

record = "protobuf,#{version},protobuf_source,protobuf,#{arch},#{ext},#{protobuf_pkg}#{ext}"
buildServer_log "protobuf" do
  name         "protobuf"
  log_location node['log_location']
  log_record   record
  action       :add
  ignore_failure true
  only_if { Dir.exist?("#{source_dir}/#{protobuf_pkg}") }
end
