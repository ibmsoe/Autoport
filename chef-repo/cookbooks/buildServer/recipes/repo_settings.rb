# This recipe is used to configure custom apt/yum repository over the
# respective ubuntu/rhel build slaves or the target nodes of autoport tool.

repo_name = node['repo_name']
repo_url  = node['buildServer']['repo_url']

case node[:platform]
when 'ubuntu'
  repo_file = "#{repo_name}.list"
  file_path = '/etc/apt/sources.list.d'
when 'redhat'
  repo_file = "#{repo_name}.repo"
  file_path = '/etc/yum.repos.d'
end

template "#{file_path}/#{repo_file}" do
  source "#{repo_file}.erb"
  group 'root'
  owner 'root'
  mode '0644'
  variables(
    repo_url:  repo_url,
    repo_name: repo_name
  )
end
