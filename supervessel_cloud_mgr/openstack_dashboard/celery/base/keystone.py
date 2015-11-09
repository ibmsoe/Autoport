from django.conf import settings

__author__ = 'yuehaitao'
from keystoneclient.v2_0 import client

AUTH_URL = getattr(settings, 'OPENSTACK_KEYSTONE_URL', '')
OPENSTACK_CONFIG_BACKEND = getattr(settings, 'OPENSTACK_CONFIG_BACKEND', {})
USER = OPENSTACK_CONFIG_BACKEND.get('user', '')
PASS = OPENSTACK_CONFIG_BACKEND.get('password', '')
TENANT = OPENSTACK_CONFIG_BACKEND.get('tenant', '')


def get_keystone_client(auth_url=AUTH_URL):
    return client.Client(username=USER, password=PASS, tenant_name=TENANT,
                         auth_url=auth_url, endpoint_type='adminURL')


def get_user(user_id='', auth_url=AUTH_URL):
    return get_keystone_client(auth_url=auth_url).users.get(user_id)


def get_role(user_id='', tenant_id='', auth_url=AUTH_URL):
    return get_keystone_client(auth_url=auth_url).roles.roles_for_user(user_id, tenant_id)
