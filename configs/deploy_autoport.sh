os_flavour=$1
DEPLOY_PATH="/var/www/html/autoport"

if [ \( "$os_flavour" = "rhel" \) -o \( "$os_flavour" = "centos" \) ]; then
    CONFIG_PATH="/etc/httpd/conf.d/autoport.conf"
    CONFIG_FILE="autoport_rhel.conf"
elif [ "$os_flavour" = "ubuntu" ]; then
    CONFIG_PATH="/etc/apache2/sites-available/autoport.conf"
    CONFIG_FILE="autoport_ubuntu.conf"
else
    echo "Please choose one of the options from rhel/ubuntu/centos"
    exit 0
fi

# Clean if old codebase is found.
rm -rf $DEPLOY_PATH/

rm -f $CONFIG_PATH

# Now start copying fresh codebase

echo "Copying autoport to webroot"

mkdir -p $DEPLOY_PATH

cp -rf ../* $DEPLOY_PATH

echo "Completed copying autoport to webroot"

cp -f $CONFIG_FILE $CONFIG_PATH

cd $DEPLOY_PATH

find . -type f -exec chmod 0644 {} \;

find . -type d -exec chmod 0755 {} \;

if [ \( "$os_flavour" = "rhel" \) -o \( "$os_flavour" = "centos" \) ]; then
    # SELinux related settings
    chcon -t httpd_sys_content_t $DEPLOY_PATH -R
    chcon -t httpd_sys_rw_content_t $DEPLOY_PATH/data -R
    setsebool -P httpd_can_network_connect 1
    chown -R apache:apache $DEPLOY_PATH
    service httpd restart
elif [ "$os_flavour" = "ubuntu" ]; then
    chown -R www-data:www-data $DEPLOY_PATH
    a2ensite autoport
    service apache2 restart
fi