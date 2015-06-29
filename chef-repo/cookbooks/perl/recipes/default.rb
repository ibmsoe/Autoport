# Installs perl and perl modules using source/build method

include_recipe 'perl::perl'
include_recipe 'perl::module-install'
include_recipe 'strict-perl'
include_recipe 'test-strict'
include_recipe 'yaml-tiny'
