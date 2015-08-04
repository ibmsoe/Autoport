# Installs perl based on the version supplied and sets it as default perl version to be used.

version      = node['buildServer']['perl']['version']
install_path = "#{node['buildServer']['perl']['prefix_dir']}/bin/perl#{version}"
perl_package = "perl-#{version}.tar.gz"
repo_url     = node['buildServer']['repo_url']
download_loc = node['buildServer']['download_location']
prefix_dir   = node['buildServer']['perl']['prefix_dir']

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
