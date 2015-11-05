# chef_server is set to ipaddress of the current node , considering that workstation and chef-server are on the same node
# As per design , in autoport both chef-server and chef-workstation would be configured on the same node.

current_dir = File.dirname(__FILE__)
chef_server = Socket.ip_address_list[1].ip_address

log_level                :info
log_location             STDOUT
node_name                "autoport-chef"
client_key               "#{current_dir}/autoport-chef.pem"
validation_client_name   "autoport-ibm-validator"
validation_key           "#{current_dir}/autoport-ibm-validator.pem"
chef_server_url          "https://#{chef_server}/organizations/autoport-ibm"
cookbook_path            ["#{current_dir}/../cookbooks"]

# Specifying path for template file to be used by default, so that it need
# not be specified explicitly on commandline during execution of knife bootstrap.

knife[:template_file]="#{current_dir}/bootstrap/autoport_template.erb"
