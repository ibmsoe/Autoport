# Installs perl based on the version supplied and sets it as default perl version to be used.

include_recipe 'buildServer::get_log'

version      = node['buildServer']['perl']['version']
install_path = "#{node['buildServer']['perl']['prefix_dir']}/bin/perl#{version}"
ext          = node['buildServer']['perl']['ext']
repo_url     = node['buildServer']['repo_url']
download_loc = node['buildServer']['download_location']
prefix_dir   = node['buildServer']['perl']['prefix_dir']
arch         = node['kernel']['machine']

if ext.empty?
  ext = ArchiveLog.getExtension('perl', version)
end

perl_package = "perl-#{version}#{ext}"

directory prefix_dir do
  mode '0755'
  owner 'root'
  group 'root'
  action :create
  ignore_failure true
end

remote_file "#{download_loc}/#{perl_package}" do
  source "#{repo_url}/archives/#{perl_package}"
  owner 'root'
  group 'root'
  mode '0755'
  action :create
  ignore_failure true
end

execute 'Extracting perl package' do
  user 'root'
  group 'root'
  cwd   '/opt'
  command "tar -xvf #{download_loc}/#{perl_package}"
  only_if { ! File.exist?(install_path) &&
            File.exist?("#{download_loc}/#{perl_package}") }
  ignore_failure true
end

execute 'Changing ownership of perl' do
  user  'root'
  group 'root'
  cwd   '/opt'
  command <<-EOH
    chown -R root:root perl-#{version}
  EOH
  ignore_failure true
  only_if { Dir.exist?("/opt/perl-#{version}") }
end

bash 'Configuring and Installating Perl' do
  user 'root'
  group 'root'
  cwd "/opt/perl-#{version}"
  code <<-EOH
    ./Configure -des -Dprefix=#{prefix_dir}
     make && make install
  EOH
  only_if { ! File.exist?(install_path)  &&
            Dir.exist?("/opt/perl-#{version}") }
  ignore_failure true
end

template '/etc/profile.d/perl.sh' do
  owner 'root'
  group 'root'
  source 'perl.sh.erb'
  mode '0644'
  variables(
    perl_home: "#{prefix_dir}/bin"
  )
  ignore_failure true
  only_if { Dir.exist?("/opt/perl-#{version}") }
end

buildServer_log "perl_source" do
  name         "perl_source"
  log_location node['log_location']
  log_record   "perl,#{version},perl_source,perl,#{arch},#{ext},#{perl_package}"
  action       :add
  ignore_failure true
  only_if { Dir.exist?("/opt/perl-#{version}") }
end
