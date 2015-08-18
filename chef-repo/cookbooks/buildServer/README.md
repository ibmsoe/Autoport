buildServer Cookbook
====================
This cookbook is meant to pre-condition the build slaves of autoport tool with identified set of Managed Packages.

+----------------+---------------------+--------------------------+------------------------------------+----------------+
|    Package     | Installation Recipe |     Uninstall Recipe     |        Supported Extensions        |  Install Type  |
+----------------+---------------------+--------------------------+------------------------------------+----------------+
|      ant       |    ant_binary.rb    |   ant_binary_remove.rb   | .tar,.tar.gz,.tar.bz2,.tar.xz,.zip | Binary install |
|     maven      |   maven_binary.rb   |  maven_binary_remove.rb  | .tar,.tar.gz,.tar.bz2,.tar.xz,.zip | Binary install |
|     scala      |   scala_binary.rb   |  scala_binary_remove.rb  | .tar,.tar.gz,.tar.bz2,.tar.xz,.zip | Binary install |
|     gradle     |   gradle_binary.rb  |     gradle_binary.rb     | .tar,.tar.gz,.tar.bz2,.tar.xz,.zip | Binary install |
|    protobuf    | protobuf_source.rb  | gradle_source_remove.rb  | .tar,.tar.gz,.tar.bz2,.tar.xz,.zip | Source Install |
|  ibm-java-sdk  |   ibm-java-sdk.rb   |  ibm-java-sdk_remove.rb  |                .bin                | Binary install |
| ibm-sdk-nodejs |  ibm-sdk-nodejs.rb  | ibm-sdk-nodejs_remove.rb |                .bin                | Binary install |
|      perl      |       perl.rb       |            NA            |              .tar.gz               | Source Install |
|       py       |        py.rb        |            NA            |              .tar.gz               | Source Install |
|     pytest     |      pytest.rb      |            NA            |              .tar.gz               | Source Install |
|  strict-perl   |    strict-perl.rb   |            NA            |              .tar.gz               | Source Install |
| module-install |  module-install.rb  |            NA            |              .tar.gz               | Source Install |
|  test-strict   |     test-strict     |            NA            |              .tar.gz               | Source Install |
|   yaml-tiny    |     test-strict     |            NA            |              .tar.gz               | Source Install |
+----------------+---------------------+--------------------------+------------------------------------+----------------+

Wrapper Recipes:
+---------------------+-----------------------------------------------------------------------------------------------------------------------+
|        Recipe       |                                                        Comments                                                       |
+---------------------+-----------------------------------------------------------------------------------------------------------------------+
|        ant.rb       | Wrapper recipe to install ant via package Manager if available. Else installing via binary.                           |
|       maven.rb      | Wrapper recipe to install maven via package Manager if available. Else installing via binary.                         |
|       scala.rb      | Wrapper recipe to install scala via package Manager if available. Else installing via binary.                         |
|      gradle.rb      | Wrapper recipe to install gradle via package Manager if available. Else installing via binary.                        |
|     protobuf.rb     | Wrapper recipe to install protobuf via package Manager if available. Else installing via binary.                      |
| autoportPackages.rb | To install all packages in autoportPackages section of ManagedList.json using underlying package Manager              |
|   repo_settings.rb  | Configuring custom repository on nodes                                                                                |
|    buildTools.rb    | Installing build-essentials / Development tools if available via package Manager                                      |
|   userPackages.rb   | Installing packages in userPackages section of ManagedList.json using underlying package Manager                      |
|      default.rb     | The outermost wrapper to call all the recipes part of cookbook , while synching up build-slaves                       |
|                     |                                                                                                                       |
+---------------------+-----------------------------------------------------------------------------------------------------------------------+

NOTE: Multiple Extension support and Uninstallation are only available for binary packages and not for source installations.

Requirements
------------
This cookbook supports:
1. Architecture: x86_64, ppc64le
2. Distributions: RHEL, UBUNTU


Attributes
----------
Each package(archive) has an associated set of data values which are defined in
terms of attributes.
Following are common set of attributes defined for each package:
NOTE: <pkg-identifier>: This string maps to package name in autoportChefPackages section of ManagedList.json.
 1. default['buildServer'][<pkg-identifier>]['version']
    - This specifies the version of the package(archive).
      There is a default value specified however, this gets overridden at runtime based on ManagedList.json
      or based on user selection on the single panel.
      Specifying default is not mandatory. Default values would allow recipes as standalone.
      Also it ensures that there is a value always available to fallback in case of any errors during overriding.
 2. default['buildServer'][<pkg-identifier>]['install_dir']
     - This specifies the path where the package(archive) is installed. By default all the packages
       are installed in /opt or in subdirectories of /opt. This never gets overridden as there is no provision to change
       default installation location via autoport tool at runtime.
 3. default['buildServer'][<pkg-identifier>]['extension']
     - This specifies the archive extension. There is a default value specified.
       This value gets overridden at runtime based on package(archive) selected during installation
       by the user. The default value for the extension is mandatory, since during the synch operation
       the package extension is not available either via ManagedList.json or via user selection.

Usage
----------
To run all the recipes of the cookbook use

buildServer::default
