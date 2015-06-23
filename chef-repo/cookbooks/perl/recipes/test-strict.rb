# Installs test-strict 0.26 using source/build.

{
  'Test-Strict' => node['perl']['test-strict']['version']
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
