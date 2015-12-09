# Installs perl module "yaml-tiny" using source and build method.
# source to be built is hosted at autoport_repo in tar.gz archive format.

include_recipe 'buildServer::perl'

arch = node['kernel']['machine']
yt_version = node['buildServer']['YAML-Tiny']['version']
extract_location = node['buildServer']['perl']['extract_location']

{
  'YAML-Tiny' => yt_version
}.each do |pkg, version|
  buildServer_perlPackage "#{pkg}-#{version}" do
    archive_name "#{pkg}-#{version}.tar.gz"
    archive_location node['buildServer']['download_location']
    extract_location node['buildServer']['perl']['extract_location']
    perl_prefix_dir node['buildServer']['perl']['prefix_dir']
    repo_location node['buildServer']['repo_url']
    action :install
    ignore_failure true
  end
end

case node['platform']
  when 'ubuntu'
    record = "YAML-Tiny,#{yt_version},perl_modules,libyaml-tiny-perl,\
#{arch},.tar.gz,YAML-Tiny-#{yt_version}.tar.gz"
  when 'redhat'
    record = "YAML-Tiny,#{yt_version},perl_modules,perl-yaml-tiny,\
#{arch},.tar.gz,YAML-Tiny-#{yt_version}.tar.gz"
end

buildServer_log 'YAML-Tiny' do
  name         'YAML-Tiny'
  log_location node['log_location']
  log_record   record
  action       :add
  ignore_failure true
  only_if { Dir.exist?("#{extract_location}/YAML-Tiny-#{yt_version}") }
end
