import logging

LOG = logging.getLogger(__name__)
BASE_TEMPLATE = {
    'heat_template_version': '2013-05-23',
    'description': 'Automatic generated template',
    'parameters': {},
    'resources': {},
    'outputs': {}
}

BASE_PARAMETERS_TEMPLATE = {
    'public_net_id': {
        'type': 'string',
    },
    'private_net_name': {
        'type': 'string',
    },
    'private_subnet_name': {
        'type': 'string',
    },
    'private_net_cidr': {
        'type': 'string',
    },
    'private_net_gateway': {
        'type': 'string',
    },
    'router_name': {
        'type': 'string',
    },
    'fixedip_master_node': {
        'type': 'string',
    },
    'image': {
        'type': 'string',
    },
    'flavor': {
        'type': 'string',
    },
    'mounts': {
        'type': 'number',
    },
    'mountpoint0': {
        'type': 'string',
    },
    'filesystem0': {
        'type': 'string',
    },
    'address0': {
        'type': 'string',
    },
    'cinder_uuid': {
        'type': 'string',
    },
    'privileged': {
        'type': 'string',
    },
    'size': {
        'type': 'number',
    },
    'metadata': {
        'type': 'json',
    },
}

BASE_RESOURCES_TEMPLATE = {
    'server_port_1': {
        'type': 'OS::Neutron::Port',
        'properties': {
            'network_id': {
                'get_resource': 'private_net'
            },
            'fixed_ips': [{'ip_address': {'get_param': 'fixedip_master_node'}}]
        }
    },
    'server_fip_1': {
        'type': 'OS::Neutron::FloatingIP',
        'properties': {
            'floating_network_id': {
                'get_param': 'public_net_id'
            },
            'port_id': {
                'get_resource': 'server_port_1'
            }
        }
    },
    'private_subnet': {
        'type': 'OS::Neutron::Subnet',
        'properties': {
            'name': {'get_param': 'private_subnet_name'},
            'network_id': {'get_resource': 'private_net'},
            'cidr': {'get_param': 'private_net_cidr'},
            'gateway_ip': {'get_param': 'private_net_gateway'}
        }
    },

    'router': {
        'type': 'OS::Neutron::Router',
        'properties': {
            'name': {'get_param': 'router_name'}
        }
    },

    'router_gateway': {
        'type': 'OS::Neutron::RouterGateway',
        'properties': {
            'router_id': {'get_resource': 'router'},
            'network_id': {'get_param': 'public_net_id'}
        }
    },

    'private_net': {
        'type': 'OS::Neutron::Net',
        'properties': {
            'name': {'get_param': 'private_net_name'}
        }
    },

    'router_interface': {
        'type': 'OS::Neutron::RouterInterface',
        'properties': {
            'router_id': {'get_resource': 'router'},
            'subnet_id': {'get_resource': 'private_subnet'}
        }
    }
}

BASE_SLAVE_PORT_TEMPLATE = {
    'type': 'OS::Neutron::Port',
    'properties': {
        'network_id': {'get_resource': 'private_net'}
    }
}

BASE_OUTPUTS_TEMPLATE = {
    'master_server_internal_ip': {
        'value': {
            'get_attr': ['sparkMaster', 'networks', {'get_attr': ['private_net', 'name']}, 0]
        }
    },
    'master_server_floating_ip': {
        'value': {
            'get_attr': ['server_fip_1', 'floating_ip_address']
        }
    }
}

BASE_NODE_TEMPLATE = {
    'type': 'OS::Nova::Server',
    'depends_on': 'private_subnet',
    'properties': {
        'flavor': {
            'get_param': 'flavor'
        },
        'image': {
            'get_param': 'image'
        },
        'metadata': {
            'get_param': 'metadata'
        },
        'user_data_format': 'RAW',
    }
}

BASE_USER_DATA_PARAMS = {
    '$master_host_ip': {'get_attr': ['server_port_1', 'fixed_ips', 0, 'ip_address']},
    '$mounts': {'get_param': 'mounts'},
    '$source0': 'cinder',
    '$uuid0': {'get_param': 'cinder_uuid'},
    '$mountpoint0': {'get_param': 'mountpoint0'},
    '$filesystem0': {'get_param': 'filesystem0'},
    '$address0': {'get_param': 'address0'},
    '$privileged': {'get_param': 'privileged'}
}

MULTI_NODE_MASTER_SCRIPT_TEMPLATE = '''
                    #!/bin/bash
                    echo `hostname` >> /home/opuser/hostname
                    rm -rf /etc/hosts
                    file="/home/opuser/hosts"
                    while [ ! -e "$file" ]
                    do
                        sleep 1s
                    done
                    cp /home/opuser/hosts /etc/hosts
                    rm /home/opuser/hosts
                    # {"storage_start" : 1, "mounts": $mounts, "mountpoint0": "$mountpoint0", "privileged": "$privileged", "uuid0": "$uuid0", "source0": "$source0", "filesystem0" : "$filesystem0", "address0" : "$address0", "storage_stop" : 1}
                '''

MULTI_NODE_SLAVE_SCRIPT_TEMPLATE = """
                    #!/bin/bash
                    echo `hostname` >> /home/opuser/hostname
                    rm -rf /etc/hosts
                    file="/home/opuser/hosts"
                    while [ ! -e "$file" ]
                    do
                        sleep 1s
                    done
                    cp /home/opuser/hosts /etc/hosts
                    rm /home/opuser/hosts
                """

