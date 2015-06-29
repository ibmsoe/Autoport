# This recipe is to install packages in the userlist of managedlist.json.
# userpackages would be passed as a json string to the recipe and would be
# fetched as dictionary key-value pairs.
# Example:
#  "userpackages"{
#      "package1": "install",
#      "package2": "remove",
#      "package3": "install",
#    }

node.default['userpackages'] = node['userpackages']
JSON[node.default['userpackages']]

node.default['userpackages'].each do |pkg, action|
  package pkg do
    action action.to_sym
    options '--force-yes'
  end
end
