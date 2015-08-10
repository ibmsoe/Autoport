# Implementation of log resource.

def whyrun_supported?
  true
end

use_inline_resources

action :add do
  path = new_resource.log_location
  dirpaths = [path]
  while path != '/' do
    dirname = ::File.dirname(path)
    dirpaths.push(dirname)
    path = dirname
  end

  dirs = dirpaths.reverse
  dirs.shift
  dirs.each do |dir|
    directory dir do
      owner  'root'
      group  'root'
      action :create
    end
  end

  file "#{new_resource.log_location}/archive.log" do
    owner  'root'
    group  'root'
    mode   '644'
    action :create_if_missing
  end

  ruby_block "Creating source install log entry for #{new_resource.name}" do
    block do
      regex_string  = Regexp.new(Regexp.quote(new_resource.log_record))
      file = Chef::Util::FileEdit.new("#{new_resource.log_location}/archive.log")
      file.search_file_delete(/^#{new_resource.name}.*$/)
      file.insert_line_if_no_match(regex_string, new_resource.log_record)
      file.write_file
    end
    not_if "grep -w '#{new_resource.log_record}' #{new_resource.log_location}/archive.log"
  end

  execute "Removing blank lines" do
    command "sed -i '/^$/d' #{new_resource.log_location}/archive.log"
  end

  new_resource.updated_by_last_action(true)
end

action :remove do

  ruby_block "Removing source install log entry for #{new_resource.name}" do
    block do
      regex_string  = Regexp.new(Regexp.quote(new_resource.log_record))
      file = Chef::Util::FileEdit.new("#{new_resource.log_location}/archive.log")
      file.search_file_delete(regex_string)
      file.write_file
    end
    only_if "grep -w '#{new_resource.log_record}' #{new_resource.log_location}/archive.log"
  end

  execute "Removing blank lines" do
    command "sed -i '/^$/d' #{new_resource.log_location}/archive.log"
  end

  new_resource.updated_by_last_action(true)
end
