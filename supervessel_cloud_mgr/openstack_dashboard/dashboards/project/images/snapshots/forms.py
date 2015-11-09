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
import logging

from django.core.urlresolvers import reverse
from django.template import loader
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
import jsonpickle
import json

from horizon import exceptions
from horizon import forms
from horizon import messages

from openstack_dashboard import api
from openstack_dashboard import policy
from openstack_dashboard.models import MarketImageInfo
from openstack_dashboard.celery.task.user_operation import send_mail_task

IMAGE_BACKEND_SETTINGS = getattr(settings, 'OPENSTACK_IMAGE_BACKEND', {})
IMAGE_FORMAT_CHOICES = IMAGE_BACKEND_SETTINGS.get('image_formats', [])
OPENSTACK_CONFIG_BACKEND = getattr(settings, 'OPENSTACK_CONFIG_BACKEND', {})
PUBLISH_IMAGE_BACKEND = getattr(settings, 'PUBLISH_IMAGE_BACKEND', {})

LOG = logging.getLogger(__name__)


class CreateSnapshot(forms.SelfHandlingForm):
    instance_id = forms.CharField(label=_("Instance ID"),
                                  widget=forms.HiddenInput(),
                                  required=False)
    snapshot_prefix = forms.CharField(label=_("Snapshot Prefix"),
                                      widget=forms.HiddenInput(),
                                      required=False)
    snapshot_name = forms.CharField(max_length=255, label=_("Snapshot Name"),
                                    widget=forms.TextInput(attrs={'id': 'prepend',
                                                                  'value': '',
                                                                  'placeholder': 'Snapshot name'}))

    def handle(self, request, data):
        snapshot_name = "%s%s" % (data['snapshot_prefix'], data['snapshot_name'])
        try:
            snapshot = api.nova.snapshot_create(request,
                                                data['instance_id'],
                                                snapshot_name)
            # NOTE(gabriel): This API call is only to display a pretty name.
            instance = api.nova.server_get(request, data['instance_id'])
            vals = {"name": snapshot_name, "inst": instance.name}
            messages.success(request, _('Snapshot "%(name)s" created for '
                                        'instance "%(inst)s"') % vals)
            return snapshot
        except Exception:
            redirect = reverse("horizon:project:instances:index")
            exceptions.handle(request,
                              _('Unable to create snapshot.'),
                              redirect=redirect)


class PublishImage(forms.SelfHandlingForm):
    snapshot_id = forms.CharField(label=_("Snapshot ID"),
                                  widget=forms.HiddenInput(),
                                  required=False)

    base_type = forms.ChoiceField(label=_("Choose your type"),
                                  choices=PUBLISH_IMAGE_BACKEND['type_choices'],
                                  required=True)

    password = forms.CharField(label=_("Password for opuser"),
                               required=True)

    root_password = forms.CharField(label=_("Password for root"),
                                    required=True)

    tags = forms.CharField(max_length=255,
                           widget=forms.TextInput(attrs={'class': 'tagsinput', 'data-role': 'tagsinput'}),
                           help_text=_("Press enter for input multi tags."),
                           label=_("Tags"), required=True)

    introduction_en = forms.CharField(max_length=65535, label=_("English Introduction (Required)"), required=True)

    title_en = forms.CharField(max_length=255, label=_("English Title (Required)"), required=True)

    details_en = forms.CharField(widget=forms.Textarea(attrs={'name': 'details_en_editor'}), required=False,
                                 label=_("English Details (Required)"))

    integrated_software = forms.CharField(max_length=255, label=_("Integrated Software (Required)"), required=True)

    introduction = forms.CharField(max_length=65535, label=_("Chinese Introduction (Optional)"), required=False)

    title = forms.CharField(max_length=255, label=_("Chinese Title (Optional)"), required=False)

    details = forms.CharField(widget=forms.Textarea(attrs={'name': 'details_editor'}), required=False,
                              label=_("Chinese Details (Optional)"))

    def __init__(self, *args, **kwargs):
        super(PublishImage, self).__init__(*args, **kwargs)
        self.market_image = None
        self.email_template = 'project/images/snapshots/publish_email.html'

    def mail_to_admin(self):
        send_to = []
        base_type = ""
        for config in OPENSTACK_CONFIG_BACKEND['configs']:
            if config['region'] == self.request.user.services_region:
                send_to = config['image_admin_email_list']
        for type_choice in PUBLISH_IMAGE_BACKEND['type_choices']:
            if self.market_image.base_type == type_choice[0]:
                base_type = type_choice[1]
        info = self.market_image.extra_info.get("info", {})
        tags = self.market_image.tags.get("tags", "")
        topic = {
            'request_title': _("request publish image"),
            'creator_id': self.market_image.creator_id,
            'creator': self.market_image.creator,
            'image_id': self.market_image.id,
            'title_en': info.get("title_en", ""),
            'details_en': info.get('details_en', ""),
            'integrated_software': info.get('integrated_software', ""),
            'introduction_en': info.get('introduction_en', ""),
            'title': info.get('title', ""),
            'details': info.get('details', ""),
            'introduction': info.get('introduction', ""),
            'password': info.get('password', ''),
            'root_password': info.get('root_password', ''),
            'base_type': base_type,
            'tags': tags
        }
        subject = _('Region (%s) %s request publish image %s') % (_("%s" % self.request.user.services_region),
                                                                  self.market_image.creator, self.market_image.id)
        html_content = loader.render_to_string(self.email_template, {'topic': topic})
        send_mail_task.delay(subject, html_content, jsonpickle.encode(send_to))

    def handle(self, request, data):
        try:
            snapshot = api.glance.image_get(request, data['snapshot_id'])
            message = _("Request publish snapshot %s successful") % snapshot.name
        except Exception, ex:
            message = _("Request Publish snapshot successful")
            LOG.error("%s %s", Exception, ex)
        market_image = MarketImageInfo()
        market_image.id = data['snapshot_id']
        market_image.base_type = data['base_type']
        market_image.creator = request.user.username
        market_image.creator_id = request.user.id
        tags = data['tags'].split(',')
        info = {
            'title_en': data['title_en'],
            'details_en': data['details_en'],
            'introduction_en': data['introduction_en'],
            'integrated_software': data['integrated_software'],
            'introduction': data['introduction'],
            'title': data['title'],
            'details': data['details'],
            'password': data['password'],
            'root_password': data['root_password'],
        }
        market_image.extra_info = {'info': info}
        market_image.tags = {'tags': tags}
        market_image.save()
        self.market_image = market_image
        self.mail_to_admin()
        messages.success(request, message)
        return True


