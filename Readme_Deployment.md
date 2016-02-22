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
