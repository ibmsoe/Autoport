# Installs perl module "file-remove" and "module-install" using source and build method.
# source to be built is hosted at autoport_repo in tar.gz archive format.

include_recipe 'buildServer::perl'

{
  'File-Remove'    => node['buildServer']['File-Remove']['version'],
  'Module-Install' => node['buildServer']['Module-Install']['version']
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
    tag = {
           'File-Remove' => 'libfile-remove-perl',
           'Module-Install' => 'libmodule-install-perl'
          }
  when 'redhat'
     tag = {
           'File-Remove' => 'perl-file-remove',
           'Module-Install' => 'perl-module-install'
          }
end

fr_version = node['buildServer']['File-Remove']['version']
mi_version = node['buildServer']['Module-Install']['version']

{
 'File-Remove' => "File-Remove,#{fr_version},perl_modules,#{tag['File-Remove']},File-Remove-#{fr_version}.tar.gz" ,
 'Module-Install' => "Module-Install,#{mi_version},perl_modules,#{tag['Module-Install']},Module-Install-#{mi_version}.tar.gz"
}.each do |name, log_record|
  puts log_record
  buildServer_log name do
    name         name
    log_location node['log_location']
    log_record   log_record
    action       :add
  end
end
