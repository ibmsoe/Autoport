# Installs python module "pytest" using source and build method.
# source to be built is hosted at autoport_repo in tar.gz archive format.

{
  'pytest'    => node['buildServer']['pytest']['version']
}.each do |pkg, version|
  buildServer_pythonPackage "#{pkg}-#{version}" do
    archive_name "#{pkg}-#{version}.tar.gz"
    archive_location node['buildServer']['download_location']
    extract_location node['buildServer']['python']['extract_location']
    repo_url node['buildServer']['repo_url']
    action :install
  end
end

log_record = "pytest,#{node['buildServer']['pytest']['version']},python_modules,python-pytest"

buildServer_log "pytest" do
  name         "pytest"
  log_location node['log_location']
  log_record   log_record
  action       :add
end
