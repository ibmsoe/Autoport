import base64
import json
import logging

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.db import connection
from django.db.models import Count
from django.http import HttpResponse
from django.utils.timezone import now, timedelta
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.views.generic import TemplateView, View
from datetime import datetime, date

from horizon import exceptions
from horizon import forms
from horizon.utils import memoized
from openstack_dashboard.dashboards.admin.images_market import forms as project_forms
from openstack_dashboard.models import MarketImageInfo, OperationHistory, City, \
    DELETED

LOG = logging.getLogger(__name__)
PUBLISH_IMAGE_BACKEND = getattr(settings, 'PUBLISH_IMAGE_BACKEND', {})


class IndexView(TemplateView):
    template_name = "admin/status/index.html"

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        return context


class CJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)


class StatusView(View):
    def _get_launch_operations(self, time_range=None):
        select = {'day': connection.ops.date_trunc_sql('day', 'launch_time')}
        operations = OperationHistory.objects. \
            filter(launch_time__range=time_range). \
            extra(select=select).values('day').annotate(number=Count('id'))
        return [json.dumps(data, cls=CJsonEncoder) for data in operations]

    def _get_delete_operations(self, time_range=None):
        select = {'day': connection.ops.date_trunc_sql('day', 'delete_time')}
        operations = OperationHistory.objects. \
            filter(delete_time__range=time_range, status=DELETED). \
            extra(select=select).values('day').annotate(number=Count('id'))
        return [json.dumps(data, cls=CJsonEncoder) for data in operations]

    def get(self, request, *args, **kwargs):
        start = now().date() - timedelta(days=7) - timedelta(hours=8)
        end = now().date() + timedelta(days=1) - timedelta(hours=8)
        data = {
            'launch_op': self._get_launch_operations((start, end)),
            'delete_op': self._get_delete_operations((start, end))
        }
        json_string = json.dumps(data, ensure_ascii=False)
        return HttpResponse(json_string, content_type='text/json')


class LaunchImageView(View):
    def _get_top10_images(self, time_range=None):
        images = OperationHistory.objects. \
                     filter(launch_time__range=time_range). \
                     values('image_name').annotate(num_images=Count('image_name')).order_by('-num_images')[:10]
        return [json.dumps(data, cls=CJsonEncoder) for data in images]

    def _get_region_launch_count(self, time_range=None):
        regions = OperationHistory.objects.\
            filter(launch_time__range=time_range).exclude(region="").\
            values('region').annotate(num_launch=Count('region')).order_by('-num_launch')
        return [json.dumps(data) for data in regions]

    def get(self, request, *args, **kwargs):
        start = now().date() - timedelta(days=7)
        end = now().date() + timedelta(days=1)
        data = {
            'images': self._get_top10_images((start, end)),
            'regions': self._get_region_launch_count((start, end))
        }
        json_string = json.dumps(data, ensure_ascii=False)
        return HttpResponse(json_string, content_type='text/json')


class GeoInstanceView(View):
    def _get_instance_launch_geos(self, request, time_range=None):
        geo_list = []
        geos = OperationHistory.objects. \
            filter(launch_time__range=time_range).values('city'). \
            annotate(num_launch=Count('id')).order_by('-num_launch')
        for data in geos:
            try:
                city = City.objects.get(en_name=data['city'])
                city_cn_name = base64.b64decode(city.cn_name)
                data['city'] = city_cn_name
            except Exception:
                pass
            geo_list.append(json.dumps(data))
        return geo_list

    def get(self, request, *args, **kwargs):
        start = now().date() - timedelta(days=7)
        end = now().date() + timedelta(days=1)
        geos = self._get_instance_launch_geos(request, (start, end))
        data = {
            'geos': geos,
        }
        json_string = json.dumps(data, ensure_ascii=False)
        return HttpResponse(json_string, content_type='text/json')


class PublishView(forms.ModalFormView):
    form_class = project_forms.PublishImage
    template_name = 'admin/images_market/publish.html'
    success_url = reverse_lazy("horizon:admin:images_market:index")

    @memoized.memoized_method
    def get_object(self):
        try:
            market_image = MarketImageInfo.objects.get(id=self.kwargs['image_id'])
            return market_image
        except Exception:
            redirect = reverse('horizon:admin:images_market:index')
            exceptions.handle(self.request,
                              _("Unable to retrieve snapshot."),
                              redirect=redirect)

    def get_initial(self):
        response = {"image_id": self.kwargs["image_id"]}
        try:
            market_image = MarketImageInfo.objects.get(id=self.kwargs["image_id"])
            for choice in PUBLISH_IMAGE_BACKEND['type_choices']:
                if market_image.base_type == choice[0]:
                    response['image_type'] = choice
            response['image_id'] = market_image.id
            response['tags'] = ",".join(market_image.tags['tags'])
            response['introduction_en'] = market_image.extra_info.get("info", {}).get("introduction_en", "")
            response['title_en'] = market_image.extra_info.get("info", {}).get("title_en", "")
            response['details_en'] = market_image.extra_info.get("info", {}).get("details_en", "")
            response['integrated_software'] = market_image.extra_info.get("info", {}).get("integrated_software", "")
            response['title'] = market_image.extra_info.get("info", {}).get("title", "")
            response['introduction'] = market_image.extra_info.get("info", {}).get("introduction", "")
            response['details'] = market_image.extra_info.get("info", {}).get("details", "")
        except Exception, ex:
            LOG.error('%s %s', Exception, ex)
            pass

        return response

    def get_context_data(self, **kwargs):
        context = super(PublishView, self).get_context_data(**kwargs)
        context['image'] = self.get_object()
        return context


class UpdateView(forms.ModalFormView):
    form_class = project_forms.UpdateImage
    template_name = 'admin/images_market/update.html'
    success_url = reverse_lazy("horizon:admin:images_market:index")

    @memoized.memoized_method
    def get_object(self):
        try:
            market_image = MarketImageInfo.objects.get(id=self.kwargs['image_id'])
            return market_image
        except Exception:
            redirect = reverse('horizon:admin:images_market:index')
            exceptions.handle(self.request,
                              _("Unable to retrieve snapshot."),
                              redirect=redirect)

    def get_initial(self):
        response = {"image_id": self.kwargs["image_id"]}
        try:
            market_image = MarketImageInfo.objects.get(id=self.kwargs["image_id"])
            for choice in PUBLISH_IMAGE_BACKEND['type_choices']:
                if market_image.base_type == choice[0]:
                    response['image_type'] = choice
            response['image_id'] = market_image.id
            response['image_final'] = market_image.final_image_id
            response['tags'] = ",".join(market_image.tags['tags'])
            response['introduction_en'] = market_image.extra_info.get("info", {}).get("introduction_en", "")
            response['title_en'] = market_image.extra_info.get("info", {}).get("title_en", "")
            response['details_en'] = market_image.extra_info.get("info", {}).get("details_en", "")
            response['integrated_software'] = market_image.extra_info.get("info", {}).get("integrated_software", "")
            response['title'] = market_image.extra_info.get("info", {}).get("title", "")
            response['introduction'] = market_image.extra_info.get("info", {}).get("introduction", "")
            response['details'] = market_image.extra_info.get("info", {}).get("details", "")
        except Exception, ex:
            LOG.error('%s %s', Exception, ex)

        return response

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context['image'] = self.get_object()
        return context
