.. role:: bash(code)
   :language: bash

Dependencies for Deploying Autoport on Apache Server:
=====================================================

In order to deploy Autoport onto Apache server following dependencies need to be pre-installed:

1. Install **pip**, so that required python libraries can be installed with all required dependencies, **pip** can be installed as::
    * *On RHEL/Centos*::
        :bash:`sudo yum install python-pip`

    *  *On Ubuntu/Debian*::
        :bash:`sudo apt-get install python-pip`

2. If packages *python-devel* and *libevent-devel* are not already installed, install them as::
    * *On RHEL/Centos*::
         :bash:`yum install libevent-devel python-devel`

    *  *On Ubuntu/Debian*::
         :bash:`sudo apt-get install libevent-devel python-devel`

3. Now install python libraries using **pip** command::
    :bash:`sudo pip install Flask`

    :bash:`sudo pip install PyGithub`

    :bash:`sudo pip install requests`

    :bash:`sudo pip install paramiko`

    :bash:`sudo pip install threadpool`

    :bash:`sudo pip install diff-match-patch`

    :bash:`sudo pip install PyYaml`

    :bash:`sudo pip install flask-compress`

    :bash:`sudo pip install pytz`

    :bash:`sudo pip install python-novaclient`


4. Install **apache server**, if not already installed, refer following links for installation::
    * `Installing Apache on RHEL 6 <https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/6/html/Managing_Confined_Services/chap-Managing_Confined_Services-The_Apache_HTTP_Server.html#sect-Managing_Confined_Services-The_Apache_HTTP_Server-The_Apache_HTTP_Server_and_SELinux>`_
    * `Installing Apache on RHEL 7/CentOS <https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/7/html/System_Administrators_Guide/ch-Web_Servers.html>`_
    * `Installing Apache on Ubuntu/Debian <https://help.ubuntu.com/lts/serverguide/httpd.html>`_

5. Install **mod_wsgi** if not already installed as below::
    *  *On Ubuntu/Debian*::
        :bash:`sudo apt-get install libapache2-mod-wsgi`

        :bash:`sudo a2enmod mod-wsgi`

    * *On RHEL/Centos*::
        :bash:`sudo yum install mod_wsgi`

Deploying Autoport on Apache Server:
====================================

1. Checkout Autoport codebase from gerrit on your local machine.
2. Go to folder **configs**::
    :bash:`cd configs`

3. Make sure script **deploy_autoport.sh** has executable permissions, if not change the permission as::
    :bash:`chmod 755 deploy_autoport.sh`

4. Now execute the deployment script as a sudo user, with OS flavor(centos/ubuntu/rhel) as argument.::
    :bash:`sudo ./deploy_autoport.sh <os_flavor>`

5. On completion of the script Autoport application will be deployed and ready to served by Apache on port 80.


**Site can be accessed using link**::
    :bash:`http://<server_hostname>/autoport`

**Autoport logs can be found at location**::
    :bash:`/var/www/html/autoport/data/autoport.log`

**Server logs can be found at**::
    *For RHEL/CentOS*::
        :bash:`/var/log/httpd/error_log`

    *For Ubuntu*::
        :bash:`/var/log/apache2/error.log`


Jenkins master installation:
============================

1. Install Jenkins master as mentioned `here <http://pkg.jenkins-ci.org/debian/>`_
2. After installation of Jenkins Master, perform following steps::
    :bash:`mkdir /home/jenkins/jenkins_home`

    a. add line "JENKINS_HOME=/home/jenkins/jenkins_home" after the line "# jenkins home location" in below file. This folder will contain Build artifacts.
        :bash:`vi /etc/default/jenkins`

    b. Install Open-jdk-7::
        *Ubuntu*::
            :bash:`sudo apt-get install openjdk-7-jdk`
        *RHEL/CentOS*::
            :bash:`sudo yum install java-1.7.0-openjdk-devel`

    c. Install git::
        *Ubuntu*::
            :bash:`sudo apt-get install git-all`
        *RHEL/CentOS*::
            :bash:`sudo yum install git-all`

    d. Now Create a user named "jenkins" and add to Sudoers list with no password, by adding following line in file "/etc/sudoers"::
        :bash:`jenkins ALL=(ALL:ALL) NOPASSWD: ALL`

       after line::
           :bash:`%sudo    ALL=(ALL:ALL) ALL`

    e. Add FQDN for current host, if required, as its a Chef master dependency. For example, if soe-test1 is Fully Qualified Name of Jenkins master and Chef master, then make following entries in file "/etc/hosts"::
        :bash:`root@soe-test1:~# cat /etc/hosts`

        :bash:`127.0.0.1       localhost`

        :bash:`9.3.126.17     soe-test1.aus.stglabs.ibm.com   soe-test1`

    f. Now reboot the system.

