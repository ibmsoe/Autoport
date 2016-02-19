import os
import time
import random, string
import globals
from novaclient import client as nvclient
import json
from urlparse import urlparse


nodes_info_file = './data/config/cloudNodeInfo.json'

cmdInvocation = False

def rebuildServer(ip, rebuildFlag = True):

    if not cmdInvocation:
        from log import logger
        logger.debug("rebuildServer: ip=%s" % ip)

    with open(nodes_info_file,'r') as f:
        obj = json.load(f)
        f.close()
    instance_name = obj[ip]['name']

    if not cmdInvocation:
        logger.debug("rebuildServer: instance_name=%s" % instance_name)

    with nvclient.Client(2, globals.os_username, globals.os_password, globals.os_tenant_name, globals.os_auth_url) as nova:
        instance = nova.servers.find(name=instance_name)
        if not cmdInvocation:
            logger.debug("rebuildServer: instance.status=%s" % instance.status)

        # instance.rebuild( obj[ip]['image_id'])
        if rebuildFlag == True:
            instance.rebuild( obj[ip]['original_image_id'])

        cnt = 0
        status = "REBUILD"
        while status == 'REBUILD' and cnt < 20:

            time.sleep(5)

            # Retrieve the instance again so the status field updates
            status = instance.status
            if not cmdInvocation:
                logger.debug("rebuildServer: instance.status=%s" % status)

            cnt += 1
    return status

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

def cloudInit():
    nodes_info={}

    if not cmdInvocation:
        from log import logger
        logger.debug("In cloudInit")
    if os.path.exists(nodes_info_file):
        logger.debug("cloudInit: nodeInfoFile Exists.")
        with open(nodes_info_file,mode='r') as f:
            nodes_info=json.load(f)
        f.close()
        if not cmdInvocation:
            logger.debug("cloudInit: nodes_info=%s" % str(nodes_info))
        if  len(nodes_info.keys()) > 0:
            return nodes_info

    floating_ip = getfloatingIp()
    instances = []

    if not cmdInvocation:
        logger.debug("In cloudInit, floating_ip=%s" % floating_ip)

    with nvclient.Client(2, globals.os_username, globals.os_password, globals.os_tenant_name, globals.os_auth_url) as nova:
        stack_id = getstackIdbyIp(nova,floating_ip)
        instances = getinstancesbyStackId(nova,stack_id)

    if not cmdInvocation:
        logger.debug("cloudInit: instances=%s" % str(instances))

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

    if not cmdInvocation:
        logger.debug("cloudInit: nodes_info=%s" % str(nodes_info))

    with open(nodes_info_file,mode='w') as f:
        json.dump(nodes_info,f)
        f.close()

    return nodes_info

if __name__ == "__main__":
    cmdInvocation = True
    globals.init()
    logger = log.init()
    nodes_info = cloudInit()
#    createSnapshot('192.168.1.213')
#    rebuildServer('192.168.1.110')
