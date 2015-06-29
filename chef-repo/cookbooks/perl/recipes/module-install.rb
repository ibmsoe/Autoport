# Installs perl module file-remove 1.52 and module-install 1.14 using source/build method
{
  'File-Remove'    => node['perl']['file-remove']['version'],
  'Module-Install' => node['perl']['module-install']['version']
}.each do |pkg, version|
  perl_package "#{pkg}-#{version}" do
    archive_name "#{pkg}-#{version}.tar.gz"
    archive_location node['perl']['archive_location']
    extract_location node['perl']['download_location']
    perl_prefix_dir node['perl']['prefix_dir']
    repo_location node['perl']['repo_url']
    action :install
  end
end
