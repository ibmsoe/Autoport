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

import json
import logging
import operator
import os
from random import Random

from django.template.defaultfilters import filesizeformat  # noqa
from django.utils.text import normalize_newlines  # noqa
from django.utils.translation import ugettext_lazy as _, get_language
from django.utils.translation import ungettext_lazy
from django.views.decorators.debug import sensitive_variables  # noqa
import jsonpickle
from django.template import loader

from django.conf import settings

from horizon import exceptions
from horizon import forms
from horizon.utils import functions
from horizon.utils import validators
from horizon import workflows
from horizon import messages
from openstack_dashboard import api
from openstack_dashboard.api import base
from openstack_dashboard.api import cinder
from openstack_dashboard.usage import quotas
from openstack_dashboard.dashboards.project.images \
    import utils as image_utils
from openstack_dashboard.dashboards.project.instances \
    import utils as instance_utils
from openstack_dashboard.models import ResourcePoint, VpnAccount, PointRate, MarketImageInfo, CAPI, PCIE, ACC_TYPE_NONE
from openstack_dashboard.utils import preauth
from openstack_dashboard.celery.task.user_operation import send_mail_task, transaction_user_points, add_operation

LOG = logging.getLogger(__name__)

CUSTOM_INSTANCE_CONFIG = getattr(settings, 'CUSTOM_INSTANCE_CONFIG', {})
OPENSTACK_CONFIG_BACKEND = getattr(settings, 'OPENSTACK_CONFIG_BACKEND', {})
TYPE_CHOICE_BACKEND = getattr(settings, 'OPENSTACK_TYPE_CHOICE_BACKEND', {})
EMAIL_HOST_USER = getattr(settings, 'EMAIL_HOST_USER', '')


class SelectProjectUserAction(workflows.Action):
    project_id = forms.ChoiceField(label=_("Project"))
    user_id = forms.ChoiceField(label=_("User"))

    def __init__(self, request, *args, **kwargs):
        super(SelectProjectUserAction, self).__init__(request, *args, **kwargs)
        # Set our project choices
        projects = [(tenant.id, tenant.name)
                    for tenant in request.user.authorized_tenants]
        self.fields['project_id'].choices = projects

        # Set our user options
        users = [(request.user.id, request.user.username)]
        self.fields['user_id'].choices = users

    class Meta:
        name = _("Project & User")
        # Unusable permission so this is always hidden. However, we
        # keep this step in the workflow for validation/verification purposes.
        permissions = ("!",)


class SelectProjectUser(workflows.Step):
    action_class = SelectProjectUserAction
    contributes = ("project_id", "user_id")


