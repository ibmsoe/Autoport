# This recipe to install packages that are directly available as os-install
# using package manager (apt/yum).
# This maps to the packages in the autoportPackages section of ManagedList.json

pkgs = {}
case node['platform']
when 'ubuntu'
  pkgs = node['buildServer']['debs']
  opt = '--force-yes'
when 'redhat', 'centos'
  pkgs = node['buildServer']['rpms']
  opt = ''
end

if pkgs.any?
  pkgs.each do |pkg_name,version|
    if version
      package "Installing managed #{pkg_name}" do
        package_name   pkg_name
        action         :install
        options        opt
        version        version
        ignore_failure true
      end

    else
      package "Installing managed #{pkg_name}" do
        package_name   pkg_name
        action         :upgrade
        options        opt
        ignore_failure true
      end
    end
  end
end
