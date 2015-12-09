# This recipe would be responsible for installing python modules
# uploaded via autoport application. Each perl module uploaded is
# expected in tar.gz format and would be installed via source/build method.

arch = node['kernel']['machine']
extract_location = node['buildServer']['python']['extract_location']

if node['buildServer']['python_modules'].any?
  node['buildServer']['python_modules'].each do |pkg, version|

    buildServer_pythonPackage "#{pkg}-#{version}" do
      archive_name "#{pkg}-#{version}.tar.gz"
      archive_location node['buildServer']['download_location']
      extract_location node['buildServer']['python']['extract_location']
      repo_url node['buildServer']['repo_url']
      action :install
      ignore_failure true
    end

    record = "#{pkg},#{version},python_modules,#{pkg},#{arch},.tar.gz,#{pkg}-#{version}.tar.gz"

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
