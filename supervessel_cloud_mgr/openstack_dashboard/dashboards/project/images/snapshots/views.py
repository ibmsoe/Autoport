# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
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

"""
Views for managing instance snapshots.
"""
import logging
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon.utils import memoized

from openstack_dashboard import api

from openstack_dashboard.dashboards.project.images.snapshots \
    import forms as project_forms
from openstack_dashboard.models import MarketImageInfo
from openstack_dashboard.utils.base import random_string

LOG = logging.getLogger(__name__)
PUBLISH_IMAGE_BACKEND = getattr(settings, 'PUBLISH_IMAGE_BACKEND', {})


class CreateView(forms.ModalFormView):
    form_class = project_forms.CreateSnapshot
    template_name = 'project/images/snapshots/create.html'
    success_url = reverse_lazy("horizon:project:images:index")

    @memoized.memoized_method
    def get_object(self):
        try:
            return api.nova.server_get(self.request,
                                       self.kwargs["instance_id"])
        except Exception:
            redirect = reverse('horizon:project:instances:index')
            exceptions.handle(self.request,
                              _("Unable to retrieve instance."),
                              redirect=redirect)

    def get_initial(self):
        instance = self.get_object()
        return {"instance_id": self.kwargs["instance_id"],
                "snapshot_prefix": random_string('s', '-'),
                'snapshot_name': instance.name}

    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        context['instance'] = self.get_object()
        return context


class PublishView(forms.ModalFormView):
    form_class = project_forms.PublishImage
    template_name = 'project/images/snapshots/publish.html'
    success_url = reverse_lazy("horizon:project:images:index")

    @memoized.memoized_method
    def get_object(self):
        try:
            return api.glance.image_get(self.request,
                                        self.kwargs['snapshot_id'])
        except Exception:
            redirect = reverse('horizon:project:images:index')
            exceptions.handle(self.request,
                              _("Unable to retrieve snapshot."),
                              redirect=redirect)

    def get_initial(self):
        return {"snapshot_id": self.kwargs["snapshot_id"]}

    def get_context_data(self, **kwargs):
        context = super(PublishView, self).get_context_data(**kwargs)
        context['snapshot'] = self.get_object()
        return context


class UpdateView(forms.ModalFormView):
    form_class = project_forms.UpdateSnapshotForm
    template_name = 'project/images/snapshots/update.html'
    success_url = reverse_lazy("horizon:project:images:index")

    @memoized.memoized_method
    def get_object(self):
        try:
            return api.glance.image_get(self.request, self.kwargs['snapshot_id'])
        except Exception:
            msg = _('Unable to retrieve image.')
            url = reverse('horizon:project:images:index')
            exceptions.handle(self.request, msg, redirect=url)

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context['snapshot'] = self.get_object()
        return context

    def get_initial(self):
        snapshot = self.get_object()
        response = {'snapshot_id': self.kwargs['snapshot_id'],
                    'name': getattr(snapshot, 'name', None) or snapshot.id}
        try:
            market_image = MarketImageInfo.objects.get(id=snapshot.id)
            info = market_image.extra_info.get("info", {})
            title_en = info.get("title_en", "")
            introduction_en = info.get("introduction_en", "")
            details_en = info.get("details_en", "")
            title = info.get("title", "")
            introduction = info.get("introduction", "")
            details = info.get("details", "")
            integrated_software = info.get("integrated_software", "")
            response['title_en'] = title_en
            response['base_type'] = market_image.base_type
            response['introduction_en'] = introduction_en
            response['details_en'] = details_en
            response['title'] = title
            response['introduction'] = introduction
            response['details'] = details
            response['integrated_software'] = integrated_software
            response['tags'] = ",".join(market_image.tags['tags'])
        except Exception, ex:
            LOG.error('%s %s', Exception, ex)

        return response
