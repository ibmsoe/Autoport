# Installs perl module "strict-perl" using source and build method.
# source to be built is hosted at autoport_repo.

Chef::Recipe.send(:include, ArchiveLog)

include_recipe 'buildServer::perl'

arch = node['kernel']['machine']
sp_version = node['buildServer']['Strict-Perl']['version']
sp_ext = node['buildServer']['Strict-Perl']['ext']
extract_location = node['buildServer']['perl']['extract_location']

if sp_ext.empty?
  sp_ext = ArchiveLog.getExtension('Strict-Perl', sp_version)
end

buildServer_perlPackage "Strict-Perl-#{sp_version}" do
  archive_name "Strict-Perl-#{sp_version}#{sp_ext}"
  archive_location node['buildServer']['download_location']
  extract_location node['buildServer']['perl']['extract_location']
  perl_prefix_dir node['buildServer']['perl']['prefix_dir']
  repo_location node['buildServer']['repo_url']
  action :install
  ignore_failure true
end

record = "Strict-Perl,#{sp_version},perl_modules,Strict_perl,\
#{arch},#{sp_ext},Strict-Perl-#{sp_version}#{sp_ext}"

buildServer_log 'Strict-Perl' do
  name         'Strict-Perl'
  log_location node['log_location']
  log_record   record
  action       :add
  ignore_failure true
  only_if { Dir.exist?("#{extract_location}/Strict-Perl-#{sp_version}") }
end
