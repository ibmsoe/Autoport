from django.conf import settings
import glanceclient

AUTH_URL = getattr(settings, 'OPENSTACK_KEYSTONE_URL', '')
OPENSTACK_CONFIG_BACKEND = getattr(settings, 'OPENSTACK_CONFIG_BACKEND', {})
ENDPOINT_TYPE = 'adminURL'
USER = OPENSTACK_CONFIG_BACKEND.get('user', '')
PASS = OPENSTACK_CONFIG_BACKEND.get('password', '')
TENANT = OPENSTACK_CONFIG_BACKEND.get('tenant', '')


def get_glance_client(token="", auth_url=AUTH_URL):
    return glanceclient.Client('1', auth_url, token=token)
