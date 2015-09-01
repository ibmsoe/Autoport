# Installs python module "py" using source and build method.
# source to be built is hosted at autoport_repo in tar.gz archive format.

py_version = node['buildServer']['py']['version']
arch       = node['kernel']['machine']

{
  'py'    => py_version
}.each do |pkg, version|
   buildServer_pythonPackage "#{pkg}-#{version}" do
      archive_name "#{pkg}-#{version}.tar.gz"
      archive_location node['buildServer']['download_location']
      extract_location node['buildServer']['python']['extract_location']
      repo_url node['buildServer']['repo_url']
      action :install
   end
end

record = "py,#{py_version},python_modules,python-py,#{arch},.tar.gz,py-#{py_version}.tar.gz"

buildServer_log "py" do
  name         "py"
  log_location node['log_location']
  log_record   record
  action       :add
end
