# Installs python module "pytest" using source and build method.
# source to be built is hosted at autoport_repo in tar.gz archive format.

pytest_ver = node['buildServer']['pytest']['version']
arch       = node['kernel']['machine']
extract_location = node['buildServer']['python']['extract_location']

{
  'pytest'    => pytest_ver
}.each do |pkg, version|
  buildServer_pythonPackage "#{pkg}-#{version}" do
    archive_name "#{pkg}-#{version}.tar.gz"
    archive_location node['buildServer']['download_location']
    extract_location node['buildServer']['python']['extract_location']
    repo_url node['buildServer']['repo_url']
    action :install
    ignore_failure true
  end
end

record = "pytest,#{pytest_ver},python_modules,python-pytest,#{arch},.tar.gz,\
pytest-#{pytest_ver}.tar.gz"

buildServer_log "pytest" do
  name         "pytest"
  log_location node['log_location']
  log_record   record
  action       :add
  ignore_failure true
  only_if { Dir.exist?("#{extract_location}/pytest-#{pytest_ver}") }
end
