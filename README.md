
# About Autoport

Automation of build and test infrastructure is needed to provide efficiencies
towards getting open source packages onto the Power Linux platform, and to ensure
no regressions of the Power-specific enablement occurs as the community
continues to enhance these packages.


Autoport provides a bridge between github.com and a Jenkins build cluster
allowing projects hosted at the former to be built and tested automatically
on the latter.  Autoport examines the content of projects to dynamically
produce build and test commands which it uses to program Jenkins.

A autoport installation is composed of the following servers:

* autoport
* jenkins master server
* N jenkins build servers

Autoport provides a managed runtime environment for Jenkins build servers
so that the requisite build tools and most commonly used packages such as
libsnappy-java, libblas, and protobuf are pre-installed.

Autoport supports programs written in C, C++, Java, Javascript, Python, Perl, PHP, Ruby, and Scala. 

To see Autoport in action:

https://crl.ptopenlab.com:8800/autoport?next=/autoport/project/


# Documentation

Documentation is available in the docs/ directory.
* [User Guide] (https://github.com/ibmsoe/Autoport/blob/master/docs/UserGuide.pdf)
* [Installation Guide] (https://github.com/ibmsoe/Autoport/blob/master/docs/README-install.md)

# Questions / Issues

Please create a project [issue] (https://github.com/ibmsoe/Autoport/issues) and include @ibmsoe/autoport in your comment.

# License

Autoport is licensed under the [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0)
