#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   hightall
#   E-mail  :   hightallyht@gmail.com
#   Date    :   14/11/11 06:49:24
#   Desc    :
#

import json
import httplib
import logging

from datetime import datetime
from django.conf import settings

from django.contrib.gis.geoip import GeoIP
import pytz

from openstack_dashboard.models import OperationHistory, DELETED, ACC_TYPE_NONE, PointRate
from openstack_dashboard.utils import user_exc
from cache_utils.decorators import cached

LOG = logging.getLogger(__name__)

USER_QUERY_SETTINGS = getattr(settings, 'USER_QUERY_BACKEND', {})
QUERY_SERVER = USER_QUERY_SETTINGS.get('server', '')
POINTS_TRANSFER_API = USER_QUERY_SETTINGS.get('points_transfer_api', '')
GET_APIKEY_API = USER_QUERY_SETTINGS.get('get_apikey_api', '')
PREAUTH_API = USER_QUERY_SETTINGS.get('preauth_api', '')
USER_POINTS_API = USER_QUERY_SETTINGS.get('user_points_api', '')
APIKEY = USER_QUERY_SETTINGS.get('apikey', '')
ADD_POINTS_API = USER_QUERY_SETTINGS.get('add_points', '')
CONNECTION_TIMEOUT = USER_QUERY_SETTINGS.get('connection_timeout', 1)


def http_request(server, headers, url, body, method):
    conn_http = httplib.HTTPConnection(server, timeout=CONNECTION_TIMEOUT)

    try:
        conn_http.request(method, url, body, headers)
        response = conn_http.getresponse()
    except Exception, ex:
        LOG.error('%s %s', Exception, ex)
        raise user_exc.HTTPInternalServerError(message=ex)

    if response.status == 404:
        raise user_exc.HTTPUnauthorized(message="Not Found")
    elif response.status not in [200, 201, 202, 203]:
        msg = "Some error"
        raise user_exc.HTTPInternalServerError(message=msg)
    else:
        data = json.loads(response.read())
        conn_http.close()
        return data


def get_apikey(username):
    headers = {'Content-type': 'application/json'}
    url = GET_APIKEY_API % {'username': username}
    body = ''

    try:
        data = http_request(QUERY_SERVER, headers, url, body, 'GET')
    except Exception, ex:
        LOG.error('%s %s' % (Exception, ex))

    if 'apikey' in data:
        return data['apikey']

    return None


def transfer_points(_from, _to, amount):
    headers = {
        'Content-type': 'application/json',
        'apikey': APIKEY
    }
    url = POINTS_TRANSFER_API % {'apikey': "supernova-admin-grp"}
    body = json.dumps([{
        'from': _from,
        'to': _to,
        'amount': amount,
    }])
    try:
        data = http_request(QUERY_SERVER, headers, url, body, 'POST')
        return data[0]['success']
    except Exception:
        raise Exception


def preauth(username, amount):
    try:
        apikey = get_apikey(username)
    except Exception, ex:
        LOG.error('%s %s' % (Exception, ex))
        return False, 'no apikey'

    headers = {'Content-type': 'application/json'}
    url = PREAUTH_API % {'apikey': apikey, 'amount': amount}
    body = ''

    LOG.debug('url: %(url)s apikey: %(apikey)s' % {'url': url, 'apikey': apikey})
    try:
        data = http_request(QUERY_SERVER, headers, url, body, 'GET')
    except Exception, ex:
        LOG.error('%s %s' % (Exception, ex))
        return False, 'no data'

    if 'success' not in data:
        return False, 'no success'

    return True, data['code']


# @cached(60*2)
def get_user_points(username):
    headers = {
        'Content-type': 'application/json',
        'apikey': APIKEY
    }
    url = USER_POINTS_API % {'username': username}
    body = ''

    try:
        data = http_request(QUERY_SERVER, headers, url, body, 'GET')
        return data['balance']
    except Exception, ex:
        LOG.error('%s %s', Exception, ex)
        return 0


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
