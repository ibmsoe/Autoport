# Installing buildtools for each x_86 machines.
# build-essentials is a reference for all the packages needed to compile a debian package.
# Development tools is a reference to all packages needed to compile software and build new rpms.

if node['kernel']['machine'] == 'x86_64'
  case node['platform']
  when 'ubuntu'
    package 'build-essential'
  when 'redhat'
    yum_cmd = 'yum groupinstall'
    execute 'Installing development tools' do
      command "#{yum_cmd} 'Development Tools' -y"
      not_if "#{yum_cmd} installed | grep 'Development Tools'"
    end
  end
end
