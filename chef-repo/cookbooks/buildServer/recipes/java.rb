# This recipe installs java package using package manager.
# It is also responsible to configure java_home using java.sh in profile.d.

java_packages = []
version = node['buildServer']['java']['version']
arch = ''

if node['kernel']['machine'] == 'x86_64'
  arch = 'amd64'
elsif node['kernel']['machine'] == 'ppc64le'
  arch = 'ppc64le'
end

case node['platform']
when 'ubuntu'
  java_packages = [
    "openjdk-#{version}-jre",
    "openjdk-#{version}-jdk"
  ]
  java_home = "/usr/lib/jvm/java-1.#{version}.0"

when 'redhat'
  java_packages = [
    "java-1.#{version}.0-openjdk",
    "java-1.#{version}.0-openjdk-devel"
  ]
  java_home = "/usr/lib/jvm/java-#{version}-openjdk-#{arch}"
end

if java_packages.any?
  java_packages.each do |pkg|
    package pkg do
      action :install
      options '--force-yes'
    end
  end

  template '/etc/profile.d/java.sh' do
    owner 'root'
    group 'root'
    source 'java.sh.erb'
    mode '0644'
    variables(
      java_home: java_home
    )
  end
end
