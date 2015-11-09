# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import copy

import json
import logging
from random import Random
from time import strftime, gmtime
from django.utils import timezone
from django.conf import settings
from django.core.urlresolvers import reverse

from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_variables  # noqa

import six
import yaml

from horizon import exceptions
from horizon import forms
from horizon import messages

from openstack_dashboard import api
from openstack_dashboard.openstack.common import strutils
from openstack_dashboard.dashboards.project.stacks.stack_template import *

LOG = logging.getLogger(__name__)

OPENSTACK_CONFIG_BACKEND = getattr(settings, 'OPENSTACK_CONFIG_BACKEND', {})
STACK_BACKEND = getattr(settings, 'STACK_BACKEND', {})


def create_upload_form_attributes(prefix, input_type, name):
    """Creates attribute dicts for the switchable upload form

    :type prefix: str
    :param prefix: prefix (environment, template) of field
    :type input_type: str
    :param input_type: field type (file, raw, url)
    :type name: str
    :param name: translated text label to display to user
    :rtype: dict
    :return: an attribute set to pass to form build
    """
    attributes = {'class': 'switched', 'data-switch-on': prefix + 'source'}
    attributes['data-' + prefix + 'source-' + input_type] = name
    return attributes


class TemplateForm(forms.SelfHandlingForm):

    class Meta:
        name = _('Select Template')
        help_text = _('Select a template to launch a stack.')

    # TODO(jomara) - update URL choice for template & environment files
    # w/ client side download when applicable
    base_choices = [('file', _('File')),
               ('raw', _('Direct Input'))]
    url_choice = [('url', _('URL'))]
    attributes = {'class': 'switchable', 'data-slug': 'templatesource'}
    template_source = forms.ChoiceField(label=_('Template Source'),
                                        choices=base_choices + url_choice,
                                        widget=forms.Select(attrs=attributes))

    attributes = create_upload_form_attributes(
        'template',
        'file',
        _('Template File'))
    template_upload = forms.FileField(
        label=_('Template File'),
        help_text=_('A local template to upload.'),
        widget=forms.FileInput(attrs=attributes),
        required=False)

    attributes = create_upload_form_attributes(
        'template',
        'url',
        _('Template URL'))
    template_url = forms.URLField(
        label=_('Template URL'),
        help_text=_('An external (HTTP) URL to load the template from.'),
        widget=forms.TextInput(attrs=attributes),
        required=False)

    attributes = create_upload_form_attributes(
        'template',
        'raw',
        _('Template Data'))
    template_data = forms.CharField(
        label=_('Template Data'),
        help_text=_('The raw contents of the template.'),
        widget=forms.widgets.Textarea(attrs=attributes),
        required=False)

    attributes = {'data-slug': 'envsource', 'class': 'switchable'}
    environment_source = forms.ChoiceField(
        label=_('Environment Source'),
        choices=base_choices,
        widget=forms.Select(attrs=attributes),
        required=False)

    attributes = create_upload_form_attributes(
        'env',
        'file',
        _('Environment File'))
    environment_upload = forms.FileField(
        label=_('Environment File'),
        help_text=_('A local environment to upload.'),
        widget=forms.FileInput(attrs=attributes),
        required=False)

    attributes = create_upload_form_attributes(
        'env',
        'raw',
        _('Environment Data'))
    environment_data = forms.CharField(
        label=_('Environment Data'),
        help_text=_('The raw contents of the environment file.'),
        widget=forms.widgets.Textarea(attrs=attributes),
        required=False)

    def __init__(self, *args, **kwargs):
        self.next_view = kwargs.pop('next_view')
        super(TemplateForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned = super(TemplateForm, self).clean()

        files = self.request.FILES
        self.clean_uploaded_files('template', _('template'), cleaned, files)
        self.clean_uploaded_files('environment',
            _('environment'),
            cleaned,
            files)

        # Validate the template and get back the params.
        kwargs = {}
        if cleaned['template_data']:
            kwargs['template'] = cleaned['template_data']
        else:
            kwargs['template_url'] = cleaned['template_url']

        if cleaned['environment_data']:
            kwargs['environment'] = cleaned['environment_data']

        try:
            validated = api.heat.template_validate(self.request, **kwargs)
            cleaned['template_validate'] = validated
        except Exception as e:
            raise forms.ValidationError(unicode(e))

        return cleaned

    def clean_uploaded_files(self, prefix, field_label, cleaned, files):
        """Cleans Template & Environment data from form upload.

        Does some of the crunchy bits for processing uploads vs raw
        data depending on what the user specified. Identical process
        for environment data & template data.

        :type prefix: str
        :param prefix: prefix (environment, template) of field
        :type field_label: str
        :param field_label: translated prefix str for messages
        :type input_type: dict
        :param prefix: existing cleaned fields from form
        :rtype: dict
        :return: cleaned dict including environment & template data
        """

        upload_str = prefix + "_upload"
        data_str = prefix + "_data"
        url = cleaned.get(prefix + '_url')
        data = cleaned.get(prefix + '_data')

        has_upload = upload_str in files
        # Uploaded file handler
        if has_upload and not url:
            log_template_name = files[upload_str].name
            LOG.info('got upload %s' % log_template_name)

            tpl = files[upload_str].read()
            if tpl.startswith('{'):
                try:
                    json.loads(tpl)
                except Exception as e:
                    msg = _('There was a problem parsing the'
                            ' %(prefix)s: %(error)s')
                    msg = msg % {'prefix': prefix, 'error': e}
                    raise forms.ValidationError(msg)
            cleaned[data_str] = tpl

        # URL handler
        elif url and (has_upload or data):
            msg = _('Please specify a %s using only one source method.')
            msg = msg % field_label
            raise forms.ValidationError(msg)

        elif prefix == 'template':
            # Check for raw template input - blank environment allowed
            if not url and not data:
                msg = _('You must specify a template via one of the '
                        'available sources.')
                raise forms.ValidationError(msg)

    def create_kwargs(self, data):
        kwargs = {'parameters': data['template_validate'],
                  'environment_data': data['environment_data'],
                  'template_data': data['template_data'],
                  'template_url': data['template_url']}
        if data.get('stack_id'):
            kwargs['stack_id'] = data['stack_id']
        return kwargs

    def handle(self, request, data):
        kwargs = self.create_kwargs(data)
        # NOTE (gabriel): This is a bit of a hack, essentially rewriting this
        # request so that we can chain it as an input to the next view...
        # but hey, it totally works.
        request.method = 'GET'

        return self.next_view.as_view()(request, **kwargs)


class ChangeTemplateForm(TemplateForm):
    class Meta:
        name = _('Edit Template')
        help_text = _('Select a new template to re-launch a stack.')
    stack_id = forms.CharField(label=_('Stack ID'),
        widget=forms.widgets.HiddenInput)
    stack_name = forms.CharField(label=_('Stack Name'),
        widget=forms.TextInput(attrs={'readonly': 'readonly'}))


class CreateStackForm(forms.SelfHandlingForm):

    param_prefix = '__param_'

    class Meta:
        name = _('Create Stack')

    template_data = forms.CharField(
        widget=forms.widgets.HiddenInput,
        required=False)
    template_url = forms.CharField(
        widget=forms.widgets.HiddenInput,
        required=False)
    environment_data = forms.CharField(
        widget=forms.widgets.HiddenInput,
        required=False)
    parameters = forms.CharField(
        widget=forms.widgets.HiddenInput)
    stack_name = forms.RegexField(
        max_length=255,
        label=_('Stack Name'),
        help_text=_('Name of the stack to create.'),
        regex=r"^[a-zA-Z][a-zA-Z0-9_.-]*$",
        error_messages={'invalid': _('Name must start with a letter and may '
                            'only contain letters, numbers, underscores, '
                            'periods and hyphens.')})
    timeout_mins = forms.IntegerField(
        initial=60,
        label=_('Creation Timeout (minutes)'),
        help_text=_('Stack creation timeout in minutes.'))
    enable_rollback = forms.BooleanField(
        label=_('Rollback On Failure'),
        help_text=_('Enable rollback on create/update failure.'),
        required=False)

    def __init__(self, *args, **kwargs):
        parameters = kwargs.pop('parameters')
        # special case: load template data from API, not passed in params
        if(kwargs.get('validate_me')):
            parameters = kwargs.pop('validate_me')
        super(CreateStackForm, self).__init__(*args, **kwargs)
        self._build_parameter_fields(parameters)

    def _build_parameter_fields(self, template_validate):
        self.fields['password'] = forms.CharField(
            label=_('Password for user "%s"') % self.request.user.username,
            help_text=_('This is required for operations to be performed '
                        'throughout the lifecycle of the stack'),
            widget=forms.PasswordInput())

        self.help_text = template_validate['Description']

        params = template_validate.get('Parameters', {})

        for param_key, param in params.items():
            field_key = self.param_prefix + param_key
            field_args = {
                'initial': param.get('Default', None),
                'label': param.get('Label', param_key),
                'help_text': param.get('Description', ''),
                'required': param.get('Default', None) is None
            }

            param_type = param.get('Type', None)
            hidden = strutils.bool_from_string(param.get('NoEcho', 'false'))

            if 'AllowedValues' in param:
                choices = map(lambda x: (x, x), param['AllowedValues'])
                field_args['choices'] = choices
                field = forms.ChoiceField(**field_args)

            elif param_type in ('CommaDelimitedList', 'String'):
                if 'MinLength' in param:
                    field_args['min_length'] = int(param['MinLength'])
                    field_args['required'] = param.get('MinLength', 0) > 0
                if 'MaxLength' in param:
                    field_args['max_length'] = int(param['MaxLength'])
                if hidden:
                    field_args['widget'] = forms.PasswordInput()
                field = forms.CharField(**field_args)

            elif param_type == 'Number':
                if 'MinValue' in param:
                    field_args['min_value'] = int(param['MinValue'])
                if 'MaxValue' in param:
                    field_args['max_value'] = int(param['MaxValue'])
                field = forms.IntegerField(**field_args)

            self.fields[field_key] = field

    @sensitive_variables('password')
    def handle(self, request, data):
        prefix_length = len(self.param_prefix)
        params_list = [(k[prefix_length:], v) for (k, v) in six.iteritems(data)
                       if k.startswith(self.param_prefix)]
        fields = {
            'stack_name': data.get('stack_name'),
            'timeout_mins': data.get('timeout_mins'),
            'disable_rollback': not(data.get('enable_rollback')),
            'parameters': dict(params_list),
            'password': data.get('password')
        }

        if data.get('template_data'):
            fields['template'] = data.get('template_data')
        else:
            fields['template_url'] = data.get('template_url')

        if data.get('environment_data'):
            fields['environment'] = data.get('environment_data')

        try:
            api.heat.stack_create(self.request, **fields)
            messages.success(request, _("Stack creation started."))
            return True
        except Exception:
            exceptions.handle(request)


class EditStackForm(CreateStackForm):

    class Meta:
        name = _('Update Stack Parameters')

    stack_id = forms.CharField(label=_('Stack ID'),
        widget=forms.widgets.HiddenInput)
    stack_name = forms.CharField(label=_('Stack Name'),
        widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    @sensitive_variables('password')
    def handle(self, request, data):
        prefix_length = len(self.param_prefix)
        params_list = [(k[prefix_length:], v) for (k, v) in six.iteritems(data)
                       if k.startswith(self.param_prefix)]

        stack_id = data.get('stack_id')
        fields = {
            'stack_name': data.get('stack_name'),
            'timeout_mins': data.get('timeout_mins'),
            'disable_rollback': not(data.get('enable_rollback')),
            'parameters': dict(params_list),
            'password': data.get('password')
        }

        # if the user went directly to this form, resubmit the existing
        # template data. otherwise, submit what they had from the first form
        if data.get('template_data'):
            fields['template'] = data.get('template_data')
        elif data.get('template_url'):
            fields['template_url'] = data.get('template_url')
        elif data.get('parameters'):
            fields['template'] = data.get('parameters')

        try:
            api.heat.stack_update(self.request, stack_id=stack_id, **fields)
            messages.success(request, _("Stack update started."))
            return True
        except Exception:
            exceptions.handle(request)


def random_name(prefix='i', randomlength=9):
    post_fix = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()

    for i in range(randomlength):
        post_fix += chars[random.randint(0, length)]

    return prefix + '_' + post_fix


class LaunchStacksForm(forms.SelfHandlingForm):
    service_type = forms.ChoiceField(label=_("Select Service type for BigData"),
                                     choices=STACK_BACKEND['service_type'],
                                     widget=forms.RadioSelect,
                                     required=True)

    node_count = forms.ChoiceField(label=_("Select count of node"),
                                   choices=STACK_BACKEND['node_count'],
                                   widget=forms.RadioSelect,
                                   required=True)

    disk_size = forms.ChoiceField(label=_("Select disk size"),
                                  choices=STACK_BACKEND['disk_size'],
                                  widget=forms.RadioSelect,
                                  required=True)

    def __init__(self, *args, **kwargs):
        super(LaunchStacksForm, self).__init__(*args, **kwargs)
        self.market_image = None

    @staticmethod
    def generate_spark_slave_node(cur_node=1, the_end=False):
        slave_hns = []
        ip_settings = []
        echo_ips = []
        scp_cmds = []
        ssh_cmds = []
        params = BASE_USER_DATA_PARAMS
        slave_node = BASE_NODE_TEMPLATE
        ip_settings.append(IP_SETTING.format(node=cur_node))
        ssh_cmds.append(SSH_CMD.format(node=cur_node))
        slave_host_ip = '$slave%d_host_ip' % cur_node
        slave_port = 'slave_port_%d' % cur_node
        slave_param = {
            slave_host_ip: {
                'get_attr': [slave_port, 'fixed_ips', 0, 'ip_address']
            }
        }
        params.update(slave_param)
        slave_name = "slave%d" % cur_node
        if the_end:
            slave_node_script = MULTI_NODE_END_SLAVE_SCRIPT_TEMPLATE
            echo_ips.append(ECHO_IP.format(node=cur_node, slave_name=slave_name))
            enter = '\\n'
            slave_node_script = slave_node_script.format(slave_hn=enter.join(slave_hns),
                                                         ip_setting=enter.join(ip_settings),
                                                         echo_ip=enter.join(echo_ips),
                                                         scp_cmd=enter.join(scp_cmds),
                                                         ssh_cmd=enter.join(ssh_cmds))
        else:
            slave_node_script = MULTI_NODE_SLAVE_SCRIPT_TEMPLATE
            echo_ips.append(ECHO_IP.format(node=cur_node, slave_name=''))
            scp_cmds.append(SCP_CMD.format(node=cur_node))
            slave_hns.append(SLAVE_HN.format(slave_name=slave_name))

        slave_user_data = {
            'user_data': {
                'str_replace': {
                    'template': slave_node_script,
                    'params': params,
                }
            }
        }
        networks = {'networks': [{'port': {'get_resource': slave_port}}]}
        slave_node['properties'].update(slave_user_data)
        slave_node['properties'].update(networks)

        return slave_node

    def generate_spark_template(self, node_count=1):
        template = BASE_TEMPLATE
        parameters = BASE_PARAMETERS_TEMPLATE
        resources = BASE_RESOURCES_TEMPLATE
        master_node = BASE_NODE_TEMPLATE
        outputs = BASE_OUTPUTS_TEMPLATE
        if node_count > 1:
            master_node_script = MULTI_NODE_MASTER_SCRIPT_TEMPLATE
        else:
            master_node_script = SINGLE_NODE_MASTER_SCRIPT_TEMPLATE
        master_user_data = {
            'user_data': {
                'str_replace': {
                    'template': master_node_script,
                    'params': BASE_USER_DATA_PARAMS,
                }
            }
        }
        networks = {'networks': [{'port': {'get_resource': 'server_port_1'}}]}
        master_node['properties'].update(master_user_data)
        master_node['properties'].update(networks)
        spark_master_dict = copy.deepcopy({'sparkMaster': master_node})
        resources.update(spark_master_dict)
        last_slave_depends_on = ['private_subnet', 'sparkMaster']
        for i in range(1, node_count):
            slave_node = self.generate_spark_slave_node(i, i == (node_count-1))
            slave_name = 'sparkSlave%d' % i
            slave_port_name = 'slave_port_%d' % i
            slave_internal_ip = 'slave_node%d_internal_ip' % i
            if i != (node_count-1):
                last_slave_depends_on.append(slave_name)
            else:
                slave_node.update({'depends_on': last_slave_depends_on})
            slave_node_dict = copy.deepcopy({slave_name: slave_node})
            slave_port_dict = copy.deepcopy({slave_port_name: BASE_SLAVE_PORT_TEMPLATE})
            resources.update(slave_node_dict)
            resources.update(slave_port_dict)
            slave_output = {
                slave_internal_ip: {
                    'value': {
                        'get_attr': [slave_name, 'networks', {'get_attr': ['private_net', 'name']}, 0]}
                }
            }
            outputs.update(slave_output)
        template.update({'parameters': parameters})
        template.update({'resources': resources})
        template.update({'outputs': outputs})

        return template

    def generate_template(self, service_type, node_count):
        if service_type == "spark":
            return self.generate_spark_template(node_count)
        if service_type == "map_reduce":
            if node_count > 1:
                return self.generate_map_reduce_multi_template(node_count)
            else:
                return self.generate_map_reduce_single_template()

    def create_cinder(self, disk_size, stack_name):
        volume_name = "%s_volume" % stack_name
        try:
            volume = api.cinder.volume_create(self.request,
                                              disk_size,
                                              volume_name,
                                              '',
                                              '',
                                              availability_zone='nova')
        except Exception, ex:
            LOG.error('%s %s', Exception, ex)
            raise Exception

        return volume

    def handle(self, request, data):
        service_type = data.get('service_type', '')
        node_count = int(data.get('node_count', ''))
        disk_size = int(data.get('disk_size', ''))
        external_ip_id = ''
        cinder_id = ''

        prefix = 'stack_%s' % request.user.username.split('@')[0]
        stack_name = random_name(prefix)
        for config in OPENSTACK_CONFIG_BACKEND['configs']:
            if config['region'] == self.request.user.services_region:
                external_ip_id = config['external_ip_id']

        template = self.generate_template(service_type, node_count)
        private_net_name = "%s_net" % stack_name
        private_subnet_name = "%s_subnet" % stack_name
        router_name = "%s_router" % stack_name
        stack_type = "1m%ds-cluster" % (node_count-1)
        try:
            volume = self.create_cinder(disk_size, stack_name)
            cinder_id = volume.id
        except Exception, ex:
            LOG.error('%s %s', Exception, ex)
        fields = {
            'stack_name': stack_name,
            'timeout_mins': 60,
            'disable_rollback': True,
            'password': 'passw0rd',
            'template': template,
            "files": {},
            "parameters": {
                'public_net_id': external_ip_id,
                'private_net_name': private_net_name,
                'private_subnet_name': private_subnet_name,
                'private_net_cidr': '30.0.0.0/24',
                'private_net_gateway': '30.0.0.1',
                'router_name': router_name,
                'fixedip_master_node': '30.0.0.10',
                'image': 'Spark-1.0.2-RHEL-7.0-ppc64be-docker-bigdata-v0.6.2RC-shell',
                'flavor': 'docker.aufs.small',
                'mounts': 1,
                'mountpoint0': '/mnt',
                'filesystem0': 'ext4',
                'address0': '/sncfs/openstack/cinder/volumes/sncfs/volume-',
                'cinder_uuid': cinder_id,
                'privileged': 'false',
                'metadata': {
                    'SPN': 'BigData',
                    'TYPE': stack_type,
                    'ACCOUNT': 'banker@admin.grp'
                },
                'size': disk_size
            },
            "environment": {},
        }

        try:
            api.heat.stack_create(self.request, **fields)
            messages.success(request, _("Stack creation started."))
            return True
        except Exception:
            api.cinder.volume_delete(self.request, cinder_id)
            exceptions.handle(request)
