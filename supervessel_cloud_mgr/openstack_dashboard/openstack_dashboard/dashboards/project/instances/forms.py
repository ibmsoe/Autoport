# Copyright 2013 OpenStack Foundation
# All Rights Reserved.
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
import os
from random import Random
from django.conf import settings

from django.core.urlresolvers import reverse
from django.template import loader
from django.template.defaultfilters import filesizeformat  # noqa
from django.utils.translation import ugettext_lazy as _, get_language
from django.views.decorators.debug import sensitive_variables  # noqa
import jsonpickle

from horizon import exceptions
from horizon import forms
from horizon import messages
from horizon.utils import validators

from openstack_dashboard import api
from openstack_dashboard.dashboards.project.images import utils
from openstack_dashboard.dashboards.project.instances \
    import utils as instance_utils
from openstack_dashboard.models import PointRate, ResourcePoint, VpnAccount
from openstack_dashboard.utils import preauth
from openstack_dashboard.celery.task.user_operation import transaction_user_points, send_mail_task, \
    update_custom_image_data, reward_user, add_operation

LOG = logging.getLogger(__name__)
OPENSTACK_CONFIG_BACKEND = getattr(settings, 'OPENSTACK_CONFIG_BACKEND', {})


def _image_choice_title(img):
    gb = filesizeformat(img.size)
    return '%s (%s)' % (img.name or img.id, gb)


class RebuildInstanceForm(forms.SelfHandlingForm):
    instance_id = forms.CharField(widget=forms.HiddenInput())

    image = forms.ChoiceField(label=_("Select Image"),
            widget=forms.SelectWidget(attrs={'class': 'image-selector'},
                                       data_attrs=('size', 'display-name'),
                                       transform=_image_choice_title))
    password = forms.RegexField(label=_("Rebuild Password"),
            required=False,
            widget=forms.PasswordInput(render_value=False),
            regex=validators.password_validator(),
            error_messages={'invalid': validators.password_validator_msg()})
    confirm_password = forms.CharField(label=_("Confirm Rebuild Password"),
            required=False,
            widget=forms.PasswordInput(render_value=False))
    disk_config = forms.ChoiceField(label=_("Disk Partition"),
                                    required=False)

    def __init__(self, request, *args, **kwargs):
        super(RebuildInstanceForm, self).__init__(request, *args, **kwargs)
        instance_id = kwargs.get('initial', {}).get('instance_id')
        self.fields['instance_id'].initial = instance_id

        images = utils.get_available_images(request, request.user.tenant_id)
        choices = [(image.id, image) for image in images]
        if choices:
            choices.insert(0, ("", _("Select Image")))
        else:
            choices.insert(0, ("", _("No images available")))
        self.fields['image'].choices = choices

        if not api.nova.can_set_server_password():
            del self.fields['password']
            del self.fields['confirm_password']

        try:
            if not api.nova.extension_supported("DiskConfig", request):
                del self.fields['disk_config']
            else:
                # Set our disk_config choices
                config_choices = [("AUTO", _("Automatic")),
                                  ("MANUAL", _("Manual"))]
                self.fields['disk_config'].choices = config_choices
        except Exception:
            exceptions.handle(request, _('Unable to retrieve extensions '
                                         'information.'))

    def clean(self):
        cleaned_data = super(RebuildInstanceForm, self).clean()
        if 'password' in cleaned_data:
            passwd = cleaned_data.get('password')
            confirm = cleaned_data.get('confirm_password')
            if passwd is not None and confirm is not None:
                if passwd != confirm:
                    raise forms.ValidationError(_("Passwords do not match."))
        return cleaned_data

    # We have to protect the entire "data" dict because it contains the
    # password and confirm_password strings.
    @sensitive_variables('data', 'password')
    def handle(self, request, data):
        instance = data.get('instance_id')
        image = data.get('image')
        password = data.get('password') or None
        disk_config = data.get('disk_config', None)
        try:
            api.nova.server_rebuild(request, instance, image, password,
                                    disk_config)
            messages.success(request, _('Rebuilding instance %s.') % instance)
        except Exception:
            redirect = reverse('horizon:project:instances:index')
            exceptions.handle(request, _("Unable to rebuild instance."),
                              redirect=redirect)
        return True


class DecryptPasswordInstanceForm(forms.SelfHandlingForm):
    instance_id = forms.CharField(widget=forms.HiddenInput())
    _keypair_name_label = _("Key Pair Name")
    _keypair_name_help = _("The Key Pair name that "
                           "was associated with the instance")
    _attrs = {'readonly': 'readonly'}
    keypair_name = forms.CharField(widget=forms.widgets.TextInput(_attrs),
                                   label=_keypair_name_label,
                                   help_text=_keypair_name_help,
                                   required=False)
    _encrypted_pwd_help = _("The instance password encrypted "
                            "with your public key.")
    encrypted_password = forms.CharField(widget=forms.widgets.Textarea(_attrs),
                                         label=_("Encrypted Password"),
                                         help_text=_encrypted_pwd_help,
                                         required=False)

    def __init__(self, request, *args, **kwargs):
        super(DecryptPasswordInstanceForm, self).__init__(request,
                                                          *args,
                                                          **kwargs)
        instance_id = kwargs.get('initial', {}).get('instance_id')
        self.fields['instance_id'].initial = instance_id
        keypair_name = kwargs.get('initial', {}).get('keypair_name')
        self.fields['keypair_name'].initial = keypair_name
        try:
            result = api.nova.get_password(request, instance_id)
            if not result:
                _unavailable = _("Instance Password is not set"
                                 " or is not yet available")
                self.fields['encrypted_password'].initial = _unavailable
            else:
                self.fields['encrypted_password'].initial = result
                self.fields['private_key_file'] = forms.FileField(
                    label=_('Private Key File'),
                    widget=forms.FileInput())
                self.fields['private_key'] = forms.CharField(
                    widget=forms.widgets.Textarea(),
                    label=_("OR Copy/Paste your Private Key"))
                _attrs = {'readonly': 'readonly'}
                self.fields['decrypted_password'] = forms.CharField(
                    widget=forms.widgets.TextInput(_attrs),
                    label=_("Password"),
                    required=False)
        except Exception:
            redirect = reverse('horizon:project:instances:index')
            _error = _("Unable to retrieve instance password.")
            exceptions.handle(request, _error, redirect=redirect)

    def handle(self, request, data):
        return True


