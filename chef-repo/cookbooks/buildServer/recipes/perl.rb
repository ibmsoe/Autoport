# Installs perl based on the version supplied and sets it as default perl version to be used.

version      = node['buildServer']['perl']['version']
install_path = "#{node['buildServer']['perl']['prefix_dir']}/bin/perl#{version}"
ext          = node['buildServer']['perl']['ext']
perl_package = "perl-#{version}#{ext}"
repo_url     = node['buildServer']['repo_url']
download_loc = node['buildServer']['download_location']
prefix_dir   = node['buildServer']['perl']['prefix_dir']
arch         = node['kernel']['machine']

directory prefix_dir do
  mode '0755'
  owner 'root'
  group 'root'
  action :create
end

remote_file "#{download_loc}/#{perl_package}" do
  source "#{repo_url}/archives/#{perl_package}"
  owner 'root'
  group 'root'
  mode '444'
  action :create
end

execute 'Extracting perl package' do
  user 'root'
  group 'root'
  cwd   '/opt'
  command "tar -xvf #{download_loc}/#{perl_package}"
  not_if   { File.exist?(install_path) }
end

execute 'Changing ownership of perl' do
  user  'root'
  group 'root'
  cwd   '/opt'
  command <<-EOH
    chown -R root:root perl-#{version}
  EOH
end

bash 'Configuring and Installating Perl' do
  user 'root'
  group 'root'
  cwd "/opt/perl-#{version}"
  code <<-EOH
    ./Configure -des -Dprefix=#{prefix_dir}
    make && make install
  EOH
  not_if { File.exist?(install_path) }
end

template '/etc/profile.d/perl.sh' do
  owner 'root'
  group 'root'
  source 'perl.sh.erb'
  mode '0644'
  variables(
    perl_home: "#{prefix_dir}/bin"
  )
end

buildServer_log "perl_source" do
  name         "perl_source"
  log_location node['log_location']
  log_record   "perl,#{version},perl_source,perl,#{arch},#{ext},#{perl_package}"
  action       :add
end
