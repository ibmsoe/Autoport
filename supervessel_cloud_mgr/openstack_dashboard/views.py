# Copyright 2012 Nebula, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import logging
import json

from datetime import datetime, timedelta
from django import shortcuts
from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import django.views.decorators.vary

# from oauth2_login_client.views import login_redirect
from openstack_auth import forms
from django.utils import translation
from django.views.generic import View, TemplateView
import humanize

import horizon
from horizon import base
from openstack_dashboard.models import PointRate, Notification, AcceleratorInfo, ResourcePoint, VpnAccount, \
    OperationHistory, ACTIVE, CAPI
from openstack_dashboard.utils import get_user_points
from django.utils.translation import ugettext_lazy as _
from openstack_dashboard.dashboards.project.images \
    import utils as image_utils
from django.views.decorators.cache import cache_page
from openstack_dashboard.dashboards.project.instances \
    import utils as instance_utils

from openstack_dashboard import api
from openstack_dashboard.utils.capi import get_capi_count

LOG = logging.getLogger(__name__)

AUTHENTICATION_BACKENDS = getattr(settings, 'AUTHENTICATION_BACKENDS', 'openstack_auth.backend.KeystoneBackend')
OPENSTACK_CONFIG_BACKEND = getattr(settings, 'OPENSTACK_CONFIG_BACKEND', {})
CAPI_QUOTA = OPENSTACK_CONFIG_BACKEND.get("capi_quota", 1)
WEBROOT = getattr(settings, 'WEBROOT', '')


def get_user_home(user):
    dashboard = None
    if user.is_superuser:
        try:
            dashboard = horizon.get_dashboard('admin')
        except base.NotRegistered:
            pass

    if dashboard is None:
        dashboard = horizon.get_default_dashboard()

    return dashboard.get_absolute_url()


@django.views.decorators.vary.vary_on_cookie
def splash(request):
    if request.user.is_authenticated():
        response = shortcuts.redirect(horizon.get_user_home(request.user))
    else:
        form = forms.Login(request)
        response = shortcuts.render(request, 'splash.html', {'form': form})
    if 'logout_reason' in request.COOKIES:
        response.delete_cookie('logout_reason')
    return response


def _one_year():
    now = datetime.utcnow()
    return datetime(now.year + 1, now.month, now.day, now.hour,
                    now.minute, now.second, now.microsecond, now.tzinfo)


def set_language(request):
    lang_code = request.GET.get('language')
    # response = shortcuts.redirect(request.META.get('HTTP_REFERER'))
    redirection = request.META.get('HTTP_REFERER')
    if redirection:
        response = shortcuts.redirect(request.META.get('HTTP_REFERER'))
    else:
        response = shortcuts.redirect(WEBROOT)
    if lang_code and translation.check_for_language(lang_code):
        if hasattr(request, 'session'):
            request.session['django_language'] = lang_code
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code,
                            expires=_one_year())

    return response


class PointsRateJsonView(View):
    def _get_point_rate(self, request):
        flavor_id = request.GET.get('flavor_id')
        points = 0
        try:
            point_rate = PointRate.objects.filter(flavor_id=flavor_id)
            if len(point_rate) > 0:
                for x in point_rate:
                    if x.service_type == 'Cloud':
                        points = x.points
                        break
        except ObjectDoesNotExist:
            pass
        return points

    def get(self, request, *args, **kwargs):
        data = {
            'points': self._get_point_rate(request)
        }
        json_string = json.dumps(data, ensure_ascii=False)
        return HttpResponse(json_string, content_type='text/json')


class UserPointsJsonView(View):
    def get(self, request, *args, **kwargs):
        data = {
            'points': get_user_points(request.user.username)
        }
        json_string = json.dumps(data, ensure_ascii=False)
        return HttpResponse(json_string, content_type='text/json')


class ImageListJsonView(View):
    def _get_images(self, request):
        project_id = None
        for tenant in request.user.authorized_tenants:
            if tenant.enabled:
                project_id = tenant.id
                break
        hypervisor_type = request.GET.get("hypervisor_type")
        sys_type = request.GET.get("sys_type")
        architecture = request.GET.get("architecture")
        accelerator_type = request.GET.get("accelerator_type", "none")
        filters = {
            "property-image_type": "image",
            "property-hypervisor_type": hypervisor_type,
            "property-sys_type": sys_type,
            "property-architecture": architecture,
            "property-accelerator_type": accelerator_type,
        }
        images = image_utils.get_available_images_by_filter(request, project_id, None, filters)
        return [(image.id, image.name) for image in images]

    def get(self, request, *args, **kwargs):
        data = {
            'image_list': self._get_images(request)
        }
        json_string = json.dumps(data, ensure_ascii=False)
        return HttpResponse(json_string, content_type='text/json')


