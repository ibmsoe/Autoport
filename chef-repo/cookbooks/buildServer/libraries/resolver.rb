# This library is added to resolve the warnings that were seen while doing a bootstrap
# on power build slaves.

module Resolver
  Chef.set_resource_priority_array(:package, [ Chef::Resource::YumPackage ], platform: 'redhat')
  Chef.set_resource_priority_array(:package, [ Chef::Resource::AptPackage ], platform: 'ubuntu')
end
