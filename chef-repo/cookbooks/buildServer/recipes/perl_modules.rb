# This recipe would be responsible for installing perl modules
# uploaded via autoport application. Each perl module uploaded, is
# expected in tar.gz format and would be installed via source/build method.

include_recipe 'buildServer::perl'

if node['buildServer']['perl_modules'].any?

  node['buildServer']['perl_modules'].each do |pkg, version|

    buildServer_perlPackage "#{pkg}-#{version}" do
      archive_name "#{pkg}-#{version}.tar.gz"
      archive_location node['buildServer']['download_location']
      extract_location node['buildServer']['perl']['extract_location']
      perl_prefix_dir node['buildServer']['perl']['prefix_dir']
      repo_location node['buildServer']['repo_url']
      action :install
    end

    buildServer_log pkg do
      name         pkg
      log_location node['log_location']
      log_record   "#{pkg},#{version},perl_modules,#{pkg},#{pkg}-#{version}.tar.gz"
      action       :add
    end
  end
end
