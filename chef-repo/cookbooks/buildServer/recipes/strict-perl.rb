# Installs perl module "strict-perl" using source and build method.
# source to be built is hosted at autoport_repo in tar.gz archive format.

include_recipe 'buildServer::perl'

arch = node['kernel']['machine']
sp_version = node['buildServer']['Strict-Perl']['version']
{
  'Strict-Perl' => sp_version
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

record = "Strict-Perl,#{sp_version},perl_modules,Strict_perl,\
#{arch},.tar.gz,Strict-Perl-#{sp_version}.tar.gz"

buildServer_log 'Strict-Perl' do
  name         'Strict-Perl'
  log_location node['log_location']
  log_record   log_record
  action       :add
end

