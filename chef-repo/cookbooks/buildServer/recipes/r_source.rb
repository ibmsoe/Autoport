# Installs R using source and build method.

Chef::Recipe.send(:include, ArchiveLog)

version      = node['buildServer']['R']['version']
install_dir  = node['buildServer']['R']['install_dir']
install_path = "#{install_dir}/R-#{version}"
ext          = node['buildServer']['R']['ext']
repo_url     = node['buildServer']['repo_url']
download_loc = node['buildServer']['download_location']
arch         = node['kernel']['machine']

if ext.empty?
  ext = ArchiveLog.getExtension('R', version)
end

r_package = "R-#{version}#{ext}"

remote_file "#{download_loc}/#{r_package}" do
  source "#{repo_url}/archives/#{r_package}"
  owner 'root'
  group 'root'
  mode '0755'
  action :create
  ignore_failure true
end

execute 'Extracting R package' do
  user 'root'
  group 'root'
  cwd   install_dir
  command "tar -xvf #{download_loc}/#{r_package}"
  only_if { ! Dir.exist?(install_path) &&
            File.exist?("#{download_loc}/#{r_package}") }
  ignore_failure true
end

bash 'Building R from source' do
  user 'root'
  group 'root'
  cwd  install_path
  code <<-EOH
     ./configure --with-readline=no --with-x=no
     make && make install
  EOH
  only_if { ! File.exist?("#{install_path}/bin/R") &&
           Dir.exist?(install_path)}
  ignore_failure true
end

template '/etc/profile.d/R.sh' do
  owner 'root'
  group 'root'
  source 'R.sh.erb'
  mode '0644'
  variables(
    r_home: "#{install_path}/bin"
  )
  ignore_failure true
  only_if { File.exist?("#{install_path}/bin/R") }
end

buildServer_log "r_source" do
  name         "r_source"
  log_location node['log_location']
  log_record   "R,#{version},r_source,R,#{arch},#{ext},#{r_package}"
  action       :add
  ignore_failure true
  only_if { File.exist?("#{install_path}/bin/R") }
end
