     NOTE: These steps are to be carried out on autoport driver.

Dependencies For Deploying Autoport On Apache Server:
=====================================================
In order to deploy Autoport onto Apache server following dependencies
need to be pre-installed :
1. Install **pip**, so that required python libraries can be installed with all
required dependencies,**pip** can be installed as :
    * **On RHEL/Centos :**
        * `$ sudo yum install python-pip`
    *  **On Ubuntu/Debian :**
        * `$ sudo apt-get install python-pip`

2. If packages *python-devel* and *libevent-devel* are not already installed,
install them as :
    * **On RHEL/Centos :**
         * `$ sudo yum install libevent-devel python-devel`
    *  **On Ubuntu/Debian:**
         * `$ sudo apt-get install libevent-devel python-devel`

3. Install python libraries using **pip** :
    * `$ sudo pip install Flask`
    * `$ sudo pip install PyGithub`
    * `$ sudo pip install requests`
    * `$ sudo pip install paramiko`
    * `$ sudo pip install threadpool`
    * `$ sudo pip install diff-match-patch`
    * `$ sudo pip install PyYaml`
    * `$ sudo pip install flask-compress`
    * `$ sudo pip install pytz`
    * `$ sudo pip install python-novaclient`

4. Install **apache server**, refer following links for installation :
    * [Installing Apache on RHEL6](https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/6/html/Managing_Confined_Services/chap-Managing_Confined_Services-The_Apache_HTTP_Server.html#sect-Managing_Confined_Services-The_Apache_HTTP_Server-The_Apache_HTTP_Server_and_SELinux)

    * [Installing Apache on RHEL7/CentOS](https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/7/html/System_Administrators_Guide/ch-Web_Servers.html)

    * [Installing Apache on Ubuntu/Debian](https://help.ubuntu.com/lts/serverguide/httpd.html)

5. Install **mod_wsgi** if not already installed as below :
    *  **On Ubuntu/Debian :**
        * `$ sudo apt-get install libapache2-mod-wsgi`
        * `$ sudo a2enmod mod-wsgi`

    *  **On RHEL/Centos :**
        * `$ sudo yum install mod_wsgi`

Deploying Autoport on Apache Server:
====================================
1. Checkout Autoport codebase from gerrit on your local machine.
2. Go to folder **configs**
    * `$ cd configs`
3. Make sure script **deploy_autoport.sh** has executable permissions :
    * `$ chmod 755 deploy_autoport.sh`
4. Now execute the deployment script as a sudo user,
   with OS flavor(centos/ubuntu/rhel) as argument :
    * `$ sudo ./deploy_autoport.sh <os_flavor>`
5. On completion of the script Autoport application will be deployed and
   ready to served by Apache on port 80.
6. Site can be accessed using link :
    * *`http://<server_hostname>/autoport`*

Log Locations:
===============
1. Autoport logs can be found at location:
    *  *`/var/www/html/autoport/data/autoport.log`*
2. Server logs can be found at:
   * **For RHEL/CentOS :**
     * `/var/log/httpd/error_log`
    * **For Ubuntu :**
      * `/var/log/apache2/error.log`


    NOTE: Below steps to be carried out on Jenkins Master

Jenkins Master Installation:
============================

1. Install Jenkins master as per link :
   [Installing Jenkins](http://pkg.jenkins-ci.org/debian/)

2. After installation of Jenkins Master, perform following steps :
    * a) Create a user **jenkins**
       * `$ useradd -p $(openssl passwd -1 <password>) jenkins
          -s /bin/bash -m -d /home/jenkins`
    * b) Create a folder 'jenkins_home' under specified path as shown below
       * `$ mkdir /home/jenkins/jenkins_home`
    * c) Edit **'/etc/default/jenkins'**
      * Add following line
      `JENKINS_HOME=/home/jenkins/jenkins_home`
       after the line
      `# jenkins home location`
    * d) Install Open-jdk-7:
        * **Ubuntu :**
            * `$ sudo apt-get install openjdk-7-jdk`
        * **RHEL/CentOS :**
            * `$ sudo yum install java-1.7.0-openjdk-devel`
    * e) Install git:
        * **Ubuntu :**
            * `$ sudo apt-get install git-all`
        * **RHEL/CentOS :**
            * `$ sudo yum install git-all`
    * e) Add **jenkins** user to sudoers list with no password
        * Add following line in file **"/etc/sudoers"**:
        `jenkins ALL=(ALL:ALL) NOPASSWD: ALL`
         after line:
        `%sudo    ALL=(ALL:ALL) ALL`

