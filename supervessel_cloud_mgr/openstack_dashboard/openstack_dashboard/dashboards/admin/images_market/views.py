import logging

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from horizon import exceptions
from horizon import forms
from horizon import tables
from horizon.utils import memoized
from openstack_dashboard import api
from openstack_dashboard.dashboards.admin.images_market import forms as project_forms
from openstack_dashboard.dashboards.admin.images_market \
    import tables as project_tables
from openstack_dashboard.models import MarketImageInfo

LOG = logging.getLogger(__name__)
PUBLISH_IMAGE_BACKEND = getattr(settings, 'PUBLISH_IMAGE_BACKEND', {})


class IndexView(tables.DataTableView):
    table_class = project_tables.AdminImagesMarketTable
    template_name = 'admin/images_market/index.html'

    def get_data(self):
        return MarketImageInfo.objects.all()


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
