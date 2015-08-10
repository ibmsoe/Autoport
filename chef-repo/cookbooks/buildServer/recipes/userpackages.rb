# The recipe would install packages in the userPackages section of managedlist.json.
# userpackages would be passed as a json string.

case node['platform']
when 'ubuntu'
  opt = '--force-yes'
when 'redhat'
  opt = ''
end

userpackages = node['buildServer']['userpackages']
if userpackages.any?
  userpackages.each do |pkg_name, pkg_data|
    if pkg_data[0] == node['kernel']['machine']
      package pkg_name do
        action         pkg_data[2].to_sym
        options        opt
        version        pkg_data[1]
        ignore_failure true
      end
    end
  end
end