class SetInstanceDetailsAction(workflows.Action):
    availability_zone = forms.ChoiceField(label=_("Availability Zone"),
                                          required=False)

    source_type = forms.ChoiceField(label=_("Instance Boot Source"),
                                    help_text=_("Choose Your Boot Source "
                                                "Type."))

    instance_snapshot_id = forms.ChoiceField(label=_("Instance Snapshot"),
                                             required=False)

    use_accelerator = forms.ChoiceField(label=_("Whether use accelerator?"),
                                        widget=forms.RadioSelect,
                                        required=False)

    accelerator_type = forms.ChoiceField(label=_("Choose Accelerator Type"),
                                         widget=forms.RadioSelect,
                                         required=False)

    capi = forms.ChoiceField(label=_("Choose Accelerator (single choice)"),
                             widget=forms.RadioSelect,
                             required=False)

    accelerator = forms.MultipleChoiceField(label=_("Choose Accelerator (multi choice)"),
                                            widget=forms.CheckboxSelectMultiple,
                                            required=False,
                                            help_text=_("Click left mouse button"
                                                        " to select accelerators."
                                                        "You can select more accelerator."))

    sys_type = forms.ChoiceField(label=_("OS Type"),
                                 widget=forms.RadioSelect,
                                 required=False)

    architecture = forms.ChoiceField(label=_("Architecture"),
                                     widget=forms.RadioSelect,
                                     required=False)

    image_id = forms.ChoiceField(
        label=_("Image Name"),
        required=False,
        widget=forms.SelectWidget(
            data_attrs=('volume_size',),
            transform=lambda x: ("%s (%s)" % (x.name,
                                              filesizeformat(x.bytes)))))

    flavor = forms.ChoiceField(label=_("Flavor"),
                               help_text=_("Size of image to launch."))

    class Meta:
        name = _("Details")
        help_text_template = ("project/instances/"
                              "_launch_details_help.html")

    def __init__(self, request, context, *args, **kwargs):
        self._init_images_cache()
        self._init_accelerators_cache()
        self.request = request
        self.context = context
        super(SetInstanceDetailsAction, self).__init__(
            request, context, *args, **kwargs)
        source_type_choices = [
            ('', _("Select source")),
            ("docker", _("Boot from docker image")),
            ("instance_snapshot_id", _("Boot from snapshot")),
        ]
        for config in TYPE_CHOICE_BACKEND['choices']:
            if config['region'] == request.user.services_region:
                self.fields['sys_type'].choices = config['sys_type']
                self.fields['architecture'].choices = config['architecture']
                self.fields['accelerator_type'].choices = config['accelerator_type']
                self.fields['use_accelerator'].choices = config['use_accelerator_choice']

        kvm_resource = 0
        try:
            resource = ResourcePoint.objects.get(name="kvm", region=self.request.user.services_region)
            kvm_resource = resource.count
        except Exception, ex:
            LOG.error("%s %s", Exception, ex)

        if not self.request.user.is_superuser:
            del self.fields['availability_zone']
            for config in OPENSTACK_CONFIG_BACKEND['configs']:
                if config['region'] == request.user.services_region:
                    if kvm_resource and 'users_use_kvm' in config and request.user.username in config['users_use_kvm']:
                        source_type_choices.append(("kvm", _("Boot from kvm image")))
        else:
            self.fields['architecture'].choices.append(("x86_64", "X86 64"))
            if kvm_resource:
                source_type_choices.append(("kvm", _("Boot from kvm image")))
        if self.request.user.services_region == "HangZhou":
            self.fields['use_accelerator'].widget = forms.HiddenInput()
            # del self.fields['use_accelerator']
        self.fields['source_type'].choices = source_type_choices

    def is_valid(self):
        is_valid = super(SetInstanceDetailsAction, self).is_valid()
        if not is_valid:
            for field in self.errors.keys():
                LOG.debug("ValidationError: %s[%s] <- \" %s",
                          type(self),
                          field,
                          # self.data[field],
                          self.errors[field].as_text()
                          )
        return is_valid

    def clean(self):
        cleaned_data = super(SetInstanceDetailsAction, self).clean()

        count = cleaned_data.get('count', 1)
        # Prevent launching more instances than the quota allows
        usages = quotas.tenant_quota_usages(self.request)
        available_count = usages['instances']['available']
        if available_count < count:
            error_message = ungettext_lazy('The requested instance '
                                           'cannot be launched as you only '
                                           'have %(avail)i of your quota '
                                           'available. ',
                                           'The requested %(req)i instances '
                                           'cannot be launched as you only '
                                           'have %(avail)i of your quota '
                                           'available.',
                                           count)
            params = {'req': count,
                      'avail': available_count}
            raise forms.ValidationError(error_message % params)
        try:
            flavor_id = cleaned_data.get('flavor')
            # We want to retrieve details for a given flavor,
            # however flavor_list uses a memoized decorator
            # so it is used instead of flavor_get to reduce the number
            # of API calls.
            flavors = instance_utils.flavor_list(self.request)
            flavor = [x for x in flavors if x.id == flavor_id][0]
        except IndexError:
            flavor = None

        count_error = []
        # Validate cores and ram.
        available_cores = usages['cores']['available']
        if flavor and available_cores < count * flavor.vcpus:
            count_error.append(_("Cores(Available: %(avail)s, "
                                 "Requested: %(req)s)")
                    % {'avail': available_cores,
                       'req': count * flavor.vcpus})

        available_ram = usages['ram']['available']
        if flavor and available_ram < count * flavor.ram:
            count_error.append(_("RAM(Available: %(avail)s, "
                                 "Requested: %(req)s)")
                    % {'avail': available_ram,
                       'req': count * flavor.ram})

        if count_error:
            value_str = ", ".join(count_error)
            msg = (_('The requested instance cannot be launched. '
                     'The following requested resource(s) exceed '
                     'quota(s): %s.') % value_str)
            if count == 1:
                self._errors['flavor'] = self.error_class([msg])
            else:
                self._errors['count'] = self.error_class([msg])

        # Validate our instance source.
        source_type = self.data.get('source_type', None)

        if source_type in ('kvm', 'docker', 'volume_image_id'):
            if source_type == 'volume_image_id':
                volume_size = self.data.get('volume_size', None)
                if not volume_size:
                    msg = _("You must set volume size")
                    self._errors['volume_size'] = self.error_class([msg])
                if float(volume_size) <= 0:
                    msg = _("Volume size must be greater than 0")
                    self._errors['volume_size'] = self.error_class([msg])
                if not cleaned_data.get('device_name'):
                    msg = _("You must set device name")
                    self._errors['device_name'] = self.error_class([msg])
            if not cleaned_data.get('image_id'):
                msg = _("You must select an image.")
                self._errors['image_id'] = self.error_class([msg])
            else:
                # Prevents trying to launch an image needing more resources.
                try:
                    image_id = cleaned_data.get('image_id')
                    # We want to retrieve details for a given image,
                    # however get_available_images uses a cache of image list,
                    # so it is used instead of image_get to reduce the number
                    # of API calls.
                    images = image_utils.get_available_images(
                        self.request,
                        self.context.get('project_id'),
                        self._images_cache)
                    image = [x for x in images if x.id == image_id][0]
                except IndexError:
                    image = None

                if image and flavor:
                    props_mapping = (("min_ram", "ram"), ("min_disk", "disk"))
                    for iprop, fprop in props_mapping:
                        if getattr(image, iprop) > 0 and \
                                getattr(image, iprop) > getattr(flavor, fprop):
                            msg = (_("The flavor '%(flavor)s' is too small "
                                     "for requested image.\n"
                                     "Minimum requirements: "
                                     "%(min_ram)s MB of RAM and "
                                     "%(min_disk)s GB of Root Disk.") %
                                   {'flavor': flavor.name,
                                    'min_ram': image.min_ram,
                                    'min_disk': image.min_disk})
                            self._errors['image_id'] = self.error_class([msg])
                            break  # Not necessary to continue the tests.

                    volume_size = cleaned_data.get('volume_size')
                    if volume_size and source_type == 'volume_image_id':
                        volume_size = int(volume_size)
                        img_gigs = functions.bytes_to_gigabytes(image.size)
                        smallest_size = max(img_gigs, image.min_disk)
                        if volume_size < smallest_size:
                            msg = (_("The Volume size is too small for the"
                                     " '%(image_name)s' image and has to be"
                                     " greater than or equal to "
                                     "'%(smallest_size)d' GB.") %
                                   {'image_name': image.name,
                                    'smallest_size': smallest_size})
                            self._errors['volume_size'] = self.error_class(
                                [msg])

        elif source_type == 'instance_snapshot_id':
            if not cleaned_data['instance_snapshot_id']:
                msg = _("You must select a snapshot.")
                self._errors['instance_snapshot_id'] = self.error_class([msg])

        elif source_type == 'volume_id':
            if not cleaned_data.get('volume_id'):
                msg = _("You must select a volume.")
                self._errors['volume_id'] = self.error_class([msg])
            # Prevent launching multiple instances with the same volume.
            # TODO(gabriel): is it safe to launch multiple instances with
            # a snapshot since it should be cloned to new volumes?
            if count > 1:
                msg = _('Launching multiple instances is only supported for '
                        'images and instance snapshots.')
                raise forms.ValidationError(msg)

        elif source_type == 'volume_snapshot_id':
            if not cleaned_data.get('volume_snapshot_id'):
                msg = _("You must select a snapshot.")
                self._errors['volume_snapshot_id'] = self.error_class([msg])
            if not cleaned_data.get('device_name'):
                msg = _("You must set device name")
                self._errors['device_name'] = self.error_class([msg])

        return cleaned_data

    def populate_flavor_choices(self, request, context):
        flavors = instance_utils.flavor_list(request)
        if flavors:
            return instance_utils.sort_flavor_list(request, flavors)
        return []

    def populate_availability_zone_choices(self, request, context):
        try:
            zones = api.nova.availability_zone_list(request)
        except Exception:
            zones = []
            exceptions.handle(request,
                              _('Unable to retrieve availability zones.'))

        zone_list = [(zone.zoneName, zone.zoneName)
                      for zone in zones if zone.zoneState['available']]
        zone_list.sort()
        if not zone_list:
            zone_list.insert(0, ("", _("No availability zones found")))
        elif len(zone_list) > 1:
            zone_list.insert(0, ("", _("Any Availability Zone")))
        return zone_list

    def get_help_text(self, extra_context=None):
        extra = extra_context or {}
        max_total_instances = 2
        total_instances_used = 0
        use_system_quota = False
        users_use_system_quota = OPENSTACK_CONFIG_BACKEND.get('users_use_system_quota', [])
        if self.request.user.username in users_use_system_quota:
            use_system_quota = True

        if not use_system_quota:
            for region in self.request.user.available_services_regions:
                try:
                    usages = api.nova.tenant_absolute_limits(self.request, region=region)
                    total_instances_used += usages.totalInstancesUsed
                except Exception:
                    pass
        extra['max_total_instances'] = max_total_instances
        extra['total_instances_used'] = total_instances_used
        extra['use_system_quota'] = use_system_quota
        try:
            extra['usages'] = api.nova.tenant_absolute_limits(self.request)
            extra['usages_json'] = json.dumps(extra['usages'])
            flavors = json.dumps([f._info for f in
                                  instance_utils.flavor_list(self.request)])
            extra['flavors'] = flavors
            images = image_utils.get_available_images(self.request,
                                                      self.initial['project_id'],
                                                      self._images_cache)
            if images is not None:
                attrs = [{'id': i.id,
                          'min_disk': getattr(i, 'min_disk', 0),
                          'min_ram': getattr(i, 'min_ram', 0)}
                         for i in images]
                extra['images'] = json.dumps(attrs)

        except Exception:
            exceptions.handle(self.request,
                              _("Unable to retrieve quota information."))
        return super(SetInstanceDetailsAction, self).get_help_text(extra)

    def _init_images_cache(self):
        if not hasattr(self, '_images_cache'):
            self._images_cache = {}

    def _init_accelerators_cache(self):
        if not hasattr(self, '_accelerators_cache'):
            self._accelerators_cache = {}

    def _get_volume_display_name(self, volume):
        if hasattr(volume, "volume_id"):
            vol_type = "snap"
            visible_label = _("Snapshot")
        else:
            vol_type = "vol"
            visible_label = _("Volume")
        return (("%s:%s" % (volume.id, vol_type)),
                (_("%(name)s - %(size)s GB (%(label)s)") %
                 {'name': volume.name,
                  'size': volume.size,
                  'label': visible_label}))

    def populate_image_id_choices(self, request, context):
        choices = []
        filters = {
            "property-image_type": "image"
        }
        images = image_utils.get_available_images_by_filter(request,
                                                            context.get('project_id'),
                                                            None,
                                                            filters)
        for image in images:
            image.bytes = image.size
            image.volume_size = max(
                image.min_disk, functions.bytes_to_gigabytes(image.bytes))
            choices.append((image.id, image))
            if context.get('image_id') == image.id and \
                    'volume_size' not in context:
                context['volume_size'] = image.volume_size
        if choices:
            choices.sort(key=lambda c: c[1].name)
            choices.insert(0, ("", _("Select Image")))
        else:
            choices.insert(0, ("", _("No images available")))
        return choices

    def populate_capi_choices(self, request, context):
        filters = {
            'is_public': True,
            'properties': {
                'image_type': 'accelerator',
                'acc_type': 'capi',
            }
        }
        (images, more, prev) = api.glance.image_list_detailed(request, filters=filters)
        choices = [({"name": image.properties.get("acc_name", image.name),
                     "id": image.id},
                    image.properties.get("acc_name", image.name)) for image in images]
        if not len(choices):
            choices = [("", _("No available accelerator"))]
        return choices

    def populate_accelerator_choices(self, request, context):
        filters = {
            'is_public': True,
            'properties': {
                'image_type': 'accelerator',
                'acc_type': 'pcie',
            }
        }
        (images, more, prev) = api.glance.image_list_detailed(request, filters=filters)
        choices = [({"name": image.properties.get("acc_name", image.name),
                     "id": image.id},
                    image.properties.get("acc_name", image.name)) for image in images]
        return choices

    def populate_instance_snapshot_id_choices(self, request, context):
        can_use_kvm = False
        for config in OPENSTACK_CONFIG_BACKEND['configs']:
            if config['region'] == request.user.services_region:
                if 'users_use_kvm' in config and request.user.username in config['users_use_kvm']:
                    can_use_kvm = True
        filters = {
            "property-image_type": "snapshot"
        }
        if not can_use_kvm:
            filters["property-hypervisor_type"] = "docker"
        images = image_utils.get_available_images_by_filter(request,
                                                            None,
                                                            self._images_cache,
                                                            filters=filters)
        resource = {"kvm": 0, "docker": 0, "lxc": 0}
        for key, value in resource.items():
            try:
                resource_obj = ResourcePoint.objects.get(name=key, region=request.user.services_region)
                resource[key] = resource_obj.count
            except Exception, ex:
                LOG.error("%s %s", Exception, ex)
        choices = [(image.id, image.name)
                   for image in images if resource[image.properties.get("hypervisor_type", "")]]
        if choices:
            choices.sort(key=operator.itemgetter(1))
            choices.insert(0, ("", _("Select Instance Snapshot")))
        else:
            choices.insert(0, ("", _("No snapshots available")))
        return choices

    def populate_volume_id_choices(self, request, context):
        volumes = []
        try:
            if base.is_service_enabled(request, 'volume'):
                volumes = [self._get_volume_display_name(v)
                           for v in cinder.volume_list(self.request)
                           if (v.status == api.cinder.VOLUME_STATE_AVAILABLE
                               and v.bootable == 'true')]
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve list of volumes.'))
        if volumes:
            volumes.insert(0, ("", _("Select Volume")))
        else:
            volumes.insert(0, ("", _("No volumes available")))
        return volumes

    def populate_volume_snapshot_id_choices(self, request, context):
        snapshots = []
        try:
            if base.is_service_enabled(request, 'volume'):
                snaps = cinder.volume_snapshot_list(self.request)
                snapshots = [self._get_volume_display_name(s) for s in snaps
                             if s.status == api.cinder.VOLUME_STATE_AVAILABLE]
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve list of volume '
                                'snapshots.'))
        if snapshots:
            snapshots.insert(0, ("", _("Select Volume Snapshot")))
        else:
            snapshots.insert(0, ("", _("No volume snapshots available")))
        return snapshots


