Overview
========

Every Chef installation needs a Chef Repository. This is the place where cookbooks, roles, config files and other artifacts for managing systems with Chef will live. For Autoport we use a standard default directory structure for chef-repo. The chef-repo is supposed to be located on workstation, which in our case is Jenkins Master. Autoport tool during initialization takes care of keeping chef-repo on Jenkins Master up to date and also uploading the latest version of cookbook on to the chef-server.

Repository Directories
======================

This repository contains several directories, and each directory contains a README file that describes what it is for in greater detail, and how to use it for managing your systems with Chef.

* `cookbooks/` - Cookbooks you download or create. Autoport work with a single cookbook `buildServer`
* `data_bags/` - Store data bags and items in .json in the repository. This is not being utilized currently for Autoport.
* `roles/` - Store roles in .rb or .json in the repository. This is not being utilized currently for Autoport.
* `environments/` - Store environments in .rb or .json in the repository. This is not being utilized currently for Autoport.

Configuration
=============

The repository contains a knife configuration file and a custom bootstrap template for autoport.

* .chef/knife.rb
* .chef/bootstrap/autoport_template.erb

The file `.chef/knife.rb` is a configuration file for knife with Autoport specific settings.
For more details on knife configuartion settings refer following sections in `docs/README-install.md`:
* Chef Installation And Setup on Jenkins Master
* Configuring Chef Workstation on Jenkins Master

Custom bootstrap template `autoport_template.erb` is created specifically to support installation of chef-client
on power architecture during knife bootstrap process.