3. SSH configuration :
    * Copy ssh keys from autoport sandbox to root and jenkins accounts,
      on Jenkins master. Perform following steps to copy:
       * `$ cp ./autoport/data/security/jenkins  root@<jenkins-master>:.ssh/`
       * `$ cp ./autoport/data/security/jenkins.pub  root@<jenkins-master>:.ssh/`
       * `$ cp ./autoport/data/security/jenkins  jenkins@<jenkins-master>:.ssh/`
       * `$ cp ./autoport/data/security/jenkins.pub jenkins@<jenkins-master>:.ssh/`

   * Ensure that appropriate permissions are set on .ssh folder.
      * `$ su jenkins`
      * `$ sudo chown -R jenkins:jenkins ~/.ssh`
      * `$ sudo chmod 700 ~/.ssh`
      * `$ sudo chmod 600 ~/.ssh/*`
      * `$ sudo restorecon -R -v ~/.ssh`

4. Jenkins server can be accessed at:
`http://new_server_hostname:8080/`

Jenkins First Time Site Configurations:
======================================

1. Click on `Manage Jenkins -> Configure System`. Set number of executors to 8.
2. Click on `Manage Jenkins -> Manage Plugins`.
Update the installed plugins,and click restart jenkins button.
3. After restart, install following plugins(Look on the available tab.
If you do not see it, there is a search option for plugins):
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


Chef Installation And Setup:
============================

