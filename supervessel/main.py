import random, string
import time
from flask import Flask, render_template, json
from heatclient.client import Client as heatClient
from keystoneclient.v2_0 import client as keyStoneClient
from heatclient.common import template_utils

app = Flask(__name__)

@app.route("/autoport/")
def main():
    return render_template("main.html")

@app.route("/autoport/createAutoportStack")
def createAutoportStack():
    global heat
    global stack_id

    # To be changed: user input arguments reading from browser?
    username = 'sunkewei@cn.ibm.com'
    password = 'passw0rd'
    tenant_name = 'sunkewei@cn.ibm.com'
    auth_url = 'http://192.168.11.51:5000/v2.0'

    try:
        # Get token from keystone
        keystone = keyStoneClient.Client(username=username, password=password,tenant_name=tenant_name, auth_url=auth_url, endpoint_type='adminURL')

        auth_token = keystone.auth_ref['token']['id']

        heat_url = ''
        services = keystone.auth_ref['serviceCatalog']
        for service in services:
            if service['name'] == 'heat':
                heat_url = service['endpoints'][0]['publicURL']

        api_version = "1"
        heat = heatClient(api_version, endpoint=heat_url, token=auth_token)

        path = "autoport.yaml"
        # from yaml to json
        tpl_files, template = template_utils.get_template_contents(path)

        #generate stack name randomly
        stack_name = 'autoport-' + randomword(10)
        create_fields = {
            'stack_name': stack_name,
            'timeout_mins': 60,
            'disable_rollback': True,
            'template': template,
            'files': {},
            'environment': {}
        }

        stack_id = heat.stacks.create(**create_fields)['stack']['id']

        # wait for stack creation's completion
        spent_time = 0
        while spent_time < 60:
            stack = heat.stacks.get(stack_id)
            if stack.status == 'COMPLETE':
                break
            elif stack.status != 'IN_PROGRESS':
                delete_fields = { 'stack_id': stack_id }
                heat.stacks.delete(**delete_fields)
                return json.jsonify(status = "failure", error="Stack creation fails. Please try later.")
            time.sleep(1)
            spent_time += 1

        # get heat template outputs information
        # Todo:
        # (1) ssh autoport driver node and run autoport with -p -u ?
        # (2) open autoport homepage automatically?
        if stack.status == 'COMPLETE':
            outputs_list = heat.stacks.get(stack_id).to_dict()['outputs']
            msg = 'Stack Name is ' + stack_name + '\n'
            for item in outputs_list:
                if item['output_key'] == 'driver_server_floating_ip':
                    msg = msg + 'The IP of Autoport driver is ' + item['output_value'] + '\n'
                    msg = msg + 'You may use your browser now - http://%s:5000/autoport/' % (item['output_value']) + '\n'
                elif item['output_key'] == 'master_server_floating_ip':
                    msg = msg + 'The IP of Jenkins master is ' + item['output_value'] + '\n'
            return json.jsonify(status = "ok", message=msg)
        else:
            return json.jsonify(status = "failure", error="Stack creation timeout. Please try later.")

    except Exception as exc:
        return json.jsonify(status = "failure", error=exc.message)

@app.route("/autoport/deleteAutoportStack")
def deleteStack():
    delete_fields = {
        'stack_id': stack_id
    }
    heat.stacks.delete(**delete_fields)

def randomword(length):
   return ''.join(random.choice(string.lowercase) for i in range(length))

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int("5000")
    )