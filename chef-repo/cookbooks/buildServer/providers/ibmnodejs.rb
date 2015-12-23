# Implementation of install and remove actions for ibmnodejs resource.

def whyrun_supported?
  true
end

use_inline_resources

action :install do

  name             = new_resource.name
  version          = new_resource.version
  archive_name     = new_resource.archive_name
  install_dir      = new_resource.install_dir
  uninstall_dir    = new_resource.uninstall_dir
  repo_url         = new_resource.repo_url

  directory "Creating install directory for ibm-nodejs" do
    path   install_dir
    action :create
    owner 'root'
    group 'root'
    mode  '0755'
    ignore_failure true
  end

  remote_file "#{install_dir}/#{archive_name}" do
    source "#{repo_url}/archives/#{archive_name}"
    owner 'root'
    group 'root'
    action :create
    mode '0777'
    ignore_failure true
  end

  template "#{install_dir}/ibm-nodejs-#{version}-installer.properties" do
    source "ibm-nodejs-installer.properties.erb"
    owner 'root'
    group 'root'
    action :create
    mode '0777'
    variables(
      install_dir: "#{install_dir}/#{name}#{version}"
    )
    ignore_failure true
    only_if { ::File.exist?("#{install_dir}/#{archive_name}") }
  end

  execute "Executing ibm nodejs sdk binary" do
    cwd     install_dir
    command "./#{archive_name} -f ./ibm-nodejs-#{version}-installer.properties -i silent 1>ibm-nodejs-log 2>&1"
    environment(
       '_JAVA_OPTIONS' => '-Dlax.debug.level=3 -Dlax.debug.all=true',
       'LAX_DEBUG' => '1'
      )
    ignore_failure true
    creates "#{install_dir}/#{name}#{version}"
    only_if { ::File.exist?("#{install_dir}/#{archive_name}") }
  end

  template "/opt/ibm/ibm-nodejs-#{version}.sh" do
    owner 'root'
    group 'root'
    source 'ibm-nodejs.sh.erb'
    mode '0644'
    variables(
      install_dir: "#{install_dir}/#{name}#{version}"
    )
   ignore_failure true
   only_if { ::Dir.exist?("#{install_dir}/#{name}#{version}") }
  end

  new_resource.updated_by_last_action(true)

end

action :remove do

  name             = new_resource.name
  version          = new_resource.version
  archive_name     = new_resource.archive_name
  install_dir      = new_resource.install_dir
  uninstall_dir    = new_resource.uninstall_dir
  repo_url         = new_resource.repo_url

  execute "Uninstalling ibm nodejs" do
    cwd   uninstall_dir
    command "./uninstall -i silent"
    ignore_failure true
    only_if { ::File.exist?("#{uninstall_dir}/uninstall") }
  end

  [
    "#{install_dir}/#{archive_name}",
    "#{install_dir}/ibm-nodejs-#{version}-installer.properties",
    "#{install_dir}/ibm-nodejs-log",
  ].each do |file|
    file file do
      action :delete
      ignore_failure true
    end
  end

  file "/etc/profile.d/ibm-nodejs-#{version}.sh" do
    action :delete
    ignore_failure true
    only_if "grep -w #{version} /etc/profile.d/ibm-nodejs-#{version}.sh"
  end

  directory "#{install_dir}/#{name}#{version}" do
    action     :delete
    recursive  true
    ignore_failure true
  end

  new_resource.updated_by_last_action(true)

end
