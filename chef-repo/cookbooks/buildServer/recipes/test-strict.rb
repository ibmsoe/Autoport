# Installs perl module "test-strict" using source and build method.
# source to be built is hosted at autoport_repo in tar.gz archive format.

include_recipe 'buildServer::perl'

ts_version = node['buildServer']['Test-Strict']['version']

{
  'Test-Strict' => ts_version
}.each do |pkg, version|
  buildServer_perlPackage "#{pkg}-#{version}" do
    archive_name "#{pkg}-#{version}.tar.gz"
    archive_location node['buildServer']['download_location']
    extract_location node['buildServer']['perl']['extract_location']
    perl_prefix_dir node['buildServer']['perl']['prefix_dir']
    repo_location node['buildServer']['repo_url']
    action :install
  end
end

case node['platform']
  when 'ubuntu'
    log_record = "Test-Strict,#{ts_version},perl_modules,libtest-strict-perl,Test-Strict-#{ts_version}.tar.gz"
  when 'redhat'
    log_record = "Test-Strict,#{ts_version},perl_modules,perl-test-strict,Test-Strict-#{ts_version}.tar.gz"
end


buildServer_log 'Test-Strict' do
  name         'Test-Strict'
  log_location node['log_location']
  log_record   log_record
  action       :add
end

