# Installs perl module "file-remove" and "module-install" using source and build method.
# source to be built is hosted at autoport_repo in tar.gz archive format.

include_recipe 'buildServer::perl'

arch = node['kernel']['machine']

case node['platform']
  when 'ubuntu'
    tag = {
           'File-Remove' => 'libfile-remove-perl',
           'Module-Install' => 'libmodule-install-perl'
          }
  when 'redhat'
     tag = {
           'File-Remove' => 'perl-File-Remove',
           'Module-Install' => 'perl-Module-Install'
          }
end

fr_version = node['buildServer']['File-Remove']['version']
mi_version = node['buildServer']['Module-Install']['version']
extract_location = node['buildServer']['perl']['extract_location']

{
  'File-Remove'    => [ fr_version,  tag['File-Remove'] ], 
  'Module-Install' => [ mi_version, tag['Module-Install'] ]
}.each do |pkg, detail|
  buildServer_perlPackage "#{pkg}-#{detail[0]}" do
    archive_name "#{pkg}-#{detail[0]}.tar.gz"
    archive_location node['buildServer']['download_location']
    extract_location node['buildServer']['perl']['extract_location']
    perl_prefix_dir node['buildServer']['perl']['prefix_dir']
    repo_location node['buildServer']['repo_url']
    action :install
    ignore_failure true
   end

  log_record = "#{pkg},#{detail[0]},perl_modules,#{detail[1]},#{arch},.tar.gz,#{pkg}-#{detail[0]}.tar.gz"
  buildServer_log pkg do
    name         pkg
    log_location node['log_location']
    log_record   log_record
    action       :add
    ignore_failure true
    only_if { Dir.exist?("#{extract_location}/#{pkg}-#{detail[0]}") }
  end
end
