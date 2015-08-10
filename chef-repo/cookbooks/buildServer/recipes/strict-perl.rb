# Installs perl module "strict-perl" using source and build method.
# source to be built is hosted at autoport_repo in tar.gz archive format.

include_recipe 'buildServer::perl'

{
  'Strict-Perl' => node['buildServer']['Strict-Perl']['version']
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

log_record = "Strict-Perl,#{node['buildServer']['Strict-Perl']['version']},perl_modules"

buildServer_log 'Strict-Perl' do
  name         'Strict-Perl'
  log_location node['log_location']
  log_record   log_record
  action       :add
end

