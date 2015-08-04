# Install scala using source and build method, using tarball hosted over autoport_repo.

version       = node['buildServer']['scala']['version']
install_dir   = node['buildServer']['scala']['install_dir']
scala_pkg    = "scala-#{version}"
archive_dir   = node['buildServer']['download_location']
scala_home   = "#{install_dir}/#{scala_pkg}"
repo_url      = node['buildServer']['repo_url']

remote_file "#{archive_dir}/#{scala_pkg}.tgz" do
  source "#{repo_url}/archives/#{scala_pkg}.tgz"
  owner 'root'
  group 'root'
  action :create
  mode '0644'
end

execute "Extracting scala #{version}" do
  cwd install_dir
  user 'root'
  group 'root'
  command "tar -xvf #{archive_dir}/#{scala_pkg}.tgz"
  creates "#{install_dir}/#{scala_pkg}"
end

template '/etc/profile.d/scala.sh' do
  owner 'root'
  group 'root'
  source 'scala_source.sh.erb'
  mode '0644'
  variables(
    scala_home: scala_home
  )
end

log_record = "scala,#{version},scala_source,scala"
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
