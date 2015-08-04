# This recipe installs maven via tarball hosted over the autoport repository.
# Pre-requiste is to install java.
# This recipe also sets maven_home and sets default path variable for maven.

include_recipe 'buildServer::java'

version       = node['buildServer']['apache-maven']['version']
install_dir   = node['buildServer']['apache-maven']['install_dir']
maven_pkg     = "apache-maven-#{version}"
archive_dir   = node['buildServer']['download_location']
maven_home    = "#{install_dir}/#{maven_pkg}"
repo_url      = node['buildServer']['repo_url']

remote_file "#{archive_dir}/#{maven_pkg}-bin.tar.gz" do
  source "#{repo_url}/archives/#{maven_pkg}-bin.tar.gz"
  owner 'root'
  group 'root'
  action :create
  mode '0644'
end

execute "Extracting ant #{version}" do
  cwd install_dir
  user 'root'
  group 'root'
  command "tar -xvf #{archive_dir}/#{maven_pkg}-bin.tar.gz"
  creates "#{install_dir}/#{maven_pkg}"
end

template '/etc/profile.d/maven.sh' do
  owner 'root'
  group 'root'
  source 'maven_source.sh.erb'
  mode '0644'
  variables(
    maven_home: maven_home
  )
end

log_record = "apache-maven,#{version},maven_source,maven"
log_location = node['log_location']
path = log_location

dirpaths = []
while path != '/' do
  dirname = File.dirname(path)
  dirpaths.push(dirname)
  path = dirname
end

dirs = dirpaths.reverse
dirs.shift

dirs.reverse.each do |dir|
  directory log_location do
    owner  'root'
    group  'root'
    action :create
  end
end

file "#{log_location}/archive.log" do
  owner  'root'
  group  'root'
  mode   '644'
  action :create_if_missing
end

ruby_block 'Creating source install log entry' do
  block do
    regex_string  = Regexp.new(Regexp.quote(log_record))
    file = Chef::Util::FileEdit.new("#{log_location}/archive.log")
    file.insert_line_if_no_match(regex_string, log_record)
    file.write_file
  end
  not_if "grep '#{log_record}' #{log_location}/archive.log"
end
