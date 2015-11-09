import json
import logging
from random import Random
from django.conf import settings
import requests

from rest_framework import viewsets, status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from openstack_dashboard.api.neutron import SecurityGroup
from openstack_dashboard.restful.serializers import UserSerializer
from base.keystone import get_keystone_client
from base.neutron import get_neutron_client
from openstack_dashboard.utils import filters

__author__ = 'yuehaitao'

LOG = logging.getLogger(__name__)
REGIONS = getattr(settings, 'REGIONS', [])


def random_password(random_length=9):
    password = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()

    for i in range(random_length):
        password += chars[random.randint(0, length)]

    return password


class UserViewSet(viewsets.ViewSet):

    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    def __init__(self):
        super(UserViewSet, self).__init__()
        self.tenant_id = ""
        self.user_id = ""
        self.response = {
            "status": "ok",
            "message": "",
            "success": True,
        }

    def _register_user(self, username="", password=""):
        for region in REGIONS:
            try:
                kc = get_keystone_client(auth_url=region[0])
                tenant = kc.tenants.create(username, "", True)
                tenant_id = getattr(tenant, "id", "")
                user = kc.users.create(username, password, username, tenant_id)
                user_id = getattr(user, "id", "")
            except Exception as exc:
                self.response['message'] = 'Create user error: %s' % exc
                return False
            else:
                LOG.debug('HIGHTALL %s %s', tenant_id, user_id)
                if region[2] == 'master':
                    self.tenant_id = tenant_id
                    self.user_id = user_id

        return True

    def _update_remote_database(self, username):
        headers = {"Content-Type": "application/json"}
        for region in REGIONS:
            if region[2] == 'slave':
                update_database_url = region[3] % {'user_name': username}
                requests.post(update_database_url, headers=headers,
                              data=json.dumps({"user_id": self.user_id, "project_id": self.tenant_id}))

    def _set_default_rule(self, username, password):
        for region in REGIONS:
            if region[2] != '':
                try:
                    endpoint_url = ""
                    kc = get_keystone_client(auth_url=region[0], username=username,
                                             password=password, tenant_name=username,
                                             endpoint_type="publicURL")
                    token = kc.auth_ref.get("token", {}).get("id", "")
                    services = kc.auth_ref.get("serviceCatalog", [])
                    for service in services:
                        service_type = service.get("type", "")
                        if service_type == "network":
                            for endpoint in service.get("endpoints", []):
                                if endpoint.get("region", "") == region[1]:
                                    endpoint_url = endpoint.get("publicURL", "")
                    neutron = get_neutron_client(token=token, auth_url=region[0],
                                                 endpoint_url=endpoint_url)
                except Exception as exc:
                    self.response['message'] = 'Set security default rule error: %s' % exc
                    return False
                else:
                    secgroups = neutron.list_security_groups(tenant_id=self.tenant_id)
                    groups = [SecurityGroup(g) for g in secgroups.get('security_groups')]
                    for group in groups:
                        if group.name == "default":
                            body = {
                                'security_group_rule': {
                                    'security_group_id': filters.get_int_or_uuid(group.id),
                                    'direction': 'ingress',
                                    'ethertype': 'IPv4',
                                    'protocol': 'tcp',
                                    'port_range_min': '4200',
                                    'port_range_max': '4200',
                                    'remote_ip_prefix': '0.0.0.0/0',
                                    'remote_group_id': None
                                }
                            }
                            neutron.create_security_group_rule(body)
                            body = {
                                'security_group_rule': {
                                    'security_group_id': filters.get_int_or_uuid(group.id),
                                    'direction': 'ingress',
                                    'ethertype': 'IPv4',
                                    'protocol': 'tcp',
                                    'port_range_min': '22',
                                    'port_range_max': '22',
                                    'remote_ip_prefix': '0.0.0.0/0',
                                    'remote_group_id': None
                                }
                            }
                            neutron.create_security_group_rule(body)
                            body = {
                                'security_group_rule': {
                                    'security_group_id': filters.get_int_or_uuid(group.id),
                                    'direction': 'ingress',
                                    'ethertype': 'IPv4',
                                    'protocol': 'icmp',
                                }
                            }
                            neutron.create_security_group_rule(body)
            else:
                headers = {"Content-Type": "application/json"}
                security_url = region[4]
                requests.post(security_url, headers=headers,
                              data=json.dumps({"username": username, "password": password,
                                               "tenant_id": self.tenant_id}))

        return True

    def _register(self, username="", password=""):
        if not self._register_user(username, password):
            return False

        self._update_remote_database(username)

        if not self._set_default_rule(username, password):
            return False

        return True

    def register(self, request):
        serializer = UserSerializer(data=request.data)
        # response = {
        #     "status": "ok",
        #     "message": "",
        #     "success": True,
        # }
        status_code = status.HTTP_200_OK
        if serializer.is_valid():
            username = serializer.data.get("user_name", "")
            password = serializer.data.get("password", "")
            register_status = self._register(username, password)
            if not register_status:
                self.response['status'] = "error"
                self.response['success'] = False
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        else:
            self.response['status'] = "error"
            self.response['success'] = False
            status_code = status.HTTP_400_BAD_REQUEST

        return Response(self.response, status_code)

    def _update_password(self, user_name="", password="", new_password="", method="update"):
        if method == "reset":
            new_password = random_password()
            for region in REGIONS:
                kc = get_keystone_client(auth_url=region[0])
                try:
                    users = kc.users.list()
                    for user in users:
                        if user.name == user_name:
                            kc.users.update_password(user.id, new_password)
                except Exception:
                    return None
        elif method == "update":
            for region in REGIONS:
                try:
                    kc = get_keystone_client(auth_url=region[0], username=user_name, password=password,
                                             tenant_name=user_name, endpoint_type='publicURL')
                    kc.users.update_own_password(password, new_password)
                except Exception:
                    return None

        return new_password

    def update_password(self, request):
        user_name = request.data.get("user_name", "")
        password = request.data.get("password", "")
        new_password = request.data.get("new_password", "")
        method = request.data.get("method", "")
        status_code = status.HTTP_200_OK
        response = {
            "password": new_password,
            "success": True
        }
        if method in ['reset', 'update']:
            new_password = self._update_password(user_name, password, new_password, method)
            if not new_password:
                response['password'] = ""
                response['success'] = False
                status_code = status.HTTP_401_UNAUTHORIZED
            response["password"] = new_password
        else:
            response['success'] = False
            status_code = status.HTTP_405_METHOD_NOT_ALLOWED

        return Response(response, status_code)
