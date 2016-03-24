buildServer Cookbook
====================
This cookbook is meant to install identified Managed Runtime packages on each of the build slaves.


| Package        | Installation Recipe | Uninstall Recipe          | Supported Extensions               | Install Type    |
|----------------|---------------------|---------------------------|------------------------------------|-----------------|
| ant            | ant_binary.rb       | ant_binary_remove.rb      | .tar,.tar.gz,.tar.bz2,.tar.xz,.zip | Binary install  |
| maven          | maven_binary.rb     | maven_binary_remove.rb    | .tar,.tar.gz,.tar.bz2,.tar.xz,.zip | Binary install  |
| scala          | scala_binary.rb     | scala_binary_remove.rb    | .tar,.tar.gz,.tar.bz2,.tar.xz,.zip | Binary install  |
| gradle         | gradle_binary.rb    | gradle_binary_remove.rb   | .tar,.tar.gz,.tar.bz2,.tar.xz,.zip | Binary install  |
| protobuf       | protobuf_source.rb  | protobuf_source_remove.rb | .tar,.tar.gz,.tar.bz2,.tar.xz,.zip | Source Install  |
| ibm-java-sdk   | ibm-java-sdk.rb     | ibm-java-sdk_remove.rb    | .bin                               | Binary install  |
| ibm-sdk-nodejs | ibm-sdk-nodejs.rb   | ibm-sdk-nodejs_remove.rb  | .bin                               | Binary install  |
| perl           | perl.rb             | NA                        | .tar.gz                            | Source Install  |
| py             | py.rb               | NA                        | .tar.gz                            | Source Install  |
| pytest         | pytest.rb           | NA                        | .tar.gz                            | Source Install  |
| strict-perl    | strict-perl.rb      | NA                        | .tar.gz                            | Source Install  |
| module-install | module-install.rb   | NA                        | .tar.gz                            | Source Install  |
| test-strict    | test-strict.rb      | NA                        | .tar.gz                            | Source Install  |
| yaml-tiny      | yaml-tiny.rb        | NA                        | .tar.gz                            | Source Install  |
| cmake          | cmake.rb            | NA                        | NA                                 | Package Manager |
| openjdk        | openjdk.rb          | NA                        | NA                                 | Package Manager |
| perl_module    | perl_modules.rb     | NA                        | .tar.gz                            | Source Install  |
| python modules | python_modules.rb   | NA                        | .tar.gz                            | Source Install  |


Wrapper Recipes:

| Recipe              | Comments                                                                                                           |
|---------------------|--------------------------------------------------------------------------------------------------------------------|
| ant.rb              | Wrapper recipe to install ant via package-manager or else via binary based on appropriate attribute value set      |
| maven.rb            | Wrapper recipe to install maven via package-manager or else via binary based on appropriate attribute value set    |
| scala.rb            | Wrapper recipe to install scala via package-manager or else via binary based on appropriate attribute value set    |
| gradle.rb           | Wrapper recipe to install gradle via package-manager or else via binary based on appropriate attribute value set   |
| protobuf.rb         | Wrapper recipe to install protobuf via package-manager or else via source based on appropriate attribute value set |
| autoportPackages.rb | To install all packages in autoportPackages section of ManagedList.json using underlying package-manager           |
| repo_settings.rb    | Configuring Autoport's custom repository on nodes                                                                  |
| java.rb             | Wrapper recipe to install openjdk and ibm-java                                                                     |
| buildTools.rb       | Installing build-essentials / Development tools if available via package-manager                                   |
| default.rb          | The outermost wrapper to call all the recipes required for synching up build-slaves                                |


Supported Distro and Arch
=========================
This cookbook supports:
* Architecture: x86_64, ppc64le
* Distributions: RHEL, UBUNTU, CentOS

Usage
======
This cookbook is run via Autoport tool by overriding default attributes, whose values are fetched
from latest `data/ManagedList.json file`.

Although to run it independently set/override attributes (check attributes/default.rb for complete list) and set
the run_list appropriately as

* `buildServer::<recipe-name>`
* `buildServer::default` (To run all recipes used during synch)
