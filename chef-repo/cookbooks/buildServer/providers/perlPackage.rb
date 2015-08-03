def whyrun_supported?
  true
end

use_inline_resources

action :install do
  name             = new_resource.name
  archive_location = new_resource.archive_location
  repo_location    = new_resource.repo_location
  archive_name     = new_resource.archive_name
  extract_location = new_resource.extract_location
  perl_prefix_dir  = new_resource.perl_prefix_dir
  perl_module      = name.split('-')
  perl_module.pop
  module_string   = perl_module.join('::')
  guard_condition = "#{perl_prefix_dir}/bin/perl \
                   -M#{module_string} -e 'print \"$#{module_string}::VERSION\"'"

  directory extract_location do
    mode '0755'
    owner 'root'
    group 'root'
    action :create
  end

  remote_file "#{archive_location}/#{archive_name}" do
    source "#{repo_location}/archives/#{archive_name}"
    owner 'root'
    group 'root'
    mode '0775'
    action :create
  end

  execute "Extracting #{archive_name} package" do
    user 'root'
    group 'root'
    cwd extract_location
    command "tar -xvf #{archive_location}/#{archive_name}"
    not_if   { ::File.exist?("#{extract_location}/#{name}") }
  end

  execute "Changing ownership of #{name}" do
    user 'root'
    group 'root'
    cwd extract_location
    command <<-EOH
      chown -R root:root #{name}
    EOH
  end

  bash "Building Package #{name}" do
    user 'root'
    cwd "#{extract_location}/#{name}"
    code <<-EOH
      #{perl_prefix_dir}/bin/perl Makefile.PL
      make
      make install >> /tmp/check
    EOH
    not_if guard_condition
  end
  new_resource.updated_by_last_action(true)
end
