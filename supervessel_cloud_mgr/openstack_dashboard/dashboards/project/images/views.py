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

from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tables
from openstack_dashboard import api
from openstack_dashboard.dashboards.project.images.snapshots \
    import tables as snapshots_tables


class IndexView(tables.DataTableView):
    table_class = snapshots_tables.SnapshotsTable
    template_name = 'project/images/snapshots/index.html'

    def has_prev_data(self, table):
        return getattr(self, "_prev_%s" % table.name, False)

    def has_more_data(self, table):
        return getattr(self, "_more_%s" % table.name, False)

    def get_data(self):
        filters = {
            "property-image_type": "snapshot",
            "property-user_id": self.request.user.id,
        }
        marker = self.request.GET.get(
            snapshots_tables.SnapshotsTable._meta.pagination_param, None)
        try:
            (images, self._more, self._prev) = api.glance.image_list_detailed(
                self.request, marker=marker, filters=filters)

        except Exception:
            images = []
            exceptions.handle(self.request, _("Unable to retrieve images."))

        return images