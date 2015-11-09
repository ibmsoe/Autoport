__author__ = 'yuehaitao'
from django.conf import settings

from neutronclient.v2_0 import client

AUTH_URL = getattr(settings, 'OPENSTACK_KEYSTONE_URL', '')
OPENSTACK_CONFIG_BACKEND = getattr(settings, 'OPENSTACK_CONFIG_BACKEND', {})
USER = OPENSTACK_CONFIG_BACKEND.get('user', '')
PASS = OPENSTACK_CONFIG_BACKEND.get('password', '')
TENANT = OPENSTACK_CONFIG_BACKEND.get('tenant', '')


def get_neutron_client(token="", auth_url=AUTH_URL, endpoint_url=""):
    return client.Client(token=token, auth_url=auth_url, endpoint_url=endpoint_url,
                         insecure=False, ca_cert=None)
