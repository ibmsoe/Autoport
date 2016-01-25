import os
import time
import random, string
import globals
from novaclient import client as nvclient
#from log import logger
import json
from urlparse import urlparse

nodes_info_file = './data/config/nodes_info.json'

def rebuildServer(ip):
    with open(nodes_info_file,'r') as f:
        obj = json.load(f)
        f.close()
    instance_name = obj[ip]['name']

    with nvclient.Client(2, globals.os_username, globals.os_password, globals.os_tenant_name, globals.os_auth_url) as nova:
        instance = nova.servers.find(name=instance_name)
        # instance.rebuild( obj[ip]['image_id'])
        instance.rebuild( obj[ip]['original_image_id'])
        status = "REBUILD"
        while status == 'REBUILD':
            time.sleep(5)
            # Retrieve the instance again so the status field updates
            status = instance.status

def randomword(length):
   return ''.join(random.choice(string.lowercase) for i in range(length))

def getstackIdbyIp(nova,ip):
    instances = nova.servers.list()
    for instance in instances:
        if ip in instance.networks.get("autoport_network",""):
            return instance.metadata.get("stack_id","")
    return ""

def getfloatingIp():
    ip = urlparse(globals.jenkinsUrl).hostname
    return ip

def getinstancesbyStackId(nova,stack_id):
    instances_ret=[]
    instances = nova.servers.list()
    for instance in instances:
        if stack_id == instance.metadata.get("stack_id",""):
            instances_ret.append(instance)
    return instances_ret

def initial():
    floating_ip = getfloatingIp()
    instances = []
    with nvclient.Client(2, globals.os_username, globals.os_password, globals.os_tenant_name, globals.os_auth_url) as nova:
        stack_id = getstackIdbyIp(nova,floating_ip)
        instances = getinstancesbyStackId(nova,stack_id)

    nodes_info={}
    for instance in instances:
        instance_info={}
        for ip in globals.nodeIPs:
            if ip in instance.networks.get("autoport_network",""):
                instance_info['instance_id'] = instance.id
                instance_info['name'] = instance.name
                instance_info['image_id']    = instance.image['id']
                instance_info['original_image_id'] = instance.image['id']
                nodes_info[ip]=instance_info
                break
    with open(nodes_info_file,mode='w') as f:
        json.dump(nodes_info,f)
        f.close()
    return nodes_info

if __name__ == "__main__":
    globals.init()
    nodes_info = initial()
#    createSnapshot('192.168.1.213')
#    rebuildServer('192.168.1.110')