class SetInstanceDetails(workflows.Step):
    action_class = SetInstanceDetailsAction
    depends_on = ("project_id", "user_id")
    contributes = ("source_type", "source_id",
                   "availability_zone", "name", "count", "flavor", "capi",
                   "use_accelerator", "accelerator_type", "accelerator",
                   "sys_type", "architecture",
                   "device_name",  # Can be None for an image.
                   "delete_on_terminate")

    def prepare_action_context(self, request, context):
        if 'source_type' in context and 'source_id' in context:
            context[context['source_type']] = context['source_id']
        return context

    def contribute(self, data, context):
        context = super(SetInstanceDetails, self).contribute(data, context)
        # Allow setting the source dynamically.
        if ("source_type" in context and "source_id" in context
                and context["source_type"] not in context):
            context[context["source_type"]] = context["source_id"]

        # Translate form input to context for source values.
        if "source_type" in data:
            if data["source_type"] in ["kvm", "docker"]:
                context["source_id"] = data.get("image_id", None)
            else:
                context["source_id"] = data.get(data["source_type"], None)

        if "volume_size" in data:
            context["volume_size"] = data["volume_size"]

        return context


KEYPAIR_IMPORT_URL = "horizon:project:access_and_security:keypairs:import"


class SetAccessControlsAction(workflows.Action):
    keypair = forms.DynamicChoiceField(label=_("Key Pair"),
                                       required=False,
                                       help_text=_("Key pair to use for "
                                                   "authentication."),
                                       add_item_link=KEYPAIR_IMPORT_URL)
    admin_pass = forms.RegexField(
        label=_("Admin Pass"),
        required=False,
        widget=forms.PasswordInput(render_value=False),
        regex=validators.password_validator(),
        error_messages={'invalid': validators.password_validator_msg()})
    confirm_admin_pass = forms.CharField(
        label=_("Confirm Admin Pass"),
        required=False,
        widget=forms.PasswordInput(render_value=False))
    groups = forms.MultipleChoiceField(label=_("Security Groups"),
                                       initial=["default"],
                                       widget=forms.CheckboxSelectMultiple(),
                                       help_text=_("Launch instance in these "
                                                   "security groups."))

    class Meta:
        name = _("Access & Security")
        help_text = _("Control access to your instance via key pairs, "
                      "security groups, and other mechanisms.")

    def __init__(self, request, *args, **kwargs):
        super(SetAccessControlsAction, self).__init__(request, *args, **kwargs)
        if not api.nova.can_set_server_password():
            del self.fields['admin_pass']
            del self.fields['confirm_admin_pass']

    def populate_keypair_choices(self, request, context):
        try:
            keypairs = api.nova.keypair_list(request)
            keypair_list = [(kp.name, kp.name) for kp in keypairs]
        except Exception:
            keypair_list = []
            exceptions.handle(request,
                              _('Unable to retrieve key pairs.'))
        if keypair_list:
            if len(keypair_list) == 1:
                self.fields['keypair'].initial = keypair_list[0][0]
            keypair_list.insert(0, ("", _("Select a key pair")))
        else:
            keypair_list = (("", _("No key pairs available")),)
        return keypair_list

    def populate_groups_choices(self, request, context):
        try:
            groups = api.network.security_group_list(request)
            security_group_list = [(sg.name, sg.name) for sg in groups]
        except Exception:
            exceptions.handle(request,
                              _('Unable to retrieve list of security groups'))
            security_group_list = []
        return security_group_list

    def clean(self):
        '''Check to make sure password fields match.'''
        cleaned_data = super(SetAccessControlsAction, self).clean()
        if 'admin_pass' in cleaned_data:
            if cleaned_data['admin_pass'] != cleaned_data.get(
                    'confirm_admin_pass', None):
                raise forms.ValidationError(_('Passwords do not match.'))
        return cleaned_data