class UpdateSnapshotForm(forms.SelfHandlingForm):
    snapshot_id = forms.CharField(widget=forms.HiddenInput())

    base_type = forms.ChoiceField(label=_("Choose your type"),
                                  choices=PUBLISH_IMAGE_BACKEND['type_choices'],
                                  required=True)

    tags = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'tagsinput', 'data-role': 'tagsinput'}),
                           label=_("Tags"), required=True)

    introduction_en = forms.CharField(max_length=65535, label=_("English Introduction (Required)"), required=True)

    title_en = forms.CharField(max_length=255, label=_("English Title (Required)"), required=True)

    details_en = forms.CharField(widget=forms.Textarea(attrs={'name': 'details_en_editor'}), required=True,
                                 label=_("English Details (Required)"))

    integrated_software = forms.CharField(max_length=255, label=_("Integrated Software (Required)"), required=True)

    introduction = forms.CharField(max_length=65535, label=_("Chinese Introduction (Optional)"), required=False)

    title = forms.CharField(max_length=255, label=_("Chinese Title (Optional)"), required=False)

    details = forms.CharField(widget=forms.Textarea(attrs={'name': 'details_editor'}), required=False,
                              label=_("Chinese Details (Optional)"))

    def __init__(self, request, *args, **kwargs):
        super(UpdateSnapshotForm, self).__init__(request, *args, **kwargs)
        self.email_template = 'project/images/snapshots/publish_email.html'
        self.market_image = None

    def mail_to_admin(self):
        send_to = []
        base_type = ""
        for config in OPENSTACK_CONFIG_BACKEND['configs']:
            if config['region'] == self.request.user.services_region:
                send_to = config['image_admin_email_list']
        for type_choice in PUBLISH_IMAGE_BACKEND['type_choices']:
            if self.market_image.base_type == type_choice[0]:
                base_type = type_choice[1]
        info = self.market_image.extra_info.get("info", {})
        tags = self.market_image.tags.get("tags", "")
        topic = {
            'request_title': _("request update information for image"),
            'creator_id': self.market_image.creator_id,
            'creator': self.market_image.creator,
            'image_id': self.market_image.id,
            'title_en': info.get("title_en", ""),
            'details_en': info.get('details_en', ""),
            'integrated_software': info.get('integrated_software', ""),
            'introduction_en': info.get('introduction_en', ""),
            'title': info.get('title', ""),
            'details': info.get('details', ""),
            'introduction': info.get('introduction', ""),
            'base_type': base_type,
            'tags': tags
        }
        subject = _('%s request update publish image %s') % (self.market_image.creator, self.market_image.id)
        html_content = loader.render_to_string(self.email_template, {'topic': topic})
        LOG.debug('send mail to admin')
        send_mail_task.delay(subject, html_content, jsonpickle.encode(send_to))

    def handle(self, request, data):
        send_mail = False
        try:
            snapshot = api.glance.image_get(request, data['snapshot_id'])
            message = _("Request update information for snapshot %s successful") % snapshot.name
        except Exception, ex:
            LOG.error('%s %s', Exception, ex)
            message = _("Request update information for snapshot successful")

        try:
            market_image = MarketImageInfo.objects.get(id=data['snapshot_id'])
            tags = data['tags'].split(',')
            info = {
                'title_en': data['title_en'],
                'details_en': data['details_en'],
                'introduction_en': data['introduction_en'],
                'integrated_software': data['integrated_software'],
                'introduction': data['introduction'],
                'title': data['title'],
                'details': data['details']
            }
            if cmp(info, market_image.extra_info.get("info", {})):
                send_mail = True
            market_image.extra_info.update({'info': info})
            market_image.tags.update({'tags': tags})
            market_image.base_type = data['base_type']
            market_image.save()
            self.market_image = market_image
            if send_mail:
                self.mail_to_admin()
            messages.success(request, message)
            return True
        except Exception, ex:
            LOG.error("%s %s", Exception, ex)
            messages.error(request, _("You didn't publish this image!"))
            return False