3. SSH configuration::
    Copy ssh keys from autoport sandbox to root and jenkins accounts, on Jenkins master. Perform following steps to copy::
        :bash:`cp ./autoport/data/security/jenkins  root@<jenkins-master>:.ssh/`

        :bash:`cp ./autoport/data/security/jenkins.pub  root@<jenkins-master>:.ssh/`

        :bash:`cp ./autoport/data/security/jenkins  jenkins@<jenkins-master>:.ssh/`

        :bash:`cp ./autoport/data/security/jenkins.pub  jenkins@<jenkins-master>:.ssh/`

    In future, we will want to dynamically add build slaves from the autoport driver.

    .. note:: Ensure that appropriate permissions are set on .ssh folder. If appropriate permissions are not applied, they can be using below commands::
      :bash:`su jenkins`

      :bash:`sudo chown -R jenkins:jenkins ~/.ssh`

      :bash:`sudo chmod 700 ~/.ssh`

      :bash:`sudo chmod 600 ~/.ssh/*`

      :bash:`sudo restorecon -R -v ~/.ssh`

Jenkins server can be accessed at `Jenkins <http://new_server_hostname:8080/>`_


Jenkins first time site configuration:
======================================

1. Click on Manage Jenkins -> Configure System. And set number of executors to 8.

2. Click on Manage Jenkins -> Manage Plugins. Update the installed plugins, and click restart jenkins button.