class SetAccessControls(workflows.Step):
    action_class = SetAccessControlsAction
    depends_on = ("project_id", "user_id")
    contributes = ("keypair_id", "security_group_ids",
            "admin_pass", "confirm_admin_pass")

    def contribute(self, data, context):
        if data:
            post = self.workflow.request.POST
            context['security_group_ids'] = post.getlist("groups")
            context['keypair_id'] = data.get("keypair", "")
            context['admin_pass'] = data.get("admin_pass", "")
            context['confirm_admin_pass'] = data.get("confirm_admin_pass", "")
        return context


class CustomizeAction(workflows.Action):
    class Meta:
        name = _("Post-Creation")
        help_text_template = ("project/instances/"
                              "_launch_customize_help.html")

    source_choices = [('', _('Select Script Source')),
                      ('raw', _('Direct Input')),
                      ('file', _('File'))]

    attributes = {'class': 'switchable', 'data-slug': 'scriptsource'}
    script_source = forms.ChoiceField(label=_('Customization Script Source'),
                                      choices=source_choices,
                                      widget=forms.Select(attrs=attributes),
                                      required=False)

    script_help = _("A script or set of commands to be executed after the "
                    "instance has been built (max 16kb).")

    script_upload = forms.FileField(
        label=_('Script File'),
        help_text=script_help,
        widget=forms.FileInput(attrs={
            'class': 'switched',
            'data-switch-on': 'scriptsource',
            'data-scriptsource-file': _('Script File')}),
        required=False)

    script_data = forms.CharField(
        label=_('Script Data'),
        help_text=script_help,
        widget=forms.widgets.Textarea(attrs={
            'class': 'switched',
            'data-switch-on': 'scriptsource',
            'data-scriptsource-raw': _('Script Data')}),
        required=False)

    def __init__(self, *args):
        super(CustomizeAction, self).__init__(*args)

    def clean(self):
        cleaned = super(CustomizeAction, self).clean()

        files = self.request.FILES
        script = self.clean_uploaded_files('script', files)

        if script is not None:
            cleaned['script_data'] = script

        return cleaned

    def clean_uploaded_files(self, prefix, files):
        upload_str = prefix + "_upload"

        has_upload = upload_str in files
        if has_upload:
            upload_file = files[upload_str]
            log_script_name = upload_file.name
            LOG.info('got upload %s' % log_script_name)

            if upload_file._size > 16 * 1024:  # 16kb
                msg = _('File exceeds maximum size (16kb)')
                raise forms.ValidationError(msg)
            else:
                script = upload_file.read()
                if script != "":
                    try:
                        normalize_newlines(script)
                    except Exception as e:
                        msg = _('There was a problem parsing the'
                                ' %(prefix)s: %(error)s')
                        msg = msg % {'prefix': prefix, 'error': e}
                        raise forms.ValidationError(msg)
                return script
        else:
            return None


