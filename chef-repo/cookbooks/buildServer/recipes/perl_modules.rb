# This recipe would be responsible for installing perl modules
# uploaded via autoport application. Each perl module uploaded
# would be installed via source/build method.

Chef::Recipe.send(:include, ArchiveLog)

include_recipe 'buildServer::perl'
arch = node['kernel']['machine']
extract_location = node['buildServer']['perl']['extract_location']

if node['buildServer']['perl_modules'].any?

  node['buildServer']['perl_modules'].each do |pkg, version|
    ext = ArchiveLog.getExtension(pkg, version)
    buildServer_perlPackage "#{pkg}-#{version}" do
      archive_name "#{pkg}-#{version}#{ext}"
      archive_location node['buildServer']['download_location']
      extract_location node['buildServer']['perl']['extract_location']
      perl_prefix_dir node['buildServer']['perl']['prefix_dir']
      repo_location node['buildServer']['repo_url']
      ignore_failure true
      action :install
    end

    record = "#{pkg},#{version},perl_modules,#{pkg},#{arch},#{ext},#{pkg}-#{version}#{ext}"
    buildServer_log pkg do
      name         pkg
      log_location node['log_location']
      log_record   record
      action       :add
      ignore_failure true
      only_if { Dir.exist?("#{extract_location}/#{pkg}-#{version}") }
    end
  end
end
