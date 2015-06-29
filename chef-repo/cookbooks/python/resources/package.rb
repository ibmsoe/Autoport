actions :install

attribute :name, name_attribute: true, kind_of: String
attribute :archive_name,     kind_of: String
attribute :archive_location, kind_of: String
attribute :extract_location, kind_of: String
attribute :repo_url,         kind_of: String

def initialize(*args)
  super
  @action = [:install]
end