class PostCreationStep(workflows.Step):
    action_class = CustomizeAction
    contributes = ("script_data",)


class SetNetworkAction(workflows.Action):
    network = forms.MultipleChoiceField(label=_("Networks"),
                                        widget=forms.CheckboxSelectMultiple(),
                                        error_messages={
                                            'required': _(
                                                "At least one network must"
                                                " be specified.")},
                                        help_text=_("Launch instance with"
                                                    " these networks"))
    if api.neutron.is_port_profiles_supported():
        widget = None
    else:
        widget = forms.HiddenInput()
    profile = forms.ChoiceField(label=_("Policy Profiles"),
                                required=False,
                                widget=widget,
                                help_text=_("Launch instance with "
                                            "this policy profile"))

    def __init__(self, request, *args, **kwargs):
        super(SetNetworkAction, self).__init__(request, *args, **kwargs)
        network_list = self.fields["network"].choices
        if len(network_list) == 1:
            self.fields['network'].initial = [network_list[0][0]]
        if api.neutron.is_port_profiles_supported():
            self.fields['profile'].choices = (
                self.get_policy_profile_choices(request))

    class Meta:
        name = _("Networking")
        permissions = ('openstack.services.network',)
        help_text = _("Select networks for your instance.")

    def populate_network_choices(self, request, context):
        network_list = []
        try:
            tenant_id = self.request.user.tenant_id
            networks = api.neutron.network_list_for_tenant(request, tenant_id)
            for n in networks:
                n.set_id_as_name_if_empty()
                network_list.append((n.id, n.name))
            sorted(network_list, key=lambda obj: obj[1])
        except Exception:
            exceptions.handle(request,
                              _('Unable to retrieve networks.'))
        return network_list

    def get_policy_profile_choices(self, request):
        profile_choices = [('', _("Select a profile"))]
        for profile in self._get_profiles(request, 'policy'):
            profile_choices.append((profile.id, profile.name))
        return profile_choices

    def _get_profiles(self, request, type_p):
        profiles = []
        try:
            profiles = api.neutron.profile_list(request, type_p)
        except Exception:
            msg = _('Network Profiles could not be retrieved.')
            exceptions.handle(request, msg)
        return profiles


