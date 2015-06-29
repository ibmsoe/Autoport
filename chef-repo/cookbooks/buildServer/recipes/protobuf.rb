protobuf_pkgs = []
case node['platform']
when 'ubuntu'
  if node['lsb']['release'] == '14.04'
    protobuf_pkgs = [
      'libprotobuf8',
      'libprotobuf-dev',
      'protobuf-compiler',
      'libprotobuf-java',
      'python-protobuf'
    ]
  end
when 'redhat'
  protobuf_pkgs = [
    'protobuf',
    'protobuf-devel',
    'protobuf-compiler',
    'protobuf-python'
  ]
end

if protobuf_pkgs.any?
  protobuf_pkgs.each do |pkg|
    package pkg do
      action :install
      options '--force-yes'
    end
  end
end
