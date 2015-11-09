from django.conf import settings

__author__ = 'yuehaitao'
from keystoneclient.v2_0 import client

AUTH_URL = getattr(settings, 'OPENSTACK_KEYSTONE_URL', '')
OPENSTACK_CONFIG_BACKEND = getattr(settings, 'OPENSTACK_CONFIG_BACKEND', {})
USER = OPENSTACK_CONFIG_BACKEND.get('user', '')
PASS = OPENSTACK_CONFIG_BACKEND.get('password', '')
TENANT = OPENSTACK_CONFIG_BACKEND.get('tenant', '')


def get_keystone_client(auth_url=AUTH_URL, username=USER, password=PASS,
                        tenant_name=TENANT, timeout=None, endpoint_type='adminURL'):
    return client.Client(username=username, password=password, tenant_name=tenant_name,
                         auth_url=auth_url, timeout=timeout, endpoint_type=endpoint_type)


def get_user(user_id='', auth_url=AUTH_URL):
    return get_keystone_client(auth_url=auth_url).users.get(user_id)


def get_role(user_id='', tenant_id='', auth_url=AUTH_URL):
    return get_keystone_client(auth_url=auth_url).roles.roles_for_user(user_id, tenant_id)
