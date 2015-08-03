include_recipe 'buildServer::perl'

{
  'YAML-Tiny' => node['buildServer']['YAML-Tiny']['version']
}.each do |pkg, version|
  buildServer_perlPackage "#{pkg}-#{version}" do
    archive_name "#{pkg}-#{version}.tar.gz"
    archive_location node['buildServer']['download_location']
    extract_location node['buildServer']['perl']['extract_location']
    perl_prefix_dir node['buildServer']['perl']['prefix_dir']
    repo_location node['buildServer']['repo_url']
    action :install
  end
end

log_record = "YAML-Tiny,#{node['buildServer']['YAML-Tiny']['version']},perl_modules,"
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