class SetNetwork(workflows.Step):
    action_class = SetNetworkAction
    # Disabling the template drag/drop only in the case port profiles
    # are used till the issue with the drag/drop affecting the
    # profile_id detection is fixed.
    if api.neutron.is_port_profiles_supported():
        contributes = ("network_id", "profile_id",)
    else:
        template_name = "project/instances/_update_networks.html"
        contributes = ("network_id",)

    def contribute(self, data, context):
        if data:
            networks = self.workflow.request.POST.getlist("network")
            # If no networks are explicitly specified, network list
            # contains an empty string, so remove it.
            networks = [n for n in networks if n != '']
            if networks:
                context['network_id'] = networks

            if api.neutron.is_port_profiles_supported():
                context['profile_id'] = data.get('profile', None)
        return context


class SetAdvancedAction(workflows.Action):
    disk_config = forms.ChoiceField(label=_("Disk Partition"), required=False,
                                    help_text=_("Automatic: The entire disk is a single partition and "
                                                "automatically resizes. Manual: Results in faster build "
                                                "times but requires manual partitioning."))
    config_drive = forms.BooleanField(label=_("Configuration Drive"),
                                      required=False, help_text=_("Configure OpenStack to write metadata to "
                                                                  "a special configuration drive that "
                                                                  "attaches to the instance when it boots."))

    def __init__(self, request, context, *args, **kwargs):
        super(SetAdvancedAction, self).__init__(request, context,
                                                *args, **kwargs)
        try:
            if not api.nova.extension_supported("DiskConfig", request):
                del self.fields['disk_config']
            else:
                # Set our disk_config choices
                config_choices = [("AUTO", _("Automatic")),
                                  ("MANUAL", _("Manual"))]
                self.fields['disk_config'].choices = config_choices
            # Only show the Config Drive option for the Launch Instance
            # workflow (not Resize Instance) and only if the extension
            # is supported.
            if context.get('workflow_slug') != 'launch_instance' or (
                    not api.nova.extension_supported("ConfigDrive", request)):
                del self.fields['config_drive']
        except Exception:
            exceptions.handle(request, _('Unable to retrieve extensions '
                                         'information.'))

    class Meta:
        name = _("Advanced Options")
        help_text_template = ("project/instances/"
                              "_launch_advanced_help.html")


class SetAdvanced(workflows.Step):
    action_class = SetAdvancedAction
    contributes = ("disk_config", "config_drive",)

    def prepare_action_context(self, request, context):
        context = super(SetAdvanced, self).prepare_action_context(request,
                                                                  context)
        # Add the workflow slug to the context so that we can tell which
        # workflow is being used when creating the action. This step is
        # used by both the Launch Instance and Resize Instance workflows.
        context['workflow_slug'] = self.workflow.slug
        return context


def random_name(prefix='i', randomlength=9):
    post_fix = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()

    for i in range(randomlength):
        post_fix += chars[random.randint(0, length)]

    return prefix + '-' + post_fix


