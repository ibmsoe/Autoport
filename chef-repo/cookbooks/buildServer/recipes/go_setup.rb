# Setting up a go workspace to install go packages.
# Note that we will not set GOPATH in profile as it will differ for each
# project being built. The workspace created below is for the go
# projects that are installed as a dependency, i.e Managed Runtime
# for "go" projects.

%w[ /opt/go /opt/go/src /opt/go/bin /opt/go/pkg ].each do |path|
  directory path do
    owner 'root'
    group 'root'
    mode  '0777'
  end
end