class FlavorsBySourceTypeJsonView(View):
    def _get_flavors(self, request, source_type=None):
        sorted_flavors_list = []

        if source_type:
            flavors = instance_utils.flavor_list(request)
            if flavors:
                new_flavors = []
                for flavor in flavors:
                    flavor_name = str(flavor.name)
                    if flavor_name.startswith(source_type):
                        new_flavors.append(flavor)
                sorted_flavors_list = instance_utils.sort_flavor_list(request, new_flavors)

        return sorted_flavors_list

    def get(self, request, *args, **kwargs):
        source_type = request.GET.get('source_type')
        image_id = request.GET.get('image_id')
        if image_id:
            image = api.glance.image_get(request, image_id)
            source_type = getattr(image, 'properties', {}).get('hypervisor_type', '')
        data = {
            'flavor_list': self._get_flavors(request, source_type)
        }
        json_string = json.dumps(data, ensure_ascii=False)
        return HttpResponse(json_string, content_type='text/json')


class VPNAccountView(TemplateView):
    template_name = "vpn.html"

    def get_context_data(self, **kwargs):
        context = super(VPNAccountView, self).get_context_data(**kwargs)
        vpns = []
        for region in self.request.user.available_services_regions:
            vpn = {"region": region}
            try:
                vpn_tmp = VpnAccount.objects.get(user_id=self.request.user.id, region=region)
                if vpn_tmp.password != "":
                    vpn['title'] = _("VPN Account name: %s") % vpn_tmp.name
                    vpn['body'] = _("Password is %s") % vpn_tmp.password
                else:
                    vpn['title'] = _("<a href='%s'>VPN Configure file %s (Click to download)</a>") % (vpn_tmp.link,
                                                                                                      vpn_tmp.name)
                    vpn['body'] = ""
            except Exception:
                vpn['title'] = "No VPN Account"
            vpns.append(vpn)
        context['vpns'] = vpns
        return context


class NotificationView(TemplateView):
    template_name = "notify.html"

    def get_context_data(self, **kwargs):
        context = super(NotificationView, self).get_context_data(**kwargs)
        notifies = Notification.objects.filter(user_id=self.request.user.id).order_by('-notify_time')[:100]
        for notify in notifies:
            notify.read_status = True
            notify.save()
        context['notifies'] = notifies
        return context


class NofityCountJsonView(View):
    def get(self, request, *args, **kwargs):
        data = {
            'count': Notification.objects.filter(user_id=request.user.id, read_status=False).count()
        }
        json_string = json.dumps(data, ensure_ascii=False)
        return HttpResponse(json_string, content_type='text/json')


class AcceleratorInfoJsonView(View):
    def get(self, request, *args, **kwargs):
        image_id = request.GET.get('image_id')
        data = {
            'points': 1,
            'chip_sn': "",
            'chip_vendor': ""
        }
        if image_id:
            image = api.glance.image_get(request, image_id)
            try:
                points_obj = PointRate.objects.get(flavor_id=image.id)
                data['points'] = points_obj.points
            except Exception, ex:
                LOG.error("%s %s", Exception, ex)
            data['chip_vendor'] = image.properties.get("chip_vendor", "")
            data['chip_sn'] = image.properties.get("chip_sn", "")
            try:
                accelerator = AcceleratorInfo.objects.get(image_id=image.id)
                image_info = json.loads(accelerator.image_info)
                data['acc_desc'] = image_info.get("desc", "")
            except Exception, ex:
                LOG.error("%s %s", Exception, ex)
                data['acc_desc'] = ""
        json_string = json.dumps(data, ensure_ascii=False)
        return HttpResponse(json_string, content_type='text/json')


class ResourceCountJsonView(View):
    def _get_avail_resource_count(self, request):
        source_type = request.GET.get('source_type')
        avail_resource_count = 0
        try:
            resource = ResourcePoint.objects.get(name=source_type, region=request.user.services_region)
            avail_resource_count = resource.count
        except Exception, ex:
            LOG.error("%s %s", Exception, ex)

        return avail_resource_count

    def get(self, request, *args, **kwargs):
        data = {
            'count': self._get_avail_resource_count(request)
        }
        json_string = json.dumps(data, ensure_ascii=False)
        return HttpResponse(json_string, content_type='text/json')


class CheckCapiView(View):
    def get(self, request, *args, **kwargs):
        time_message = ""
        image_id = request.GET.get('image_id')
        fpga_board = ""
        try:
            image = api.glance.image_get(request, image_id)
        except Exception:
            pass
        else:
            fpga_board = image.properties.get("fpga_board", "")

        status, remain_times = get_capi_count(self.request.user.services_region, fpga_board=fpga_board)
        if remain_times:
            time_message = "%s seconds" % remain_times
        data = {
            'status_ok': status,
            'time': time_message,
        }
        LOG.debug('HIGHTALL %s', data)
        json_string = json.dumps(data, ensure_ascii=False)
        return HttpResponse(json_string, content_type='text/json')
