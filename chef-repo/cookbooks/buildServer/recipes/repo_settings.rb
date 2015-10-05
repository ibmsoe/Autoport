# This recipe is used to configure custom apt/yum repository over the
# respective ubuntu/rhel build slaves or the target nodes of autoport tool.

repo_name = node['repo_name']
repo_url  = node['buildServer']['repo_url']
node_os = node['platform']

case node_os
when 'ubuntu'
  repo_file = "#{repo_name}.list"
  file_path = '/etc/apt/sources.list.d'
when 'redhat'
  repo_file = "#{repo_name}.repo"
  file_path = '/etc/yum.repos.d'
  node_os   = 'rhel'
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
    platform_version: node['platform_version'],
  )
end
