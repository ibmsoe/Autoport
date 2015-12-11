# Installs perl module "test-strict" using source and build method.
# source to be built is hosted at autoport_repo.

Chef::Recipe.send(:include, ArchiveLog)

include_recipe 'buildServer::perl'

arch = node['kernel']['machine']
ts_version = node['buildServer']['Test-Strict']['version']
ts_ext = node['buildServer']['Test-Strict']['ext']
extract_location = node['buildServer']['perl']['extract_location']

if ts_ext.empty?
  ts_ext = ArchiveLog.getExtension('Test-Strict', ts_version)
end

buildServer_perlPackage "Test-Strict-#{ts_version}" do
  archive_name "Test-Strict-#{ts_version}#{ts_ext}"
  archive_location node['buildServer']['download_location']
  extract_location node['buildServer']['perl']['extract_location']
  perl_prefix_dir node['buildServer']['perl']['prefix_dir']
  repo_location node['buildServer']['repo_url']
  action :install
  ignore_failure true
end

case node['platform']
  when 'ubuntu'
    record = "Test-Strict,#{ts_version},perl_modules,libtest-strict-perl,\
#{arch},#{ts_ext},Test-Strict-#{ts_version}#{ts_ext}"
  when 'redhat'
    record = "Test-Strict,#{ts_version},perl_modules,perl-test-strict,\
#{arch},#{ts_ext},Test-Strict-#{ts_version}#{ts_ext}"
end


buildServer_log 'Test-Strict' do
  name         "Test-Strict"
  log_location node['log_location']
  log_record   record
  action       :add
  ignore_failure true
  only_if { Dir.exist?("#{extract_location}/Test-Strict-#{ts_version}") }
end
