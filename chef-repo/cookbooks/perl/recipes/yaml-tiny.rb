# Installs yaml-tiny 1.64 using source/build
{
  'YAML-Tiny' => node['perl']['yaml_tiny']['version']
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
