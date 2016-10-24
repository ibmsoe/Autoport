# Installs luajit using source and build method.

include_recipe 'buildServer::get_log'

version      = node['buildServer']['luajit']['version']
install_dir  = node['buildServer']['luajit']['install_dir']
install_path = "#{install_dir}/LuaJIT-#{version}"
ext          = node['buildServer']['luajit']['ext']
repo_url     = node['buildServer']['repo_url']
download_loc = node['buildServer']['download_location']
arch         = node['kernel']['machine']
prefix       = "/usr/local/luajit-#{version}"

if ext.empty?
  ext = ArchiveLog.getExtension('LuaJIT', version)
end

luajit_package = "LuaJIT-#{version}#{ext}"

remote_file "#{download_loc}/#{luajit_package}" do
  source "#{repo_url}/archives/#{luajit_package}"
  owner 'root'
  group 'root'
  mode '0755'
  action :create
  ignore_failure true
end

execute 'Extracting luajit package' do
  user 'root'
  group 'root'
  cwd   install_dir
  command "tar -xvf #{download_loc}/#{luajit_package}"
  only_if { ! Dir.exist?(install_path) &&
            File.exist?("#{download_loc}/#{luajit_package}") }
  ignore_failure true
end

bash 'Building luajit from source' do
  user 'root'
  group 'root'
  cwd  install_path
  code <<-EOH
     make && make install PREFIX="#{prefix}"
  EOH
  only_if { ! File.exist?("#{prefix}/bin/luajit") &&
           Dir.exist?(install_path)}
  ignore_failure true
end

link "#{prefix}/bin/luajit" do
  to "#{prefix}/bin/luajit-#{version}-beta2"
  ignore_failure true
end

template '/etc/profile.d/luajit.sh' do
  owner 'root'
  group 'root'
  source 'luajit.sh.erb'
  mode '0644'
  variables(
    luajit_home: "#{prefix}/bin"
  )
  ignore_failure true
  only_if { File.exist?("#{prefix}/bin/luajit") }
end

buildServer_log "LuaJIT" do
  name         "LuaJIT"
  log_location node['log_location']
  log_record   "LuaJIT,#{version},luajit_source,LuaJIT,#{arch},#{ext},#{luajit_package}"
  action       :add
  ignore_failure true
  only_if { File.exist?("#{prefix}/bin/luajit") }
end
