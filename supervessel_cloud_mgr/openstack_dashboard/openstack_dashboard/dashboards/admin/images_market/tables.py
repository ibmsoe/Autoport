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

from django.utils.translation import ugettext_lazy as _, ungettext_lazy
from django.conf import settings

from horizon import tables

from openstack_dashboard import api, policy
from openstack_dashboard.dashboards.project.images.images \
    import tables as project_tables
from openstack_dashboard.models import MarketImageInfo

PUBLISH_IMAGE_BACKEND = getattr(settings, 'PUBLISH_IMAGE_BACKEND', {})

LOG = logging.getLogger(__name__)


class AdminCreateImage(project_tables.CreateImage):
    url = "horizon:admin:images:create"


class AdminEditImage(project_tables.EditImage):
    url = "horizon:admin:images:update"

    def allowed(self, request, image=None):
        return True


class UpdateMetadata(tables.LinkAction):
    url = "horizon:admin:images:update_metadata"
    name = "update_metadata"
    verbose_name = _("Update Metadata")
    classes = ("ajax-modal",)
    icon = "pencil"


class PublishImage(policy.PolicyTargetMixin, tables.LinkAction):
    name = "publish_image"
    verbose_name = _("Publish Image")
    classes = ("btn-primary", "ajax-modal")
    url = "horizon:admin:images_market:publish"

    def allowed(self, request, image=None):
        return not image.published


class UpdateImage(policy.PolicyTargetMixin, tables.LinkAction):
    name = "update_image"
    verbose_name = _("Edit Image")
    url = "horizon:admin:images_market:update"
    classes = ("ajax-modal",)

    def allowed(self, request, image=None):
        return image.published


class UnpublishImage(policy.PolicyTargetMixin, tables.DeleteAction):
    name = "unpublish"
    classes = ("btn-danger",)
    icon = "off"
    policy_rules = (("image", "delete_image"),)

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Unpublish Image",
            u"Unpublish Images",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Scheduled unpublish of image",
            u"Scheduled unpublish of images",
            count
        )

    def allowed(self, request, image=None):
        """Allow terminate action if instance not currently being deleted."""
        return image.published

    def action(self, request, obj_id):
        try:
            image = MarketImageInfo.objects.get(id=obj_id)
            meta = {"is_public": False,
                    "properties": {
                        'place_holder': None,
                        "base_type": None,
                    }}
            try:
                api.glance.image_update(request, image.final_image_id, **meta)
                image.final_image_id = ""
                image.published = False
                image.save()
            except Exception, ex:
                LOG.debug('%s %s', Exception, ex)
        except Exception, ex:
            LOG.error("%s %s", Exception, ex)


class UpdateRow(tables.Row):
    ajax = True

    def get_data(self, request, image_id):
        image = api.glance.image_get(request, image_id)
        return image


class AdminImageFilterAction(tables.FilterAction):
    filter_type = "server"
    filter_choices = (('name', _("Image Name ="), True),
                      ('status', _('Status ='), True),
                      ('disk_format', _('Format ='), True),
                      ('size_min', _('Min. Size (MB)'), True),
                      ('size_max', _('Max. Size (MB)'), True))


def get_tags(image):
    return image.tags.get("tags", [])


def get_image_type(image):
    image_type = ""
    for type_choice in PUBLISH_IMAGE_BACKEND['type_choices']:
        if image.base_type == type_choice[0]:
            image_type = type_choice[1]

    return image_type


class AdminImagesMarketTable(tables.DataTable):
    image_id = tables.Column("id",
                             verbose_name=_("Image Id"))

    final_image_id = tables.Column("final_image_id",
                                   verbose_name=_("Final Image Id"))

    creator = tables.Column("creator",
                            verbose_name=_("Creator"))

    image_type = tables.Column(get_image_type,
                               verbose_name=_("Image Type"))

    downloads = tables.Column("downloads",
                              verbose_name=_("Downloads"))

    tags = tables.Column(get_tags,
                         verbose_name=_("Tags"))

    published = tables.Column("published",
                              verbose_name=_("Published"))

    class Meta:
        name = "images"
        row_class = UpdateRow
        verbose_name = _("Images")
        # table_actions = (AdminCreateImage, AdminDeleteImage,
        #                  AdminImageFilterAction)
        # row_actions = (AdminEditImage, UpdateMetadata, AdminDeleteImage)
        row_actions = (PublishImage, UpdateImage, UnpublishImage)

