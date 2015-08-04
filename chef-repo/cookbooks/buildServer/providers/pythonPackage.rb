def whyrun_supported?
  true
end

use_inline_resources

action :install do
  name             = new_resource.name
  archive_location = new_resource.archive_location
  archive_name     = new_resource.archive_name
  repo_url         = new_resource.repo_url
  extract_location = new_resource.extract_location

  directory extract_location do
    mode '0755'
    owner 'root'
    group 'root'
    action :create
  end

  remote_file "#{archive_location}/#{archive_name}" do
    source "#{repo_url}/archives/#{archive_name}"
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

  bash "Install python package #{name}" do
    user 'root'
    group 'root'
    cwd "#{extract_location}/#{name}"
    code <<-EOH
        python setup.py build
        python setup.py install
      EOH
  end
  new_resource.updated_by_last_action(true)
end
