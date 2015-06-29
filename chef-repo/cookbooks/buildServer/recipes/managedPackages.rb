# This recipe uses the respective package manager to install
# the packages using the "package" resource of chef.
# Few of the packages are not directly available
# via official mirrors and are hosted over custom repository.
# These are scala,scons, sbt.

# List of packages common to both architecture and distributions.
pkg_list = [
  'git',
  'make',
  'ant',
  'snappy',
  'autoconf',
  'libtool',
  'automake',
  'make',
  'tcl',
  'python-setuptools',
  'ruby',
  'cmake',
  'scons',
  'sbt'
]

case node[:platform]
when 'ubuntu'
  # List of pacakges for ubuntu
  deb_list = [
    'g++',
    'openjdk-7-jdk',
    'zlibc',
    'zlib1g',
    'zlib1g-dev',
    'liblzo2-2',
    'liblzo2-dev',
    'lzop',
    'python-lzo',
    'libpath-tiny-perl',
    'libyaml-tiny-perl',
    'python-pytest',
    'ruby',
    'scala',
    'gradle',
    'nodejs',
    'npm'
  ]
  pkg_list.push(*deb_list)
when 'redhat'
  # Common list of rhel packages available over both x86 and ppc64le
  rpm_list = [
    'gcc-c++',
    'java-1.7.0-openjdk',
    'zlib',
    'zlib-devel',
    'lzo',
    'perl-CPAN'
  ]

  if node['kernel']['machine'] == 'x86_64'
    # List of pacakges specific to x_86
    rpm_x_86_list = [
      'scala'
    ]
    rpm_list.push(*rpm_x_86_list)
  elsif node['kernel']['machine'] == 'ppc64le'
    # List of pacakges specific to ppc64le
    rpm_ppcle_list = [
      'maven',
      'perl-File-Remove',
      'python-py'
    ]
    rpm_list.push(*rpm_ppcle_list)
  end
  pkg_list.push(*rpm_list)
end

pkg_list.each do |pkg|
  package pkg do
    action :install
    options '--force-yes'
  end
end
