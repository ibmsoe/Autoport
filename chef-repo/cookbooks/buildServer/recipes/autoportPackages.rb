# This recipe to install packages that are directly available as os-install
# using package manager (apt/yum).
# This maps to the packages in the autoportPackages section of ManagedList.json

case node['platform']
when 'ubuntu'
  pkgs = node['buildServer']['debs']
  opt = '--force-yes' 
  check_expression = "apt-cache policy" 
when 'redhat'
  pkgs = node['buildServer']['rpms']
  opt = ''
  check_expression = "yum info"
end

if pkgs.any?
  pkgs.each do |pkg_name,version|
    if version
      package pkg_name do
        action         :install
        options        opt
        version        version
        ignore_failure true
        only_if "#{check_expression} #{pkg_name}"
      end

    else
      package pkg_name do
        action         :upgrade
        options        opt
        ignore_failure true
        only_if "#{check_expression} #{pkg_name}"
      end
    end
  end
end
