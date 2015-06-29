# Installs perl 5.20.2 and sets it as default perl version to be used.

version      = node['perl']['version']
install_path = "#{node['perl']['prefix_dir']}/bin/perl#{version}"
perl_package = "perl-#{version}.tar.gz"
repo_url     = node['perl']['repo_url']

directory node['perl']['prefix_dir'] do
  mode '0755'
  owner 'root'
  group 'root'
  action :create
end

case node[:platform]
when 'ubuntu'
  dev_tool_cmd = 'apt-get install -y build-essential'
when 'redhat'
  dev_tool_cmd = 'yum groupinstall -y "Development tools"'
end

execute 'Installing development tools' do
  cwd node['download_location']
  command dev_tool_cmd
end

# TODO
# Uncomment below if an external repo is provided.
# remote_file "#{node['perl']['download_location']}/#{perl_package}" do
#  source  "#{repo_path}/#{perl_package}"
#  owner   'root'
#  group   'root'
#  mode    '444'
#  action  :create
# end

# Temporaryily storing the pacakage (.tar.gz) as part of cookbooks
# Though not recommended to be pushed as part of cookbook as
# package must not be versioned as part of code.
remote_file "#{node['perl']['download_location']}/#{perl_package}" do
  source "#{repo_url}/#{perl_package}"
  owner 'root'
  group 'root'
  mode '444'
  action :create
end

execute 'Extracting perl package' do
  user 'root'
  group 'root'
  cwd node['perl']['download_location']
  command "tar -xvf #{perl_package}"
  not_if   { File.exist?(install_path) }
end

execute 'Changing ownership of perl' do
  user 'root'
  group 'root'
  cwd node['perl']['download_location']
  command <<-EOH
    chown -R root:root perl-#{version}
  EOH
end

bash 'Configuring and Installating Perl' do
  user 'root'
  group 'root'
  cwd "#{node['perl']['download_location']}/perl-#{version}"
  code <<-EOH
    ./Configure -des -Dprefix=#{node['perl']['prefix_dir']}
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
    perl_home: "#{node['perl']['prefix_dir']}/bin"
  )
end
