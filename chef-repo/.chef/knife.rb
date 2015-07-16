# chef_server is set to hostname of the current node , considering that workstation and chef-server are on the same node
# As per design , in autoport both chef-server and chef-workstation would be configured on the same node.

current_dir = File.dirname(__FILE__)
chef_server = Socket.gethostbyname(Socket.gethostname).first

log_level                :info
log_location             STDOUT
node_name                "autoport-chef"
client_key               "#{current_dir}/autoport-chef.pem"
validation_client_name   "autoport-ibm-validator"
validation_key           "#{current_dir}/autoport-ibm-validator.pem"
chef_server_url          "https://#{chef_server}/organizations/autoport-ibm"
cookbook_path            ["#{current_dir}/../cookbooks"]