SLAVE_HN = 'hn_{slave_name}=`sudo -u opuser ssh -o StrictHostKeyChecking=no ${slave_name}_host_ip hostname`'
IP_SETTING = 'ip_{node}=$slave{node}_host_ip'
ECHO_IP = 'echo "$ip_{node} $hn{slave_name}" >> /etc/hosts'
SCP_CMD = 'sudo -u opuser scp -o StrictHostKeyChecking=no /etc/hosts $slave{node}_host_ip:/home/opuser/hosts'
SSH_CMD = 'sudo -u opuser ssh -t -o StrictHostKeyChecking=no $slave{node}_host_ip "sed -i s/__MASTER__/$hn_master/ /opt/hadoop-2.2.0/etc/hadoop/core-site.xml; sed -i s/__MASTERIP__/$ip_m/ /opt/spark-1.0.2-bin-hadoop2/conf/spark-env.sh;  /opt/hadoop-2.2.0/sbin/hadoop-daemon.sh start datanode;  /opt/spark-1.0.2-bin-hadoop2/sbin/start-slave.sh {node} spark://$ip_m:7077"'

MULTI_NODE_END_SLAVE_SCRIPT_TEMPLATE = '''
            #!/bin/bash
            chmod +w /etc/hosts
            echo `hostname` >> /home/opuser/hostname
            hn=`hostname -s`
            hn_master=`sudo -u opuser ssh -o StrictHostKeyChecking=no $master_host_ip hostname`
            {slave_hn}
            ip_m=$master_host_ip
            {ip_setting}
            echo "$ip_m $hn_master" >> /etc/hosts
            {echo_ip}
            sudo -u opuser scp -o StrictHostKeyChecking=no /etc/hosts $master_host_ip:/home/opuser/hosts
            {scp_cmd}
            sudo -u opuser ssh -t -o StrictHostKeyChecking=no $master_host_ip "sed -i s/__MASTER__/$hn_master/ /opt/hadoop-2.2.0/etc/hadoop/core-site.xml;  sed -i s/__MASTERIP__/$ip_m/ /opt/spark-1.0.2-bin-hadoop2/conf/spark-env.sh; /opt/hadoop-2.2.0/bin/hdfs namenode -format;  /opt/hadoop-2.2.0/sbin/hadoop-daemon.sh start namenode;  /opt/spark-1.0.2-bin-hadoop2/sbin/start-master.sh"
            {ssh_cmd}
'''

SINGLE_NODE_MASTER_SCRIPT_TEMPLATE = '''
            #!/bin/bash
            chmod +w /etc/hosts
            echo `hostname` >> /home/opuser/hostname
            hn=`hostname -s`
            ip_m=$master_host_ip
            echo "$ip_m $hn" >> /etc/hosts
            sudo -u opuser ssh -t -o StrictHostKeyChecking=no $master_host_ip "sed -i s/__MASTER__/$hn/ /opt/hadoop-2.2.0/etc/hadoop/core-site.xml; sed -i s/__MASTERIP__/$ip_m/ /opt/spark-1.0.2-bin-hadoop2/conf/spark-env.sh; /opt/hadoop-2.2.0/bin/hdfs namenode -format;  /opt/hadoop-2.2.0/sbin/hadoop-daemon.sh start namenode;  /opt/spark-1.0.2-bin-hadoop2/sbin/start-master.sh; /opt/hadoop-2.2.0/sbin/hadoop-daemon.sh start datanode;  /opt/spark-1.0.2-bin-hadoop2/sbin/start-slave.sh 1 spark://$ip_m:7077"
            # {"storage_start" : 1, "mounts": $mounts, "mountpoint0": "$mountpoint0", "privileged": "$privileged", "uuid0": "$uuid0", "source0": "$source0", "filesystem0" : "$filesystem0", "address0" : "$address0", "storage_stop" : 1}
           '''

# class BaseTemplate(object):
#     def __init__(self):
#         pass
#
#     def set_property(self, key, value):
#         setattr(self, key, value)
#
#     def list_all_member(self):
#         for name, value in vars(self).items():
#             LOG.debug('%s=%s', name, value)
#
#     def get_property(self, key):
#         if hasattr(self, key):
#             return getattr(self, key)
#         return None
#
#     def update_property(self, key, value):
#         if hasattr(self, key):
#             val = getattr(self, key)
#             val.update(value)
#             setattr(self, key, val)
#
#     def generate_template_dict(self):
#         return dict((key, value) for key, value in self.__dict__.items())
#
#
# class TemplateResource(BaseTemplate):
#     def __init__(self):
#         for k, v in BASE_RESOURCE_TEMPLATE.items():
#             setattr(self, k, v)
#         super(TemplateResource, self).__init__()
#
#
# class TemplateResourceNode(BaseTemplate):
#     def __init__(self):
#         for k, v in BASE_NODE_TEMPLATE.items():
#             setattr(self, k, v)
#         super(TemplateResourceNode, self).__init__()
#
#
# class TemplateOutputs(BaseTemplate):
#     def __init__(self):
#         for k, v in BASE_OUTPUTS_TEMPLATE.items():
#             setattr(self, k, v)
#         super(TemplateOutputs, self).__init__()
#
#
# class TemplateParams(BaseTemplate):
#     def __init__(self):
#         for k, v in BASE_PARAMETERS_TEMPLATE.items():
#             setattr(self, k, v)
#         super(TemplateParams, self).__init__()
#
#
# class Template(BaseTemplate):
#     def __init__(self):
#         self.heat_template_version = '2013-05-23'
#         self.description = 'Automatic generated template'
#         super(Template, self).__init__()
