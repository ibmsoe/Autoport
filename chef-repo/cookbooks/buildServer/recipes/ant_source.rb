# This recipe installs ant via tarball hosted over the autoport repository.
# Pre-requiste is to install java.
# This recipe also sets ant_home and sets default path variable for ant.

include_recipe 'buildServer::java'

version       = node['buildServer']['apache-ant']['version']
install_dir   = node['buildServer']['apache-ant']['install_dir']
ant_pkg       = "apache-ant-#{version}"
archive_dir   = node['buildServer']['download_location']
ant_home      = "#{install_dir}/#{ant_pkg}"
repo_url      = node['buildServer']['repo_url']

remote_file "#{archive_dir}/#{ant_pkg}-bin.tar.bz2" do
  source "#{repo_url}/archives/#{ant_pkg}-bin.tar.bz2"
  owner 'root'
  group 'root'
  action :create
  mode '0644'
end

execute "Extracting ant #{version}" do
  cwd install_dir
  user 'root'
  group 'root'
  command "tar -jxf #{archive_dir}/#{ant_pkg}-bin.tar.bz2"
  creates "#{install_dir}/#{ant_pkg}"
end

template '/etc/profile.d/ant.sh' do
  owner 'root'
  group 'root'
  source 'ant_source.sh.erb'
  mode '0644'
  variables(
    ant_home: ant_home
  )
end


log_record = "apache-ant,#{version},ant_source,ant"
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