class LaunchInstance(workflows.Workflow):
    slug = "launch_instance"
    name = _("Launch Instance")
    finalize_button_name = _("Launch")
    success_message = _('Created %(count)s named "%(name)s". '
                        'Please check account and password for this virtual machine in %(email)s.')
    failure_message = _('Unable to launch %(count)s named "%(name)s".')
    success_url = "horizon:project:instances:index"
    multipart = True
    default_steps = (SelectProjectUser,
                     SetInstanceDetails)

    def __init__(self, request, *args, **kwargs):
        super(LaunchInstance, self).__init__(request, *args, **kwargs)
        self.avail_zone = 'nova'
        name = self.request.user.username.split('@')[0]
        self.instance_name = random_name(prefix=name)
        self.nics = []
        self.private_ip = ''
        self.floating_ip = None
        self.port = None
        self.vpn_username = None
        self.vpn_password = None
        if get_language() == 'en':
            self.vpn_email_template = 'project/instances/vpn_email_en.html'
            self.instance_email_template = 'project/instances/email_instance_info_en.html'
        elif get_language() == 'zh-cn':
            self.vpn_email_template = 'project/instances/vpn_email.html'
            self.instance_email_template = 'project/instances/email_instance_info.html'

    def create_network(self):
        internal_ip_id = ''
        external_ip_id = ''
        management_ip_id = ''
        for config in OPENSTACK_CONFIG_BACKEND['configs']:
            if config['region'] == self.request.user.services_region:
                internal_ip_id = config['internal_ip_id']
                external_ip_id = config['external_ip_id']
                management_ip_id = config['management_ip_id']

        self.port = api.neutron.port_create(self.request, internal_ip_id)
        for ips in self.port.fixed_ips:
            self.private_ip = ips['ip_address']
        if self.request.user.is_superuser and management_ip_id != '':
            self.nics = [{"port-id": self.port.id}, {"net-id": management_ip_id}]
        else:
            self.nics = [{"port-id": self.port.id}]

        self.floating_ip = api.network.tenant_floating_ip_allocate(self.request, external_ip_id)

    def set_avail_zone(self, request, context):
        use_accelerator = context.get('use_accelerator', '')
        accelerator_type = context.get('accelerator_type', '')
        if request.user.is_superuser:
            self.avail_zone = context.get('availability_zone', None)
        else:
            if use_accelerator == 'fpga':
                self.avail_zone = ''
                # for config in OPENSTACK_CONFIG_BACKEND['configs']:
                #     if config['region'] == request.user.services_region:
                #         avail_zone_dict = config.get('accelerator_zone', {})
                #         self.avail_zone = avail_zone_dict.get(accelerator_type, 'nova')
            elif use_accelerator == 'gpu':
                for config in OPENSTACK_CONFIG_BACKEND['configs']:
                    if config['region'] == request.user.services_region:
                        self.avail_zone = config.get('gpu_zone', '')

    def format_status_message(self, message):
        name = self.instance_name
        return message % {"count": _("instance"), "name": name, "email": self.request.user.username}

    def pre_auth_user(self, context, accelerator_list):
        flavor_id = context['flavor']
        need_points = 10
        check_result = True
        if self.request.user.is_superuser:
            return 0, check_result

        try:
            point_rate = PointRate.objects.get(flavor_id=flavor_id, service_type='Cloud')
            need_points = point_rate.points
        except Exception, ex:
            LOG.error('%s %s', Exception, ex)

        check_result, err_code = preauth(self.request.user.username, need_points)
        for accelerator in accelerator_list:
                if 'points' in accelerator:
                    need_points += int(accelerator['points'])

        return need_points, check_result

    def recount_vm(self, source_type):
        if source_type not in ['kvm', 'docker', 'container']:
            return True

        try:
            resource = ResourcePoint.objects.get(name=source_type, region=self.request.user.services_region)
            if resource.count < 1:
                messages.error(self.request, _("There is not enough resource to be use"))
                return False

            count = resource.count - 1
            resource.count = count
            resource.save()

            return True
        except Exception, ex:
            LOG.error("%s %s", Exception, ex)
            return False

    def set_vpn_for_bj(self):
        success = False
        try:
            VpnAccount.objects.get(user_id=self.request.user.id, region=self.request.user.services_region)
            success = True
        except Exception:
            try:
                vpn = VpnAccount.objects.filter(user_id="")
                vpn_used = vpn[0]
                self.vpn_username = vpn_used.name
                self.vpn_password = vpn_used.password
                # TODO(hightall): need atomic operation;
                vpn_used.user_id = self.request.user.id
                vpn_used.save()
                success = True
            except Exception, ex:
                LOG.error("%s %s", Exception, ex)
                success = False

        return success

    def set_vpn_for_hz(self):
        success = False
        try:
            VpnAccount.objects.get(user_id=self.request.user.id, region=self.request.user.services_region)
            success = True
        except Exception:
            out_file = "/usr/share/openstack-dashboard/static/vpn/%s/%s.ovpn" % (
                self.request.user.services_region, self.request.user.username)
            vpn_cmd = "/usr/share/easy-rsa/key-gen.sh -m %s -f %s" % (self.request.user.username, out_file)
            status = os.system(vpn_cmd)
            if not status:
                success = True
                vpn = VpnAccount()
                vpn.user_id = self.request.user.id
                vpn.region = self.request.user.services_region
                vpn.name = "%s.ovpn" % self.request.user.username
                vpn.link = "/static/vpn/%s/%s.ovpn" % (self.request.user.services_region, self.request.user.username)
                vpn.save()
            else:
                success = False

        return success

    def set_vpn_account(self):
        success = False
        try:
            VpnAccount.objects.get(user_id=self.request.user.id, region=self.request.user.services_region)
            success = True
        except Exception:
            if self.request.user.services_region == "Beijing":
                success = self.set_vpn_for_bj()
            elif self.request.user.services_region == "HangZhou":
                success = self.set_vpn_for_hz()

        if not success:
            messages.warning(self.request, _("""There is not enough vpn account,
                                     we will email the vpn account to you after we get"""))

    def send_email(self):
        if self.vpn_username and self.vpn_password:
            topic = {'vpn_account': self.vpn_username, 'vpn_password': self.vpn_password}
            subject = 'VPN Account for OpenPOWER(This is autoSend email, Please do not reply!)'
            html_content = loader.render_to_string(
                self.vpn_email_template,
                {
                    'topic': topic
                }
            )
            user_list = [self.request.user.username]
            if not self.request.user.is_superuser:
                send_mail_task.delay(subject, html_content, jsonpickle.encode(user_list))
            messages.success(self.request, _("VPN account has been sent to your email! Please check it!"))

        topic = {
            'region': self.request.user.services_region,
            'instance_name': self.instance_name,
            'fixed_ip': self.private_ip,
            'floating_ip': self.floating_ip.ip
        }
        subject = _('Instance %s (This is autoSend email, Please do not reply!)') % self.instance_name
        vpns = []
        for region in self.request.user.available_services_regions:
            vpn = {"region": region}
            try:
                vpn_tmp = VpnAccount.objects.get(user_id=self.request.user.id, region=region)
                if vpn_tmp.password != "":
                    vpn['title'] = _("VPN Account name: %s") % vpn_tmp.name
                    vpn['body'] = _("Password is %s") % vpn_tmp.password
                else:
                    vpn['title'] = _("VPN Configure file "
                                     "<a href='http://218.75.77.116%s' target='_blank' "
                                     "class='link-u' style='color:#40bfc4; "
                                     "text-decoration:underline'>"
                                     "<span class='link-u' style='color:#40bfc4; text-decoration:underline'>"
                                     "%s</span></a> (Click to download)") % (vpn_tmp.link,
                                                                             vpn_tmp.name)
                    vpn['body'] = ""
            except Exception:
                vpn['title'] = "No VPN Account"
            vpns.append(vpn)

        html_content = loader.render_to_string(
            self.instance_email_template,
            {
                'topic': topic,
                'vpns': vpns,
            }
        )
        user_list = [self.request.user.username]
        if not self.request.user.is_superuser:
            send_mail_task.delay(subject, html_content, jsonpickle.encode(user_list))

    def get_accelerators(self, context):
        use_accelerator = context.get('use_accelerator', '')
        accelerator_type = context.get('accelerator_type', '')
        accelerator_list = []
        accelerator_bw = 1000

        if use_accelerator != 'fpga':
            return accelerator_list

        if accelerator_type == "capi":
            accelerator_ids = context.get('capi', None)
            acc_tmp = accelerator_ids.replace("u'", "'").replace("'", '"')
            accelerator = json.loads(acc_tmp)
            image = api.glance.image_get(self.request, accelerator.get("id", ""))
            fpga_board = getattr(image, "properties", {}).get("fpga_board", "")
            accelerator['bw'] = ("%d" % accelerator_bw)
            accelerator.update({'fpga_board': fpga_board})
            LOG.debug('HIGHTALL %s', accelerator)
            accelerator_list.append(accelerator)
        elif accelerator_type == "pcie":
            accelerator_ids = context.get('accelerator', None)
            for acc in accelerator_ids:
                acc_tmp = acc.replace("u'", "'").replace("'", '"')
                accelerator = json.loads(acc_tmp)
                image = api.glance.image_get(self.request, accelerator.get("id", ""))
                fpga_board = getattr(image, "properties", {}).get("fpga_board", "")
                accelerator['bw'] = ("%d" % accelerator_bw)
                accelerator.update({'fpga_board': fpga_board})
                LOG.debug('HIGHTALL %s', accelerator)
                accelerator_list.append(accelerator)

        return accelerator_list

    def release_resource(self):
        # TODO(hightall): release network resource when fail
        pass

    @sensitive_variables('context')
    def handle(self, request, context):
        custom_script = context.get('script_data', '')
        accelerator_type = context.get('accelerator_type', '')

        dev_mapping_1 = None
        dev_mapping_2 = None

        image_id = ''

        accelerator_list = self.get_accelerators(context)

        need_points, check_result = self.pre_auth_user(context, accelerator_list)
        if not check_result:
            messages.warning(request, _("You Do not have enough points"))
            return False

        sys_type = context.get('sys_type', '')
        use_accelerator = context.get('use_accelerator', '')
        if use_accelerator != '':
            use_accelerator = True
        else:
            use_accelerator = False
        architecture = context.get('architecture', '')
        # Determine volume mapping options
        source_type = context.get('source_type', None)
        if source_type in ['kvm', 'docker', 'container', 'instance_snapshot_id']:
            image_id = context['source_id']

        if source_type == 'instance_snapshot_id':
            image = api.glance.image_get(self.request, image_id)
            source_type = getattr(image, "properties", {}).get("hypervisor_type", "")
            place_holder = getattr(image, "properties", {}).get("place_holder", "")
            if place_holder == "market":
                try:
                    market_image = MarketImageInfo.objects.get(image_id=image_id)
                    downloads = market_image.downloads + 1
                    market_image.downloads = downloads
                    market_image.save()
                except Exception:
                    pass

        check_vm_result = self.recount_vm(source_type)
        if not check_vm_result:
            return False

        self.set_avail_zone(request, context)

        self.create_network()

        try:
            instance = api.nova.server_create(request,
                                              self.instance_name,
                                              image_id,
                                              context['flavor'],
                                              '',
                                              normalize_newlines(custom_script),
                                              [u'default'],
                                              block_device_mapping=dev_mapping_1,
                                              block_device_mapping_v2=dev_mapping_2,
                                              nics=self.nics,
                                              availability_zone=self.avail_zone,
                                              instance_count=1,
                                              meta={"SPN": "Cloud"},
                                              admin_pass='',
                                              disk_config='AUTO',
                                              accelerator=accelerator_list)
            portid = "%(port-id)s_%(ip_addr)s" % {'port-id': self.port.id, 'ip_addr': self.private_ip}
            api.network.floating_ip_associate(self.request,
                                              self.floating_ip.id,
                                              portid)

            if not self.request.user.is_superuser:
                transaction_user_points.delay(self.request.user.username, "supernova@admin.grp", need_points)

            self.set_vpn_account()
            self.send_email()
            dt = {
                "image_id": image_id,
                "flavor_id": context['flavor'],
                "instance_id": instance.id,
                "image_name": instance.image_name,
                "os_type": instance.image_os_type,
                "floating_ip": self.floating_ip.ip,
                "private_ip": self.private_ip,
                "virtual_type": source_type,
                "sys_type": sys_type,
                "architecture": architecture,
                "use_accelerator": use_accelerator,
                "accelerator_type": accelerator_type,
            }
            add_operation.delay(jsonpickle.encode(request), jsonpickle.encode(dt))

            return True
        except Exception:
            exceptions.handle(request)
            return False
