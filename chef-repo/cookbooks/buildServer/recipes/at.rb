# Creating file to set environment variable for power-advance-toolchain
# Commented part of the code is meant to install power-advance-tool-chain
# in case if we want make it part of default ManagedRuntme rather than it
# being treated as user-added package.

arch = node['kernel']['machine']
#version = node['at']['version']

if arch == 'ppc64le'

  #case node[:platform]
  #when 'ubuntu'
  #  opt = '--force-yes'
  #when 'redhat', 'centos'
  #  opt = ''
  #end

  #pkgs = [
  #         "advance-toolchain-at#{version}-runtime",
  #         "advance-toolchain-at#{version}-devel",
  #         "advance-toolchain-at#{version}-perf",
  #         "advance-toolchain-at#{version}-mcore-libs",
  #       ]

  #pkgs.each do |pkg_name|
  #  package "Installing managed #{pkg_name}" do
  #    package_name   pkg_name
  #    action         :install
  #    options        opt
  #    ignore_failure true
  #  end
  #end

  cookbook_file '/etc/profile.d/at.sh' do
    source 'at.sh'
    owner 'root'
    group 'root'
    mode '0644'
    ignore_failure true
  end

end
