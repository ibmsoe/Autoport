# This recipe would be responsible for installing python modules
# uploaded via autoport application. Each perl module uploaded is
# expected in tar.gz format and would be installed via source/build method.

if node['buildServer']['python_modules'].any?
  node['buildServer']['python_modules'].each do |pkg, version|

    buildServer_pythonPackage "#{pkg}-#{version}" do
      archive_name "#{pkg}-#{version}.tar.gz"
      archive_location node['buildServer']['download_location']
      extract_location node['buildServer']['python']['extract_location']
      repo_url node['buildServer']['repo_url']
      action :install
    end

    buildServer_log pkg do
      name         pkg
      log_location node['log_location']
      log_record = "#{pkg},#{version},python_modules,#{pkg},#{pkg}-#{version}"
      action       :add
    end
  end
end
