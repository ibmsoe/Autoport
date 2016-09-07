# Installs python module "pytest" using source and build method.
# source to be built is hosted at autoport_repo.

include_recipe 'buildServer::get_log'

pytest_ver = node['buildServer']['pytest']['version']
pytest_ext = node['buildServer']['pytest']['ext']
arch       = node['kernel']['machine']
extract_location = node['buildServer']['python']['extract_location']

if pytest_ext.empty?
  pytest_ext = ArchiveLog.getExtension('pytest', pytest_ver)
end

buildServer_pythonPackage "pytest-#{pytest_ver}" do
  archive_name "pytest-#{pytest_ver}#{pytest_ext}"
  archive_location node['buildServer']['download_location']
  extract_location node['buildServer']['python']['extract_location']
  repo_url node['buildServer']['repo_url']
  action :install
  ignore_failure true
end

record = "pytest,#{pytest_ver},python_modules,python-pytest,#{arch},#{pytest_ext},\
pytest-#{pytest_ver}#{pytest_ext}"

buildServer_log "pytest" do
  name         "pytest"
  log_location node['log_location']
  log_record   record
  action       :add
  ignore_failure true
  only_if { Dir.exist?("#{extract_location}/pytest-#{pytest_ver}") }
end
