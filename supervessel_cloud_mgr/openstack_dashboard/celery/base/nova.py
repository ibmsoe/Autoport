import datetime
from django.conf import settings
from django.template import loader
import jsonpickle
from novaclient import client
from openstack_dashboard.celery.base import keystone
from openstack_dashboard.celery.base.glance import get_glance_client
from openstack_dashboard.celery.base.keystone import get_keystone_client
from openstack_dashboard.celery.task.user_operation import transaction_user_points, send_mail_task
from openstack_dashboard.models import PointRate, PointOperation, SnapshotHistory
from openstack_dashboard.utils import user_api
import logging

LOG = logging.getLogger(__name__)

AUTH_URL = getattr(settings, 'OPENSTACK_KEYSTONE_URL', '')
OPENSTACK_CONFIG_BACKEND = getattr(settings, 'OPENSTACK_CONFIG_BACKEND', {})
ENDPOINT_TYPE = 'adminURL'
USER = OPENSTACK_CONFIG_BACKEND.get('user', '')
PASS = OPENSTACK_CONFIG_BACKEND.get('password', '')
TENANT = OPENSTACK_CONFIG_BACKEND.get('tenant', '')


def get_nova_client(region_name="Beijing", auth_url=AUTH_URL):
    return client.Client(1.1, USER, PASS, TENANT, auth_url,
                         endpoint_type=ENDPOINT_TYPE,
                         service_type="compute",
                         region_name=region_name)


def handle_server(server, seq, region):
    auth_url = region[0]
    region_name = region[1]
    warning_email_template = 'warning_email.html'
    user = keystone.get_user(server.user_id, auth_url=auth_url)
    roles = keystone.get_role(server.user_id, server.tenant_id, auth_url=auth_url)
    for role in roles:
        if role.name == "admin":
            return True
    points = int(user_api.get_user_points(user.username))
    flavor_id = server.flavor.get('id', '')
    need_points = 0
    spn = server.metadata.get("SPN", "Cloud")
    account = server.metadata.get("ACCOUNT", user.username)
    try:
        point_rate = PointRate.objects.get(flavor_id=flavor_id, service_type=spn)
        need_points = point_rate.points
    except Exception as exc:
        pass

    # LOG.debug('HIGHTALL sequence %s region %s user %s points %s need_points %s instance id %s name %s',
    #           seq, region_name, user.username, points, need_points, server.id, server.name)

    if need_points < points:
        transaction_user_points(account, "supernova@admin.grp", need_points)
        point_operation = PointOperation()
        point_operation.user_id = server.user_id
        point_operation.user_name = user.username
        point_operation.transfer_user = account
        point_operation.transfer_points = need_points
        point_operation.remain_points = points - need_points
        point_operation.region = region_name
        point_operation.save()
        if points < (3*need_points) and spn == "Cloud":
            subject = "Bluepoints warning"
            html_content = loader.render_to_string(
                warning_email_template,
                {
                    "bluepoints": points,
                    "instance": server.name,
                }
            )
            user_list = [user.username]
            send_mail_task(subject, html_content, jsonpickle.encode(user_list))
    elif points < need_points and spn == "Cloud":
        today = datetime.datetime.now().strftime("%m-%d-%y")
        snapshot_name = "%s-%s" % (today, server.name)
        try:
            nova_client = get_nova_client(region_name=region_name, auth_url=auth_url)
            snapshot = nova_client.servers.create_image(server.id, snapshot_name)
            while True:
                server = nova_client.servers.get(server.id)
                task_state = getattr(server, "OS-EXT-STS:task_state", "")
                if not task_state:
                    break
            meta = {
                "owner": server.tenant_id,
                "properties": {
                    "user_id": server.user_id,
                }
            }
            keystone_client = get_keystone_client(auth_url=auth_url)
            token = keystone_client.auth_ref['token']['id']
            url = ""
            for service in keystone_client.auth_ref['serviceCatalog']:
                if service['type'] == 'image':
                    for endpoint in service['endpoints']:
                        if endpoint['region'] == region_name:
                            url = endpoint['adminURL']
            glance_client = get_glance_client(token=token, auth_url=url)
            glance_client.images.update(snapshot, **meta)
            snapshot_history = SnapshotHistory()
            snapshot_history.instance_name = server.name
            snapshot_history.region = region_name
            snapshot_history.snapshot_id = snapshot
            snapshot_history.snapshot_name = snapshot_name
            snapshot_history.user_name = user.username
            snapshot_history.user_id = server.user_id
            snapshot_history.save()
            nova_client.servers.delete(server.id)
        except Exception, ex:
            LOG.debug('%s %s', Exception, ex)
