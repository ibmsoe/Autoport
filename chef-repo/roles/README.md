Overview
========

Create roles here, in either the Role Ruby DSL (.rb) or JSON (.json) files. To install roles on the server, use knife.

For example, create `roles/base_example.rb`:

    name "base_example"
    description "Example base role applied to all nodes."
    # List of recipes and roles to apply. Requires Chef 0.8, earlier versions use 'recipes()'.
    #run_list()
    # Attributes applied if the node doesn't have it set already.
    #default_attributes()
    # Attributes applied no matter what the node has set already.
    #override_attributes()

Then upload it to the Chef Server:

    knife role from file roles/base_example.rb

Autoport Specific Information
=============================
In case of Autoport we do not maintain and version control the roles.
Roles are created temporarily to hold specific run-list and override attributes for a specific knife bootstrap process.
Before every knife bootstrap process a role is created, populated with specific run list and attributes.
During the boostrap process this role is applied to the target node.
Roles are deleted as soon as knife bootstrap process ends.
