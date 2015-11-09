# -*- coding: utf-8 -*-
# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 Nebula, Inc.
# Copyright 2012 OpenStack Foundation
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
Views for managing Images and Snapshots.
"""
import logging
from django.shortcuts import render_to_response

from django.utils.translation import ugettext_lazy as _, get_language

from horizon import exceptions
from horizon import tables
from openstack_dashboard import api
from openstack_dashboard.dashboards.project.images.market \
    import tables as market_tables
from openstack_dashboard.models import PointRate
from django.db.models import Min
from openstack_dashboard.utils.check_quota import check_instance_quota

LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = market_tables.ImagesMarketTable
    template_name = 'project/images/market/index.html'

    def has_prev_data(self, table):
        return self._prev
        # return getattr(self, "_prev_%s" % table.name, False)

    def has_more_data(self, table):
        return self._more
        # return getattr(self, "_more_%s" % table.name, False)

    def get_data(self):
        marker = self.request.GET.get(
            market_tables.ImagesMarketTable._meta.pagination_param, None)
        filters = {
            'is_public': True,
            'property-image_type': 'custom_image',
            'property-place_holder': 'market',
        }
        try:
            (images, self._more, self._prev) = api.glance.image_list_detailed(
                self.request, marker=marker, paginate=True, filters=filters)

        except Exception:
            images = []
            exceptions.handle(self.request, _("Unable to retrieve images."))

        market_images = []
        for image in images:
            if not image.is_public:
                continue
            virtual_type = getattr(image, "properties", {}).get("hypervisor_type", "")
            point_rate = PointRate.objects.filter(virtual_type=virtual_type).aggregate(Min('points'))
            image.properties['points'] = point_rate['points__min']
            image.properties['language'] = get_language()
            image.properties['check_instance_quota'], image.properties['quota_result_reason'] = \
                check_instance_quota(self.request)
            market_images.append(image)
        return market_images
