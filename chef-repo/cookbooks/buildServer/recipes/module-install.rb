# Installs perl module "file-remove" and "module-install" using source and build method.
# source to be built is hosted at autoport_repo.

include_recipe 'buildServer::get_log'
include_recipe 'buildServer::perl'

arch = node['kernel']['machine']

case node['platform']
  when 'ubuntu'
    tag = {
           'File-Remove' => 'libfile-remove-perl',
           'Module-Install' => 'libmodule-install-perl'
          }
  when 'redhat', 'centos'
     tag = {
           'File-Remove' => 'perl-File-Remove',
           'Module-Install' => 'perl-Module-Install'
          }
end

fr_version = node['buildServer']['File-Remove']['version']
fr_ext = node['buildServer']['File-Remove']['ext']
mi_version = node['buildServer']['Module-Install']['version']
mi_ext = node['buildServer']['Module-Install']['ext']
extract_location = node['buildServer']['perl']['extract_location']

{
  'File-Remove'    => [ fr_version,  tag['File-Remove'], fr_ext ], 
  'Module-Install' => [ mi_version, tag['Module-Install'], mi_ext ]
}.each do |pkg, detail|
  
  if detail[2].empty?
    detail[2] = ArchiveLog.getExtension(pkg, detail[0])
  end

  buildServer_perlPackage "#{pkg}-#{detail[0]}" do
    archive_name "#{pkg}-#{detail[0]}#{detail[2]}"
    archive_location node['buildServer']['download_location']
    extract_location node['buildServer']['perl']['extract_location']
    perl_prefix_dir node['buildServer']['perl']['prefix_dir']
    repo_location node['buildServer']['repo_url']
    action :install
    ignore_failure true
   end

  log_record = "#{pkg},#{detail[0]},perl_modules,#{detail[1]},#{arch},#{detail[2]},#{pkg}-#{detail[0]}#{detail[2]}"
  buildServer_log pkg do
    name         pkg
    log_location node['log_location']
    log_record   log_record
    action       :add
    ignore_failure true
    only_if { Dir.exist?("#{extract_location}/#{pkg}-#{detail[0]}") }
  end
end
