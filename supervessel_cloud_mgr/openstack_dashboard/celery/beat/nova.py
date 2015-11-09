import logging

from celery.schedules import crontab
from celery.task import periodic_task
from django.conf import settings

from openstack_dashboard.celery.base.nova import get_nova_client, handle_server

AUTH_URL = getattr(settings, 'OPENSTACK_KEYSTONE_URL', '')
OPENSTACK_CONFIG_BACKEND = getattr(settings, 'OPENSTACK_CONFIG_BACKEND', {})
ENDPOINT_TYPE = 'adminURL'
USER = OPENSTACK_CONFIG_BACKEND.get('user', '')
PASS = OPENSTACK_CONFIG_BACKEND.get('password', '')
TENANT = OPENSTACK_CONFIG_BACKEND.get('tenant', '')
REGIONS = getattr(settings, 'REGIONS', [])

LOG = logging.getLogger(__name__)


@periodic_task(name='beat.handle_servers',
               run_every=crontab(hour="23", minute="55", day_of_week="*"))
def handle_servers():
    i = 1
    for region in REGIONS:
        search_opts = {
            'marker': None,
            'all_tenants': True,
            'paginate': True,
            'limit': 21,
        }
        LOG.debug('handle_servers %s %s', region[0], region[1])
        nc = get_nova_client(region_name=region[1], auth_url=region[0])
        while True:
            try:
                servers = nc.servers.list(True, search_opts)
            except Exception as exc:
                LOG.debug('error %s', exc)
                break
            else:
                if len(servers) == 0:
                    break
                search_opts['marker'] = servers[-1].id
                for server in servers:
                    LOG.debug('HIGHTALL will handle %s %s %s', i, server.name, region[1])
                    handle_server(server, i, region)
                    i += 1
