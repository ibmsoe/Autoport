# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tables
from openstack_dashboard import api
from openstack_dashboard.usage import base
from django.conf import settings

OPENSTACK_CONFIG_BACKEND = getattr(settings, 'OPENSTACK_CONFIG_BACKEND', {})


class UsageView(tables.DataTableView):
    usage_class = None
    show_terminated = True
    csv_template_name = None

    def __init__(self, *args, **kwargs):
        super(UsageView, self).__init__(*args, **kwargs)
        if not issubclass(self.usage_class, base.BaseUsage):
            raise AttributeError("You must specify a usage_class attribute "
                                 "which is a subclass of BaseUsage.")

    def get_template_names(self):
        if self.request.GET.get('format', 'html') == 'csv':
            return (self.csv_template_name or
                    ".".join((self.template_name.rsplit('.', 1)[0], 'csv')))
        return self.template_name

    def get_content_type(self):
        if self.request.GET.get('format', 'html') == 'csv':
            return "text/csv"
        return "text/html"

    def get_data(self):
        try:
            project_id = self.kwargs.get('project_id',
                                         self.request.user.tenant_id)
            self.usage = self.usage_class(self.request, project_id)
            self.usage.summarize(*self.usage.get_date_range())
            self.usage.get_limits()
            self.kwargs['usage'] = self.usage
            return self.usage.usage_list
        except Exception:
            exceptions.handle(self.request,
                              _('There is something wrong in this region. '
                                'Please try other region. We will fix it soon.'))
            return []

    def get_context_data(self, **kwargs):
        context = super(UsageView, self).get_context_data(**kwargs)
        context['table'].kwargs['usage'] = self.usage
        context['form'] = self.usage.form
        context['usage'] = self.usage
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
                    total_instances_used += usages.get('totalInstancesUsed', 0)
                except Exception, ex:
                    pass
        context['max_total_instances'] = max_total_instances
        context['total_instances_used'] = total_instances_used
        context['use_system_quota'] = use_system_quota
        try:
            context['simple_tenant_usage_enabled'] = \
                api.nova.extension_supported('SimpleTenantUsage', self.request)
        except Exception:
            context['simple_tenant_usage_enabled'] = True
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get('format', 'html') == 'csv':
            render_class = self.csv_response_class
            response_kwargs.setdefault("filename", "usage.csv")
        else:
            render_class = self.response_class
        resp = render_class(request=self.request,
                            template=self.get_template_names(),
                            context=context,
                            content_type=self.get_content_type(),
                            **response_kwargs)
        return resp