1. Get chef-server-core package and install as
per instructions from this [website](https://packagecloud.io/chef/stable/packages/ubuntu/lucid/chef-server-core_12.1.0-1_amd64.deb).
(or) alternatively, download it from [opscode](https://downloads.chef.io/chef-server/ubuntu/) ,
make sure to select the appropriate OS version and architecture.

2. Once the download is complete, run below command to install chef-server:
    * `$ sudo dpkg -i chef-server-core_*.deb`

3. Re-configure chef-server via below command:
    * `$ sudo chef-server-ctl reconfigure`

4. In order to make all communication between chef-server and target nodes via IPs ,
and not through fqdn. Create a file /etc/opscode/chef-server.rb with following content:

        lb['api_fqdn'] = node['ipaddress']
        lb['web_ui_fqdn'] = node['ipaddress']
        nginx['server_name'] = node['ipaddress']
        nginx['url'] = "https://#{node['ipaddress']}"
        bookshelf['vip'] = node['ipaddress']`

5. Edit the below files(temporary tweak):
    * Edit `/opt/opscode/embedded/cookbooks/private-chef/templates/default/nginx/nginx.conf.erb`.
          * Change  all occurrence of  `server_name <%= node['fqdn'] %>;`
       to `server_name <%= node['ipaddress'] %>;`
    * Edit `/opt/opscode/embedded/cookbooks/private-chef/recipes/show_config.rb`.
          * Change `config = PrivateChef.generate_config(node['fqdn'])`
       to `config = PrivateChef.generate_config(node['ipaddress'])`
    *  Again run reconfigure:
       * `$ sudo chef-server-ctl reconfigure`

6. Create an administrative user:
    * `$ sudo  chef-server-ctl user-create <user_name> <first_name>
       <last_name> <email> <password> --filename FILE_NAME`:

          NOTE: Make sure that user_name is set to "autoport-chef"
                and FILE_NAME is set to "autoport-chef.pem".This would eliminate
                the need to create knife.rb per installation and allow
                use of a common knife.rb present in autoport codebase.

7. Create Organization:
   * `$ chef-server-ctl org-create short_name long_name
   --association_user user_name --filename  ORG_FILE_NAME`

         short_name: A basic identifier for your organization.
         Make sure we set the value as autoport-ibm.
         long_name:  proper name of the organization.
         Make sure we set the value as autoport-ibm.
         user_name:  User to be added to the Organization.
         This value is the one created in #6 above i.e  autoport-chef`

Chef Workstation Installation:
==============================
- Download [chef-client](https://downloads.chef.io/chef-client/ubuntu/) package.
- Make sure to select the appropriate OS version and architecture.
- Install chef-client:
   * `$ sudo dpkg -i chef_*_amd64.deb`

Configuring Workstation:
========================
- Create a directory named ".chef" and add certificate files :
    * `$ mkdir -p /var/opt/autoport/chef-repo/.chef`
    * `$ cp autoport-ibm-validator.pem /var/opt/autoport/chef-repo/.chef/`
    * `$ cp autoport-chef.pem /var/opt/autoport/chef-repo/.chef/`


Configuring Custom Managed Repositories:
========================================
RPMS, DEBS which are not directly available via yum/apt package manager on
the slaves nodes, are maintained in the custom repository.
Along with RPMS and DEBS there are few binaries/tar/zip packages also maintained.
These packages are part of Managed Runtime.

In order to setup repositories perform following steps:
  1. Install,configure and run apache2 server:
      * `$ sudo apt-get install apache2`
      * Edit /etc/apache2/ports.conf  to change Listen parameter to 90
        replacine **Listen  <new_port>** instead of **Listen  80**
      * Restart Apache server::
         * `sudo service apache2 restart`

    2. Install utilities **"createrepo"** (for creating custom yum repository)
       and **reprepro** (for creating apt repository):
        * `$ sudo apt-get install createrepo`
        * `$ sudo apt-get install reprepro`

    3. Create following folder structures to setup repository:
        - /var/www/autoport_repo
        - /var/www/autoport_repo/rpms/
        - /var/www/autoport_repo/debs/
        - /var/www/autoport_repo/archives/

    4. Create sub-directories as per supported os and os-release.
        - /var/www/autoport_repo/debs/ubuntu
        - /var/www/autoport_repo/debs/ubuntu/conf
        - /var/www/autoport_repo/debs/ubuntu/trusty
        - /var/www/autoport_repo/rpms/rhel
        - /var/www/autoport_repo/debs/rhel/7
        - /var/www/autoport_repo/rpms/centos
        - /var/www/autoport_repo/debs/centos/7
    5.
           Note: With new supported OS-release, maintain the structure as:
           Debian based:
           - /var/www/autoport_repo/debs/<os>
           - /var/www/autoport_repo/debs/<os>/conf
           - /var/www/autoport_repo/debs/<os>/<os-release-2>
           - /var/www/autoport_repo/debs/<os>/<os-release-1>
           - /var/www/autoport_repo/debs/<os>/<os-release-N>
           Here, OS-release maps to codebase-name
           e.g for ubuntu OS-releases could be trusty, utopic
           Redhat based:
           - /var/www/autoport_repo/rpms/<os>
           - /var/www/autoport_repo/rpms/<os>/<release-number>
           Here, <release-number> maps to e.g  for rhel, release-number
           could be 7 (major-version i.e 7 not 7.x).

4.  Create distribution file at /var/www/autoport_repo/debs/ubuntu/conf/
    using below command:
      * `$ sudo touch distributions`
      * Add below content to the file:

                Origin: autoport_repo
                Label: autoport_repo
                Codename: trusty
                Components: main
                Architectures: i386 amd64 ppc64le ppc64el source
                Description: autoport_repo

            NOTE*:With new OS-release append the below block with new values.
               Origin: autoport_repo
               Label: autoport_repo
               Codename:  <OS-release>
               Components: main
               Architectures: i386 amd64 ppc64le ppc64el source
               Description: autoport_repo

    5. Upload required Managed packages in the specified path below

              |-- archives
              |   |-- File-Remove-1.52.tar.gz
              |   |-- Module-Install-1.14.tar.gz
              |   |-- Strict-Perl-2014.10.tar.gz
              |   |-- Strict-Perl-2015.08.tar.gz
              |   |-- Test-Strict-0.26.tar.gz
              |   |-- YAML-Tiny-1.64.tar.gz
              |   |-- apache-ant-1.9.3-bin.tar.bz2
              |   |-- apache-ant-1.9.6-bin.zip
              |   |-- apache-maven-3.0.5-bin.tar.gz
              |   |-- apache-maven-3.3.3-bin.zip
              |   |-- archive.log
              |   |-- gradle-1.12-bin.zip
              |   |-- gradle-1.4-bin.zip
              |   |-- gradle-2.9-bin.zip
              |   |-- ibm-4.2.2.0-node-v4.2.2-linux-ppcle64.bin
              |   |-- ibm-4.2.2.0-node-v4.2.2-linux-x64.bin
              |   |-- ibm-java-sdk-7.1-3.20-ppc64le-archive.bin
              |   |-- ibm-java-sdk-7.1-3.20-x86_64-archive.bin
              |   |-- ibm-java-sdk-8.0-2.0-ppc64le-archive.bin
              |   |-- ibm-java-sdk-8.0-2.0-x86_64-archive.bin
              |   |-- perl-5.20.2.tar.gz
              |   |-- perl-5.22.0.tar.gz
              |   |-- protobuf-2.5.0.tar.gz
              |   |-- protobuf-2.6.1.tar.gz
              |   |-- py-1.4.26.tar.gz
              |   |-- pytest-2.6.4.tar.gz
              |   |-- pytest-2.7.2.tar.gz
              |   `-- scala-2.9.2.tgz
              |-- debs
              |   `-- ubuntu
              |       |-- trusty
              |       |   |-- chef_12.3.0-1_amd64.deb
              |       |   |-- chef_12.4.0~dev.0+20150519080415.git.237.2882f53-1_ppc64el.deb
              |       |   |-- openjdk-8-jdk_8u45-b14-1~14.04_amd64.deb
              |       |   |-- openjdk-8-jdk_8u45-b14-1~14.04_ppc64el.deb
              |       |   |-- openjdk-8-jre-headless_8u45-b14-1~14.04_amd64.deb
              |       |   |-- openjdk-8-jre-headless_8u45-b14-1~14.04_ppc64el.deb
              |       |   |-- openjdk-8-jre_8u45-b14-1~14.04_amd64.deb
              |       |   |-- openjdk-8-jre_8u45-b14-1~14.04_ppc64el.deb
              |       |   |-- sbt-0.13.9.deb
              |       |   `-- scala-2.9.2.deb
              `-- rpms
                  |-- centos
                  |   `-- 7
                  |       |-- chef-12.3.0-1.el6.x86_64.rpm
                  |       |-- chef-12.4.0~dev.0+20150519065500.git.237.2882f53-1.el7.ppc64le.rpm
                  |       |-- chef-12.4.0~dev.0+git.237.2882f53-1.el7.ppc64.rpm
                  |       |-- python-pip-7.1.0-3.fc24.noarch.rpm
                  |       |-- rpmrebuild-2.11-4.fc23.noarch.rpm
                  |       |-- sbt-0.13.5.rpm
                  |       |-- scala-2.10.2.rpm
                  |       `-- scons-2.3.0-1.noarch.rpm
                  `-- rhel
                      `-- 7
                          |-- chef-12.3.0-1.el6.x86_64.rpm
                          |-- chef-12.4.0~dev.0+20150519065500.git.237.2882f53-1.el7.ppc64le.rpm
                          |-- chef-12.4.0~dev.0+git.237.2882f53-1.el7.ppc64.rpm
                          |-- python-pip-7.1.0-3.fc24.noarch.rpm
                          |-- rpmrebuild-2.11-4.fc23.noarch.rpm
                          |-- sbt-0.13.5.rpm
                          |-- scala-2.10.2.rpm
                           `-- scons-2.3.0-1.noarch.rpm

6. Once all the packages are placed in appropriate directory run below commands:
   * `$ createrepo /var/www/autoport_repo/rpms/<os>/<release-number>`
   * `$ cd /var/www/autoport_repo/debs/<os>; reprepro -b
   /var/www/autoport_repo/debs/<os> inludedeb <OS-release>
   /var/www/autoport_repo/debs/<os>/<os-release>`
   * `$ service apache2 restart`


     NOTE: These steps are to be carried out on build slaves.

Configuring Jenkins Build Slaves:
=================================
1. Install Open-jdk-7. This is necessary to connect the build slave to Jenkins master:
   * **Ubuntu :**
        * `$ sudo apt-get install openjdk-7-jdk`
    * **RHEL/CentOS :**
        * `$ sudo yum install java-1.7.0-openjdk-devel`

2. SSH configurations:
    * Edit **/etc/ssh/sshd_config**.
       * Ensure you have added/edited the setting as:
          * `change PermitRootLogin yes`
       * For *Ubuntu/Debian* build slaves, add (or) edit to the following:
          * `UseDNS no`
    * Restart ssh service.
       * **Ubuntu :**
         * `$ sudo service ssh restart`
       * **RHEL/CentOS :**
         * `$ service sshd restart`

3. Create **jenkins** user account
      * `$ useradd -p $(openssl passwd -1 <password>) jenkins
          -s /bin/bash -m -d /home/jenkins`

4. Add jenkins to Sudoers list:

       %sudo   ALL=(ALL:ALL) ALL
       jenkins ALL=(ALL) NOPASSWD: ALL
       Change "Defaults requiretty" to "Defaults !requiretty" if present

5. Configure ssh keys:
   * Append the content of jenkins.pub present on Jenkins Master at /home/jenkins/.ssh/
     to  /home/jenkins/.ssh/authorized_keys of each the build slave.
   *  Make sure that permissions are correct for .ssh folder and its content:
      * `$ su jenkins`
      * `sudo chown -R jenkins:jenkins ~/.ssh`
      * `sudo chmod 700 ~/.ssh`
      * `sudo chmod 600 ~/.ssh/*`
      * `sudo restorecon -R -v ~/.ssh`

6. Add slave node to Jenkins Master.
   * Go to `Jenkins Dashboard -> Manage Jenkins -> Manage Nodes -> New Node`
   * Fill in the details after selecting **Dumb Slave** option:

          Name: <node-name>
          # of executors: 8
          Remote root directory: /home/jenkins
          Label: Ubuntu_14.04_x86-64
          Launch Method: Launch slave agents on Unix machines via SSH
          Host: <ip-address/fqdn of the slave node>
          Credentials:
              Select option SSH Username with private key
              Username: <jenkins>
              Private Key: </home/jenkins/.ssh/jenkins>

7. Ensure on all build slaves **UMASK** is set to **002**
