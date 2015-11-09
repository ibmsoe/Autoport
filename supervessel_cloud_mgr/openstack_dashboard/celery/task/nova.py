from time import sleep
import logging

from django.conf import settings
import jsonpickle
from celery import task

from openstack_dashboard import api

LOG = logging.getLogger(__name__)

OPENSTACK_CONFIG_BACKEND = getattr(settings, 'OPENSTACK_CONFIG_BACKEND', {})
OPENSTACK_CUSTOM_BACKEND = getattr(settings, 'OPENSTACK_CUSTOM_BACKEND', {})


@task(name='terminate-instance-operation', bind=True,
      default_retry_delay=10, max_retries=12, time_limit=1800)
def terminate_instance(self, request_pickle, instance_id):
    request = jsonpickle.decode(request_pickle)
    while True:
        try:
            server = api.nova.server_get(request, instance_id)
        except Exception:
            break
        else:
            LOG.debug('HIGHTALL delete %s status %s', server.name, getattr(server, 'OS-EXT-STS:task_state'))
            sleep(5)

    floating_ip_list = api.network.tenant_floating_ip_list(request)
    for floating_ip in floating_ip_list:
        if not floating_ip.get('instance_id', None) and not floating_ip.get('fixed_ip', None):
            LOG.debug('HIGHTALL delete floating ip id %s', floating_ip.id)
            api.network.tenant_floating_ip_release(request, floating_ip.id)

