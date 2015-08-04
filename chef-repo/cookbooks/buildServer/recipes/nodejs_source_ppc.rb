# Installs nodejs using source/build method on the archive maintained over autoport_repo.

version       = node['buildServer']['nodejs']['version']
install_dir   = node['buildServer']['nodejs']['install_dir']
nodejs_pkg    = "node-v#{version}-release-ppc"
archive_dir   = node['buildServer']['download_location']
repo_url      = node['buildServer']['repo_url']

remote_file "#{archive_dir}/#{nodejs_pkg}.tar.gz" do
  source "#{repo_url}/archives/#{nodejs_pkg}.tar.gz"
  owner 'root'
  group 'root'
  action :create
  mode '0644'
end

execute "Extracting nodejs #{version}" do
  cwd install_dir
  user 'root'
  group 'root'
  command "tar -xvf #{archive_dir}/#{nodejs_pkg}.tar.gz"
  creates "#{install_dir}/node"
end

execute "Building nodejs #{version}" do
  cwd "#{install_dir}/node"
  command './configure --dest-cpu=ppc64 && make && make install'
end

log_record = "node-v,#{version},nodejs_source,nodejs"
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
