# This recipe is used to configure custom apt/yum repository over the
# respective ubuntu/rhel build slaves or the target nodes of autoport tool.

repo_name = node['repo_name']
repo_url  = node['buildServer']['repo_url']
node_os = node['platform']

case node_os
when 'ubuntu'
  repo_file = "#{repo_name}.list"
  update_command = "apt-get -y autoclean && apt-get -y update && apt-get -y autoremove"
  file_path = '/etc/apt/sources.list.d'
  execute "rm -rf #{file_path}/*" do
    ignore_failure true
  end
when 'centos'
  repo_file = "#{repo_name}.repo"
  file_path = '/etc/yum.repos.d'
  update_command = "yum clean expire-cache"
when 'redhat'
  repo_file = "#{repo_name}.repo"
  file_path = '/etc/yum.repos.d'
  node_os   = 'rhel'
  update_command = "yum clean expire-cache"
end

# node['lsb']['codename'] gives the release name ,
# such as trusty in case of ubuntu 14.04.

template "#{file_path}/#{repo_file}" do
  source "#{repo_file}.erb"
  group 'root'
  owner 'root'
  mode '0644'
  variables(
    os: node_os,
    repo_url:  repo_url,
    repo_name: repo_name,
    osrelease: node['lsb']['codename'],
    platform_version: node['platform_version'].split(".")[0],
  )
  ignore_failure true
end

execute update_command do
  ignore_failure true
end
