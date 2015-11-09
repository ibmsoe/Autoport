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


class PublishImage(forms.SelfHandlingForm):
    image_id = forms.CharField(label=_("Snapshot ID"),
                               widget=forms.HiddenInput(),
                               required=False)

    image_final = forms.ChoiceField(label=_("Final image to be used"),
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

    def __init__(self, *args, **kwargs):
        super(PublishImage, self).__init__(*args, **kwargs)
        self.market_image = None
        self.email_template = 'admin/images_market/publish_email.html'
        filters = {
            'is_public': True,
            'property-image_type': "custom_image"
        }
        marker = self.request.GET.get("image_marker", None)
        (images, self._more, self._prev) = api.glance.image_list_detailed(
            self.request, marker=marker, filters=filters)
        choices = [(image.id, image.name) for image in images]
        self.fields['image_final'].choices = choices

    def mail_to_request_user(self):
        send_to = [self.market_image.creator]
        image_type = ""
        for type_choice in PUBLISH_IMAGE_BACKEND['type_choices']:
            if self.market_image.base_type == type_choice[0]:
                image_type = type_choice[1]
        final_info = self.market_image.extra_info.get("final_info", {})
        topic = {
            'creator_id': self.market_image.creator_id,
            'creator': self.market_image.creator,
            'image_id': self.market_image.id,
            'final_image_id': self.market_image.final_image_id,
            'title_en': final_info.get('title_en', ""),
            'details_en': final_info.get('details_en', ""),
            'integrated_software': final_info.get('integrated_software', ""),
            'introduction_en': final_info.get('introduction_en', ""),
            'title': final_info.get('title', ""),
            'details': final_info.get('details', ""),
            'introduction': final_info.get('introduction', ""),
            'image_type': image_type,
            'tags': self.market_image.tags.get("final_tags", "")
        }
        subject = '%s is published successful' % self.market_image.id
        html_content = loader.render_to_string(self.email_template, {'topic': topic})
        send_mail_task.delay(subject, html_content, jsonpickle.encode(send_to))

    def update_image(self):
        meta = {"is_public": True,
                "properties": {
                    'place_holder': "market",
                    "base_type": self.market_image.base_type
                }}

        try:
            image = api.glance.image_update(self.request, self.market_image.final_image_id, **meta)
            messages.success(self.request, _('Image was successfully updated.'))
            return image
        except Exception, ex:
            LOG.debug('%s %s', Exception, ex)
            pass

    def handle(self, request, data):
        try:
            market_image = MarketImageInfo.objects.get(id=data['image_id'])
            message = _("Publish snapshot %s successful") % market_image.id
            market_image.final_image_id = data['image_final']
            final_tags = data['tags'].split(',')
            final_info = {
                'title_en': data['title_en'],
                'details_en': data['details_en'],
                'introduction_en': data['introduction_en'],
                'integrated_software': data['integrated_software'],
                'introduction': data['introduction'],
                'title': data['title'],
                'details': data['details']
            }
            market_image.extra_info.update({'final_info': final_info})
            market_image.tags.update({'final_tags': final_tags})
            market_image.published = True
            market_image.save()
            self.market_image = market_image
            self.update_image()
            self.mail_to_request_user()
            messages.success(request, message)
            return True
        except Exception, ex:
            LOG.debug('%s %s', Exception, ex)
            return False


class UpdateImage(forms.SelfHandlingForm):
    image_id = forms.CharField(label=_("Snapshot ID"),
                               widget=forms.HiddenInput(),
                               required=False)

    image_final = forms.CharField(label=_("Final image to be used"),
                                  widget=forms.TextInput(attrs={"disabled": "disabled"}),
                                  required=False)

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

    def __init__(self, *args, **kwargs):
        super(UpdateImage, self).__init__(*args, **kwargs)
        self.market_image = None
        self.email_template = 'admin/images_market/publish_email.html'

    def mail_to_request_user(self):
        send_to = [self.market_image.creator]
        image_type = ""
        for type_choice in PUBLISH_IMAGE_BACKEND['type_choices']:
            if self.market_image.base_type == type_choice[0]:
                image_type = type_choice[1]
        topic = {
            'creator_id': self.market_image.creator_id,
            'creator': self.market_image.creator,
            'image_id': self.market_image.id,
            'final_image_id': self.market_image.final_image_id,
            'title_en': self.market_image.extra_info['final_info']['title_en'],
            'details_en': self.market_image.extra_info['final_info']['details_en'],
            'integrated_software': self.market_image.extra_info['final_info']['integrated_software'],
            'introduction_en': self.market_image.extra_info['final_info']['introduction_en'],
            'title': self.market_image.extra_info['final_info']['title'],
            'details': self.market_image.extra_info['final_info']['details'],
            'introduction': self.market_image.extra_info['final_info']['introduction'],
            'image_type': image_type,
            'tags': self.market_image.tags['final_tags']
        }
        subject = 'information for image %s is updated.' % self.market_image.id
        html_content = loader.render_to_string(self.email_template, {'topic': topic})
        send_mail_task.delay(subject, html_content, jsonpickle.encode(send_to))

    def handle(self, request, data):
        try:
            market_image = MarketImageInfo.objects.get(id=data['image_id'])
            message = _("Update snapshot %s successful") % market_image.id
            final_tags = data['tags'].split(',')
            info = {
                'title_en': data['title_en'],
                'details_en': data['details_en'],
                'introduction_en': data['introduction_en'],
                'integrated_software': data['integrated_software'],
                'introduction': data['introduction'],
                'title': data['title'],
                'details': data['details']
            }
            extra_info = market_image.extra_info
            extra_info['final_info'] = info
            market_image.extra_info = extra_info
            tags = market_image.tags
            tags['final_tags'] = final_tags
            market_image.tags = tags
            market_image.published = True
            market_image.save()
            self.market_image = market_image
            self.mail_to_request_user()
            messages.success(request, message)
            return True
        except Exception, ex:
            LOG.error('%s %s', Exception, ex)
            return False
