# Installs python py module 1.4.26 using source/build
{
  'py'    => node['python']['py']['version']
}.each do |pkg, version|
  python_package "#{pkg}-#{version}" do
    archive_name "#{pkg}-#{version}.tar.gz"
    archive_location node['python']['archive_location']
    extract_location node['python']['download_location']
    repo_url node['python']['repo_url']
    action :install
  end
end
