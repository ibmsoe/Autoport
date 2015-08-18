# This recipe is used to install nodejs package
# Over ppc64le architecture (rhel/ubuntu) ibm-nodejs is installed via binary.
# Over x86_64 (rhel/ubuntu) installation takes place via shell script,
# which manupilates the source-lists of package manager and make nodejs
# available via yum/apt.

arch = node['kernel']['machine']
if arch == 'ppc64le'
  include_recipe 'buildServer::ibm-sdk-nodejs'
else
  setup_file = ''
  case node[:platform]
  when 'ubuntu'
    setup_file = 'setup_deb'
    opt = '--force-yes'
  when 'redhat'
    setup_file = 'setup_rpm'
    opt = ''
  end

  cookbook_file "#{Chef::Config[:file_cache_path]}/#{setup_file}" do
    source setup_file
    owner 'root'
    group 'root'
    mode '777'
    action :create
  end

  bash "Execute setup script #{setup_file}" do
    cwd "#{Chef::Config[:file_cache_path]}"
    code <<-EOH
    ./#{setup_file} > #{Chef::Config[:file_cache_path]}/node_js_install_log
    EOH
  end

  package 'nodejs' do
    action :upgrade
    options opt
  end
end
