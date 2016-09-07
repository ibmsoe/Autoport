# Installs perl module "yaml-tiny" using source and build method.
# source to be built is hosted at autoport_repo .

include_recipe 'buildServer::get_log'
include_recipe 'buildServer::perl'

arch = node['kernel']['machine']
yt_version = node['buildServer']['YAML-Tiny']['version']
yt_ext = node['buildServer']['YAML-Tiny']['ext']
extract_location = node['buildServer']['perl']['extract_location']

if yt_ext.empty?
  yt_ext = ArchiveLog.getExtension('YAML-Tiny', yt_version)
end

buildServer_perlPackage "YAML-Tiny-#{yt_version}" do
  archive_name "YAML-Tiny-#{yt_version}#{yt_ext}"
  archive_location node['buildServer']['download_location']
  extract_location node['buildServer']['perl']['extract_location']
  perl_prefix_dir node['buildServer']['perl']['prefix_dir']
  repo_location node['buildServer']['repo_url']
  action :install
  ignore_failure true
end

case node['platform']
  when 'ubuntu'
    record = "YAML-Tiny,#{yt_version},perl_modules,libyaml-tiny-perl,\
#{arch},#{yt_ext},YAML-Tiny-#{yt_version}#{yt_ext}"
  when 'redhat', 'centos'
    record = "YAML-Tiny,#{yt_version},perl_modules,perl-yaml-tiny,\
#{arch},#{yt_ext},YAML-Tiny-#{yt_version}#{yt_ext}"
end

buildServer_log 'YAML-Tiny' do
  name         'YAML-Tiny'
  log_location node['log_location']
  log_record   record
  action       :add
  ignore_failure true
  only_if { Dir.exist?("#{extract_location}/YAML-Tiny-#{yt_version}") }
end
