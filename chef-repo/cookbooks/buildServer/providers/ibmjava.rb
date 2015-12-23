# Implementation of install and remove actions for ibmjava resource.

def whyrun_supported?
  true
end

use_inline_resources

action :install do

  java_package     = new_resource.name
  version          = new_resource.version
  major_version    = new_resource.version.split(".")[0]
  install_dir      = new_resource.install_dir
  uninstall_dir    = new_resource.uninstall_dir
  repo_url         = new_resource.repo_url
  arch             = new_resource.arch

  directory "Creating install directory for ibm-java" do
    path   install_dir
    action :create
    owner 'root'
    group 'root'
    mode  '0755'
    ignore_failure true
  end

  remote_file "#{install_dir}/#{java_package}-#{arch}-archive.bin" do
    source "#{repo_url}/archives/#{java_package}-#{arch}-archive.bin"
    owner 'root'
    group 'root'
    action :create
    mode '0777'
    ignore_failure true
  end

  template "#{install_dir}/ibm-java-#{version}-installer.properties" do
    source "ibm-java-installer.properties.erb"
    owner 'root'
    group 'root'
    action :create
    mode '0644'
    variables(
      install_dir:"#{install_dir}/#{java_package}"
    )
    ignore_failure true
    only_if { ::File.exist?("#{install_dir}/#{java_package}-#{arch}-archive.bin") }
  end

  execute "Executing Java Binary" do
    cwd     install_dir
    command "./#{java_package}-#{arch}-archive.bin \
      -f ./ibm-java-#{version}-installer.properties -i silent 1>ibm-java-log 2>&1"
    environment(
       '_JAVA_OPTIONS' => '-Dlax.debug.level=3 -Dlax.debug.all=true',
       'LAX_DEBUG' => '1'
    )
    creates "#{install_dir}/#{java_package}"
    ignore_failure true
    only_if { ::File.exist?("#{install_dir}/#{java_package}-#{arch}-archive.bin") }
  end

  template "#{install_dir}/ibm-java-#{major_version}.sh" do
    owner 'root'
    group 'root'
    source 'ibm-java.sh.erb'
    mode '0644'
    variables(
      java_home:"#{install_dir}/#{java_package}"
    )
    ignore_failure true
    only_if { ::Dir.exist?("#{install_dir}/#{java_package}") }
  end

  new_resource.updated_by_last_action(true)

end

action :remove do

  java_package     = new_resource.name
  version          = new_resource.version
  major_version    = new_resource.version.split(".")[0]
  install_dir      = new_resource.install_dir
  uninstall_dir    = new_resource.uninstall_dir
  repo_url         = new_resource.repo_url
  arch             = new_resource.arch

  execute "Uninstalling ibm nodejs" do
    cwd   uninstall_dir
    command "./uninstall -i silent"
    ignore_failure true
    only_if { File.exist?("#{uninstall_dir}/uninstall") }
  end

  [
    "#{install_dir}/#{java_package}-#{arch}-archive.bin",
    "#{install_dir}/ibm-java-#{version}-installer.properties",
    "#{install_dir}/ibm-java-log"
  ].each do |file|
    file file do
      action :delete
      ignore_failure true
    end
  end

  file "#{install_dir}/ibm-java-#{major_version}.sh" do
    action :delete
    ignore_failure true
  end

  directory "#{install_dir}/#{java_package}" do
    action     :delete
    recursive  true
    ignore_failure true
  end

  new_resource.updated_by_last_action(true)
end
