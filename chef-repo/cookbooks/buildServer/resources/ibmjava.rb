# This resource is used to install/remove ibm-java of a specific version on the target node 

actions :install, :remove

attribute :name, name_attribute: true, kind_of: String
attribute :version,       kind_of: String
attribute :install_dir,   kind_of: String
attribute :uninstall_dir, kind_of: String
attribute :repo_url,      kind_of: String
attribute :arch,          kind_of: String

def initialize(*args)
  super
end

