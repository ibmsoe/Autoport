# Installs python module "py" using source and build method.
# source to be built is hosted at autoport_repo.

include_recipe 'buildServer::get_log'

py_version = node['buildServer']['py']['version']
py_ext = node['buildServer']['py']['ext']
arch       = node['kernel']['machine']
extract_location = node['buildServer']['python']['extract_location']

if py_ext.empty?
  py_ext = ArchiveLog.getExtension('py', py_version)
end

buildServer_pythonPackage "py-#{py_version}" do
  archive_name "py-#{py_version}#{py_ext}"
  archive_location node['buildServer']['download_location']
  extract_location node['buildServer']['python']['extract_location']
  repo_url node['buildServer']['repo_url']
  action :install
  ignore_failure true
end

record = "py,#{py_version},python_modules,python-py,#{arch},#{py_ext},py-#{py_version}#{py_ext}"

buildServer_log "py" do
  name         "py"
  log_location node['log_location']
  log_record   record
  action       :add
  ignore_failure true
  only_if { Dir.exist?("#{extract_location}/py-#{py_version}") }
end
