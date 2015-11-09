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

from collections import defaultdict
import logging

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.template import defaultfilters as filters
from django.utils.http import urlencode
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy

from horizon import tables
from horizon.utils.memoized import memoized  # noqa

from openstack_dashboard import api
from openstack_dashboard.api import base

from openstack_dashboard.models import MarketImageInfo

NOT_LAUNCHABLE_FORMATS = ['aki', 'ari']

LOG = logging.getLogger(__name__)

PUBLISH_IMAGE_BACKEND = getattr(settings, 'PUBLISH_IMAGE_BACKEND', {})


def filter_tenants():
    return getattr(settings, 'IMAGES_LIST_FILTER_TENANTS', [])


@memoized
def filter_tenant_ids():
    return map(lambda ft: ft['tenant'], filter_tenants())


class InstancesFilterAction(tables.FilterAction):
    filter_type = "server"
    filter_choices = (('name', _("Instance Name"), True),
                      ('status', _("Status ="), True),
                      ('image', _("Image ID ="), True),
                      ('flavor', _("Flavor ID ="), True))



class OwnerFilter(tables.FixedFilterAction):
    def get_fixed_buttons(self):
        def make_dict(text, tenant, icon):
            return dict(text=text, value=tenant, icon=icon)

        buttons = [make_dict(_("All types"), "all", '')]
        for item in PUBLISH_IMAGE_BACKEND['type_choices']:
            buttons.append(make_dict(item[1], item[0], ''))
        return buttons

    def categorize(self, table, images):
        user_tenant_id = table.request.user.tenant_id
        tenants = defaultdict(list)
        for im in images:
            categories = get_image_categories(im, user_tenant_id)
            for category in categories:
                tenants[category].append(im)
                tenants['all'].append(im)
        return tenants


def get_image_categories(im, user_tenant_id):
    categories = []
    for item in PUBLISH_IMAGE_BACKEND['type_choices']:
        if im.properties.get("base_type", "") == item[0]:
            categories.append(item[0])
    return categories


def get_image_name(image):
    return getattr(image, "name", None) or image.id


def get_image_type(image):
    return getattr(image, "properties", {}).get("image_type", "image")


def get_format(image):
    format = getattr(image, "disk_format", "")
    # The "container_format" attribute can actually be set to None,
    # which will raise an error if you call upper() on it.
    if format is not None:
        return format.upper()


def get_title(image):
    title = ""
    try:
        market_image = MarketImageInfo.objects.get(final_image_id=image.id)
        language = getattr(image, "properties", {}).get("language", "")
        if language == "en":
            title = market_image.extra_info.get("final_info", {}).get("title_en", "")
        elif language == "zh-cn":
            title = market_image.extra_info.get("final_info", {}).get("title", "")
            if title == "":
                title = market_image.extra_info.get("final_info", {}).get("title_en", "")
    except Exception:
        pass

    LOG.debug('%s %s', image.id, title)
    return title


def get_introduction(image):
    introduction = ""
    try:
        market_image = MarketImageInfo.objects.get(final_image_id=image.id)
        language = getattr(image, "properties", {}).get("language", "")
        if language == "en":
            introduction = market_image.extra_info.get("final_info", {}).get("introduction_en", "")
        elif language == "zh-cn":
            introduction = market_image.extra_info.get("final_info", {}).get("introduction", "")
            if introduction == "":
                introduction = market_image.extra_info.get("final_info", {}).get("introduction_en", "")
    except Exception:
        pass

    return introduction


def get_details(image):
    details = ""
    try:
        market_image = MarketImageInfo.objects.get(final_image_id=image.id)
        language = getattr(image, "properties", {}).get("language", "")
        if language == "en":
            details = market_image.extra_info.get("final_info", {}).get("details_en", "")
        elif language == "zh-cn":
            details = market_image.extra_info.get("final_info", {}).get("details", "")
            if details == "":
                details = market_image.extra_info.get("final_info", {}).get("details_en", "")
    except Exception:
        pass

    return details


def get_tags(image):
    tags = []
    try:
        market_image = MarketImageInfo.objects.get(final_image_id=image.id)
        tags = market_image.tags.get("final_tags", [])
    except Exception:
        pass

    return tags


def get_top(image):
    top_image = MarketImageInfo.objects.all().order_by('-downloads')[:3]
    for market_image in top_image:
        if image.id == market_image.final_image_id:
            return True

    return False


def get_integrated_software(image):
    integrated_software = ""
    try:
        market_image = MarketImageInfo.objects.get(final_image_id=image.id)
        integrated_software = market_image.extra_info.get("final_info", {}).get("integrated_software", "")
    except Exception:
        pass

    return integrated_software


def get_downloads(image):
    downloads = 0
    try:
        market_image = MarketImageInfo.objects.get(final_image_id=image.id)
        downloads = market_image.downloads
    except Exception:
        pass

    return downloads


def get_base_type(image):
    for item in PUBLISH_IMAGE_BACKEND['type_choices']:
        type_name = getattr(image, "properties", {}).get("base_type", "")
        if type_name == item[0]:
            return item[1]
    return ""


def get_points(image):
    return getattr(image, "properties", {}).get("points", 0)


def get_launch_link(image):
    check_instance_quota = getattr(image, "properties", {}).get("check_instance_quota", True)
    if not check_instance_quota:
        return "javascript:void(0);"
    url = reverse('horizon:project:instances:launch_market_image',
                  args=[image.id])

    return url


def get_creator(image):
    creator = ""
    try:
        market_image = MarketImageInfo.objects.get(final_image_id=image.id)
        creator = market_image.creator
    except Exception:
        pass

    return creator


class UpdateRow(tables.Row):
    ajax = True

    def get_data(self, request, image_id):
        image = api.glance.image_get(request, image_id)
        return image

    def load_cells(self, image=None):
        super(UpdateRow, self).load_cells(image)
        # Tag the row with the image category for client-side filtering.
        image = self.datum
        my_tenant_id = self.table.request.user.tenant_id
        image_categories = get_image_categories(image, my_tenant_id)
        for category in image_categories:
            self.classes.append('category-' + category)


class ImagesMarketTable(tables.DataTable):
    name = tables.Column(get_image_name,
                         verbose_name=_("Snapshot Name"))

    title = tables.Column(get_title,
                          verbose_name=_("Image Title"))

    introduction = tables.Column(get_introduction,
                                 verbose_name=_("Image Introduction"))

    detail = tables.Column(get_details,
                           verbose_name=_("Image Details"))

    downloads = tables.Column(get_downloads,
                              verbose_name=_("Image Downloads"))

    creator = tables.Column(get_creator,
                            verbose_name=_("Image Creator"))

    launch_link = tables.Column(get_launch_link,
                                verbose_name=_("Image Launch"))

    integrated_software = tables.Column(get_integrated_software,
                                        verbose_name=_("Integrated Software"))

    is_top = tables.Column(get_top,
                           verbose_name=_("Top"))

    points = tables.Column(get_points,
                           verbose_name=_("Points"))

    tags = tables.Column(get_tags,
                         verbose_name=_("Tags"))

    base_type = tables.Column(get_base_type,
                              verbose_name=_("Base Type"))

    class Meta:
        name = "snapshots"
        row_class = UpdateRow
        template = "project/images/market/market_table.html"
        verbose_name = _("Images")
        table_actions = (OwnerFilter, )
        table_actions_template = "project/images/market/table_actions.html"
        pagination_param = "image_marker"
