# Recipe would uninstall/remove luajit package built from source

Chef::Recipe.send(:include, ArchiveLog)

version       = node['buildServer']['luajit']['version']
install_dir   = node['buildServer']['luajit']['install_dir']
install_path  = "#{install_dir}/LuaJIT-#{version}"
luajit_pkg    = "LuaJIT-#{version}"
archive_dir   = node['buildServer']['download_location']
ext           = node['buildServer']['luajit']['ext']
arch          = node['kernel']['machine']
prefix        = "/usr/local/luajit-#{version}"

if ext.empty?
  ext = ArchiveLog.getExtension('LuaJIT', version)
end

link "#{prefix}/bin/luajit" do
  action :delete
  ignore_failure true
end

bash 'Uninstalling luajit' do
  user 'root'
  group 'root'
  cwd  install_path
  code <<-EOH
     make uninstall PREFIX="#{prefix}"
  EOH
  only_if {Dir.exist?(install_path)}
  ignore_failure true
end

file "#{archive_dir}/#{luajit_pkg}#{ext}" do
   action :delete
   ignore_failure true
end

directory "#{install_path}" do
   action :delete
   recursive true
   ignore_failure true
end

directory "#{prefix}" do
  action :delete
  recursive true
  ignore_failure true
end

file "/etc/profile.d/luajit.sh" do
  action :delete
  only_if "grep -w #{version} /etc/profile.d/luajit.sh"
  ignore_failure true
end

buildServer_log "LuaJIT" do
  name         "LuaJIT"
  log_location node['log_location']
  log_record   "LuaJIT,#{version},luajit_source,LuaJIT,#{arch},#{ext},#{luajit_pkg}"
  action       :remove
  ignore_failure true
  only_if { File.exist?("#{prefix}/bin/luajit") }
end

