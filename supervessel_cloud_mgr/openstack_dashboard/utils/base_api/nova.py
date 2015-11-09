from django.conf import settings
from novaclient import client

OPENSTACK_CONFIG_BACKEND = getattr(settings, 'OPENSTACK_CONFIG_BACKEND', {})
REGIONS = getattr(settings, 'REGIONS', [])
AUTH_URL = REGIONS[1][0]
ENDPOINT_TYPE = 'adminURL'
USER = OPENSTACK_CONFIG_BACKEND.get('user', '')
PASS = OPENSTACK_CONFIG_BACKEND.get('password', '')
TENANT = OPENSTACK_CONFIG_BACKEND.get('tenant', '')


def get_nova_client(region_name="Beijing", auth_url=AUTH_URL):
    return client.Client(1.1, USER, PASS, TENANT, auth_url,
                         endpoint_type=ENDPOINT_TYPE,
                         service_type="compute",
                         region_name=region_name)