3.After restart, install following plugins(Look on the available tab. If you don't see it, there is a search option for plugins)::
    - Artifact Deployer Plugin
    - Copy Artifact Plugin
    - Compress build log Plugin
    - Conditional-buildstep Plugin
    - description setter plugin
    - Git Client Plugin
    - Git Plugin
    - GitHub Plugin
    - Github API Plugin
    - Hudson Post build task
    - Multijob plugin
    - Node and Label parameter Plugin
    - Parameterized Trigger Plugin
    - Plot plugin
    - Publish over SSH
    - Rebuilder
    - Run conditional Plugin
    - SSH Agent Plugin
    - Show Build Parameters Plugin
    - Workflow: Step API
    - Slave Setup Plugin
    - Docker plugin
    - Libvirt Slaves Plugin
    - Environment Injector Plugin
    - Build-timeout Plugin
    - Pre-scm-buildstep Plugin


Chef Installation and Setup:
============================

1. Get chef-server-core package and install per instructions from this `website <https://packagecloud.io/chef/stable/packages/ubuntu/lucid/chef-server-core_12.1.0-1_amd64.deb>`_.  (or) alternatively, download from https://downloads.chef.io/chef-server/ubuntu/ , make sure to select the appropriate OS version and architecture.
2. Once the download is complete, run below command to install chef-server::
    :bash:`sudo dpkg -i chef-server-core_*.deb`
3. Re-configure chef-server via below command::
    :bash:`sudo chef-server-ctl reconfigure`
4. In order to make all communication between chef-server and target nodes via IPs , and not through fqdn. Follow the below steps::
    - Create a file /etc/opscode/chef-server.rb with following content::
        :bash:`lb['api_fqdn'] = node['ipaddress']`

        :bash:`lb['web_ui_fqdn'] = node['ipaddress']`

        :bash:`nginx['server_name'] = node['ipaddress']`

        :bash:`nginx['url'] = "https://#{node['ipaddress']}"`

        :bash:`bookshelf['vip'] = node['ipaddress']`

5. Edit the below files(temporary tweak)::
    a. /opt/opscode/embedded/cookbooks/private-chef/templates/default/nginx/nginx.conf.erb
       Change  all occurrence of  "server_name <%= node['fqdn'] %>;" to "server_name <%= node['ipaddress'] %>;"

    b. /opt/opscode/embedded/cookbooks/private-chef/recipes/show_config.rb
        Change "config = PrivateChef.generate_config(node['fqdn'])"  to "config = PrivateChef.generate_config(node['ipaddress'])"

    c. Again run reconfigure::
        :bash:`sudo chef-server-ctl reconfigure`

6. Create an administrative user::
    :bash:`sudo  chef-server-ctl user-create user_name first_name last_name email password --filename FILE_NAME`

    **Note**::
        a) Make sure that user_name is set to "autoport-chef" and FILE_NAME is set with the value "autoport-chef.pem" as shown in the example.This would eliminate the need to create knife.rb per installation and allow use of a common knife.rb present in autoport codebase.
        b) first_name,last_name,email,password,: These values can be set appropriately. These values are only used while using chef-webui. (e.g. http://soe-test1.aus.stglabs.ibm.com/)  and would not be utilized by the autoport application. However, we suggest to use values as per example shown , to maintain consistency.

7. Create Organization::
    :bash:`chef-server-ctl org-create short_name long_name --association_user user_name --filename  ORG_FILE_NAME`

    :bash:`short_name: value should be a basic identifier for your organization.  Make sure we set the value as autoport-ibm.`

    :bash:`long_name:  proper name of the organization. Make sure we set the value as autoport-ibm.`

    :bash:`user_name:  User to be added to the Organization. This value is the once created in #4 above i.e  autoport-chef`

Process to be followed to do a re-registration of existing nodes to chef-server:
================================================================================

a. :bash:`knife node delete <node-name>`

   .. note:: Node name can be found using knife node list, in case of autoport node-name = hostname of  node

b. :bash:`knife client delete <client-name>`

    .. note:: client-name can be found using client list, in case of autoport client-name = hostname of  node

c. Login to the target node and remove "/etc/chef" folder
    :bash:`rm -rf /etc/chef`

d. During next knife bootstrap or "sync" operation via autoport , nodes would get re-registered.

Chef Workstation Installation:
==============================
- Download `chef-client <https://downloads.chef.io/chef-client/ubuntu/>`_ package. 
- Make sure to select the appropriate OS version and architecture.
- Install chef-client::
    :bash:`sudo dpkg -i chef_*_amd64.deb`


Configuring Workstation:
========================

- Create a directory named ".chef" and add certificate files in it, as below:
    :bash:`mkdir -p /var/opt/autoport/chef-repo/.chef`

    :bash:`cp autoport-ibm-validator.pem /var/opt/autoport/chef-repo/.chef/`

    :bash:`cp autoport-chef.pem /var/opt/autoport/chef-repo/.chef/`


Configuring Custom Managed Repositories:
========================================

Some additional packages are required to be pre-installed on a slave node, as many other packages need those packages to be available for proper execution. Such packages will be part of Managed repositories.

In order to setup such repositories perform following steps::
    1. Install,configure and run apache2 server:
            :bash:`sudo apt-get install apache2`

        Change default listening port if required, by updating file "/etc/apache2/ports.conf" and replacing "Listen  <new_port>" instead of "Listen  80"

        Change hostname if required using below command::
            :bash:`hostname -v <fully qualified domain name>`
            :bash:`# e.g. soe07x-vm2.aus.stglabs.ibm.com`

        Restart Apache server::
            :bash:`sudo service apache2 restart`

    2. Install utilities "createrepo"(for creating redhat based repositories) and "reprepro"(for creating debian based repositories)::
        :bash:`sudo apt-get install createrepo`

        :bash:`sudo apt-get install reprepro`

    3. Create following folder structures to setup repository based on OS distros:
        - /var/www/autoport_repo
        - /var/www/autoport_repo/rpms/
        - /var/www/autoport_repo/debs/
        - /var/www/autoport_repo/archives/
        - /var/www/autoport_repo/debs/ubuntu
        - /var/www/autoport_repo/debs/ubuntu/conf
        - /var/www/autoport_repo/debs/ubuntu/trusty
        - /var/www/autoport_repo/rpms/rhel
        - /var/www/autoport_repo/debs/rhel/7

        **Note**::
            With every new supported OS release, directory structure should be maintained in below format::
                *Debian based*::
                    - /var/www/autoport_repo/debs/<os>
                    - /var/www/autoport_repo/debs/<os>/conf
                    - /var/www/autoport_repo/debs/<os>/<os-release-2>
                    - /var/www/autoport_repo/debs/<os>/<os-release-1>
                    - /var/www/autoport_repo/debs/<os>/<os-release-N>

                Here, OS-release maps to codebase-name e.g for ubuntu OS-releases could be trusty, utopic

                *Redhat based*::
                    - /var/www/autoport_repo/rpms/<os>
                    - /var/www/autoport_repo/rpms/<os>/<release-number>

                Here, <release-number> maps to e.g  for rhel, release-number could be 7 (major-version i.e 7 not 7.x).
    4. Create distribution file at /var/www/autoport_repo/debs/ubuntu/conf/ using below command:
        :bash:`sudo touch distributions`

       With below contents::

                *Origin: autoport_repo*
                *Label: autoport_repo*
                *Codename: trusty*
                *Components: main*
                *Architectures: i386 amd64 ppc64le ppc64el source*
                *Description: autoport_repo*

                *Origin: autoport_repo*
                *Label: autoport_repo*
                *Codename: jessie*
                *Components: main*
                *Architectures: i386 amd64 ppc64le ppc64el source*
                *Description: autoport_repo*

                *Origin: autoport_repo*
                *Label: autoport_repo*
                *Codename: utopic*
                *Components: main*
                *Architectures: i386 amd64 ppc64le ppc64el source*
                *Description: autoport_repo*

       **NOTE**::
            With every new OS-release append the above block to the same file with updated Codename field::

               *Origin: autoport_repo*
               *Label: autoport_repo*
               *Codename:  <OS-release>*
               *Components: main*
               *Architectures: i386 amd64 ppc64le ppc64el source*
               *Description: autoport_repo*

    5. Upload required Managed packages that needs to be build from source, in folder "/var/www/autoport_repo/archives/". Below is the list of packages::
        -  apache-ant-1.9.3-bin.tar.bz2
        -  apache-ant-1.9.6-bin.tar.bz2
        -  apache-maven-3.0.5-bin.tar.gz
        -  apache-maven-3.3.3-bin.zip
        -  archive.log
        -  File-Remove-1.52.tar.gz
        -  gradle-1.12-bin.zip
        -  gradle-1.4-bin.zip
        -  ibm-1.2.0.5-node-v0.12.7-linux-ppcle64.bin
        -  ibm-java-sdk-7.1-3.10-ppc64le-archive.bin
        -  ibm-java-sdk-7.1-3.10-x86_64-archive.bin
        -  ibm-java-sdk-8.0-1.1-ppc64le-archive.bin
        -  ibm-java-sdk-8.0-1.1-x86_64-archive.bin
        -  Module-Install-1.14.tar.gz
        -  perl-5.20.2.tar.gz
        -  perl-5.22.0.tar.gz
        -  protobuf-2.6.1.tar.gz
        -  py-1.4.26.tar.gz
        -  pytest-2.6.4.tar.gz
        -  pytest-2.7.2.tar.gz
        -  scala-2.9.2.tgz
        -  Strict-Perl-2014.10.tar.gz
        -  Strict-Perl-2015.08.tar.gz
        -  Test-Strict-0.26.tar.gz
        -  YAML-Tiny-1.64.tar.gz

        **NOTE**:: Above package can be located at http://soe-test1.aus.stglabs.ibm.com:90/autoport_repo/
            Refer http://soe-test1.aus.stglabs.ibm.com:90/autoport_repo/debs/ for deb packages
            Refer http://soe-test1.aus.stglabs.ibm.com:90/autoport_repo/rpms/ for rpm packages

    6. Once all the packages are placed in appropriate directory run below commands::
       :bash:`createrepo /var/www/autoport_repo/rpms/<os>/<release-number>`

        :bash:`cd /var/www/autoport_repo/debs/<os>; reprepro -b /var/www/autoport_repo/debs/<os> inludedeb <OS-release> /var/www/autoport_repo/debs/<os>/<os-release>`

        :bash:`service apache2 restart`
