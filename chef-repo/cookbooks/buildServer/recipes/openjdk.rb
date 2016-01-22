# This recipe installs java package using package manager.

java_packages = {}
version_arr = node['buildServer']['openjdk']['version']
arch = ''

if node['kernel']['machine'] == 'x86_64'
  arch = 'amd64'
elsif node['kernel']['machine'] == 'ppc64le'
  arch = 'ppc64el'
end

case node['platform']
when 'ubuntu'
  if version_arr.kind_of?(Array) and version_arr.any?
    version_arr.each do |version|
      java_packages[version] = {
                                'pkgs' => [
                                           "openjdk-#{version}-jre-headless",
                                           "openjdk-#{version}-jre",
                                           "openjdk-#{version}-jdk"
                                          ],
                                'home' => "/usr/lib/jvm/java-#{version}-openjdk-#{arch}"
                               }
    end
  end
  opt = '--force-yes'
when 'redhat', 'centos'
  if version_arr.kind_of?(Array) and version_arr.any?
    version_arr.each do |version|
      java_packages[version] = {
                                'pkgs' => [
                                           "java-1.#{version}.0-openjdk",
                                           "java-1.#{version}.0-openjdk-devel"
                                          ],
                                'home' => "/usr/lib/jvm/java-1.#{version}.0-openjdk"
                               }
    end
  end
  opt = ''
end

if java_packages.kind_of?(Hash) and java_packages.any?
  java_packages.each do |key, value|
    value['pkgs'].each do |pkg|
      package pkg do
        action :install
        options opt
        ignore_failure true
      end
    end

    template "/opt/openjdk-#{key}.sh" do
      owner 'root'
      group 'root'
      source 'openjdk.sh.erb'
      mode '0644'
      variables(
        java_home: value['home']
      )
      only_if { Dir.exist?(value['home']) }
      ignore_failure true
    end
  end
end