def random_name(prefix='i', randomlength=9):
    post_fix = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()

    for i in range(randomlength):
        post_fix += chars[random.randint(0, length)]

    return prefix + '-' + post_fix


class LaunchMarketImage(forms.SelfHandlingForm):
    image_id = forms.CharField(label=_("image"),
                               widget=forms.HiddenInput,
                               required=True)
    image_name = forms.CharField(label=_("Image Name"),
                                 required=False)
    flavor = forms.ChoiceField(label=_("Choose flavor"),
                               required=True)

    def __init__(self, *args, **kwargs):
        super(LaunchMarketImage, self).__init__(*args, **kwargs)
        self.avail_zone = 'nova'
        name = self.request.user.username.split('@')[0]
        self.instance_name = random_name(prefix=name)
        self.nics = []
        self.private_ip = ''
        self.floating_ip = None
        self.port = None
        self.vpn_username = None
        self.vpn_password = None
        self.success_message = _('Created %(count)s named "%(name)s". '
                                 'Please check account and password for this virtual machine in %(email)s.') % {
            "count": _("instance"), "name": self.instance_name, "email": self.request.user.username
        }
        if get_language() == 'en':
            self.vpn_email_template = 'project/instances/vpn_email_en.html'
            self.instance_email_template = 'project/instances/email_instance_info_en.html'
        elif get_language() == 'zh-cn':
            self.vpn_email_template = 'project/instances/vpn_email.html'
            self.instance_email_template = 'project/instances/email_instance_info.html'
        image_id = kwargs.get('initial', {}).get('image_id', "")
        hypervisor_type = 'docker'
        try:
            image = api.glance.image_get(self.request, image_id)
            hypervisor_type = image.properties.get('hypervisor_type', '')
        except Exception:
            pass
        flavors = instance_utils.flavor_list(self.request)
        if flavors:
            self.fields['flavor'].choices = \
                instance_utils.sort_match_flavor_list(self.request, flavors, hypervisor_type)
        self.fields['image_name'].widget.attrs['readonly'] = True

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

    def pre_auth_user(self, flavor_id):
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
        success = True
        try:
            VpnAccount.objects.get(user_id=self.request.user.id, region=self.request.user.services_region)
        except Exception:
            try:
                vpn = VpnAccount.objects.filter(user_id="")
                vpn_used = vpn[0]
                self.vpn_username = vpn_used.name
                self.vpn_password = vpn_used.password
                # TODO(hightall): need atomic operation;
                vpn_used.user_id = self.request.user.id
                vpn_used.save()
            except Exception, ex:
                LOG.error("%s %s", Exception, ex)
                success = False

        return success

    def set_vpn_for_hz(self):
        success = True
        try:
            VpnAccount.objects.get(user_id=self.request.user.id, region=self.request.user.services_region)
        except Exception:
            out_file = "/usr/share/openstack-dashboard/static/vpn/%s/%s.ovpn" % (
                self.request.user.services_region, self.request.user.username)
            vpn_cmd = "/usr/share/easy-rsa/key-gen.sh -m %s -f %s" % (self.request.user.username, out_file)
            status = os.system(vpn_cmd)
            if not status:
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

    def handle(self, request, data):
        image_id = data.get('image_id', '')
        flavor_id = data.get('flavor', '')
        source_type = 'docker'
        sys_type = ''
        architecture = ''
        LOG.debug('image_id %s flavor_id %s', image_id, flavor_id)

        need_points, check_result = self.pre_auth_user(flavor_id)
        if not check_result:
            messages.warning(request, _("You Do not have enough points"))
            return False
        try:
            image = api.glance.image_get(request, image_id)
            source_type = image.properties.get('hypervisor_type', '')
            sys_type = image.properties.get('sys_type', '')
            architecture = image.properties.get('architecture', '')
        except Exception:
            pass

        check_vm_result = self.recount_vm(source_type)
        if not check_vm_result:
            return False

        self.create_network()
        try:
            instance = api.nova.server_create(request,
                                              self.instance_name,
                                              image_id,
                                              flavor_id,
                                              '',
                                              '',
                                              [u'default'],
                                              block_device_mapping=None,
                                              block_device_mapping_v2=None,
                                              nics=self.nics,
                                              availability_zone=self.avail_zone,
                                              instance_count=1,
                                              meta={"SPN": "Cloud"},
                                              admin_pass='',
                                              disk_config='AUTO')
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
                "flavor_id": flavor_id,
                "instance_id": instance.id,
                "image_name": instance.image_name,
                "os_type": instance.image_os_type,
                "floating_ip": self.floating_ip.ip,
                "private_ip": self.private_ip,
                "virtual_type": source_type,
                "sys_type": sys_type,
                "architecture": architecture,
                "use_accelerator": False,
            }
            add_operation.delay(jsonpickle.encode(request), jsonpickle.encode(dt))
            update_custom_image_data.delay(image_id)
            reward_user.delay(image_id)

            LOG.debug('dt %s', dt)
            messages.success(self.request, self.success_message)

            return True
        except Exception:
            exceptions.handle(request)
            return False
