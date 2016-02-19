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
import logging
from django import template
from django.conf import settings

from django.core import urlresolvers
from django.http import Http404  # noqa
from django.template.defaultfilters import title  # noqa
from django.utils.http import urlencode  # noqa
from django.utils.translation import ugettext_lazy as _, string_concat
from django.utils.translation import ungettext_lazy

from horizon import messages
from horizon import tables
from horizon.utils import filters

from heatclient import exc

from openstack_dashboard import api
from openstack_dashboard.dashboards.project.stacks import mappings

LOG = logging.getLogger(__name__)
STACK_BACKEND = getattr(settings, 'STACK_BACKEND', {})
QUOTA = STACK_BACKEND.get('quota', 1)

class LaunchStack(tables.LinkAction):
    name = "launch"
    verbose_name = _("Launch Autoport Cluster")
    url = "horizon:project:stacks:launch"
    classes = ("ajax-modal",)
    #attrs = {'data-toggle': 'modal', 'data-target': '#modal_wrapper'}
    icon = "plus"
    policy_rules = (("orchestration", "cloudformation:CreateStack"),)

    def disable_btn(self):
        if "disabled" not in self.classes:
            self.classes = [c for c in self.classes] + ['disabled']
            self.verbose_name = string_concat(self.verbose_name, ' ',
                                              _("(Quota exceeded)"))
            self.url = "javascript:void(0);"

    def enable_btn(self):
        self.verbose_name = _("Launch Autoport Cluster")
        classes = [c for c in self.classes if c != "disabled"]
        self.classes = classes
        self.url = "horizon:project:stacks:launch"

    def allowed(self, request, datum):
        stacks = []
        try:
            stacks, _, _ = api.heat.stacks_list(request)
        except Exception:
            self.disable_btn()

        if len(stacks) >= QUOTA:
            self.disable_btn()
        else:
            self.enable_btn()

        return True


class ChangeStackTemplate(tables.LinkAction):
    name = "edit"
    verbose_name = _("Change Cluster Template")
    url = "horizon:project:stacks:change_template"
    classes = ("ajax-modal",)
    icon = "pencil"

    def get_link_url(self, stack):
        return urlresolvers.reverse(self.url, args=[stack.id])


class DeleteStack(tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Cluster",
            u"Delete Clusters",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Cluster",
            u"Deleted Clusters",
            count
        )

    policy_rules = (("orchestration", "cloudformation:DeleteStack"),)

    def delete(self, request, stack_id):
        try:
            stack = api.heat.stack_get(request, stack_id)
            volume_id = stack.parameters.get('cinder_uuid', None)
            if volume_id:
                try:
                    api.cinder.volume_delete(request, volume_id)
                except Exception:
                    pass
        except Exception:
            pass
        api.heat.stack_delete(request, stack_id)

    def allowed(self, request, stack):
        if stack is not None:
            return stack.stack_status != 'DELETE_COMPLETE'
        return True

class RebuildCluster(tables.LinkAction):
    name = "rebuild"
    verbose_name = _("Rebuild Cluster")
    url = "horizon:project:stacks:rebuild"
    classes = ("ajax-modal",)
    icon = "pencil"
    pass

class StacksUpdateRow(tables.Row):
    ajax = True

    def can_be_selected(self, datum):
        return datum.stack_status != 'DELETE_COMPLETE'

    def get_data(self, request, stack_id):
        try:
            return api.heat.stack_get(request, stack_id)
        except exc.HTTPNotFound:
            # returning 404 to the ajax call removes the
            # row from the table on the ui
            raise Http404
        except Exception as e:
            messages.error(request, e)


def get_stack_ips(stack):
    template_name = 'project/stacks/_stacks_ips.html'
    context = {"stack": stack}
    return template.loader.render_to_string(template_name, context)


class StacksTable(tables.DataTable):
    STATUS_CHOICES = (
        (None, True),
        ("Complete", True),
        ("Failed", False),
    )
    name = tables.Column("stack_name",
                         verbose_name=_("Cluster Name"),
                         link="horizon:project:stacks:detail",)
    created = tables.Column("creation_time",
                            verbose_name=_("Created"),
                            filters=(filters.parse_isotime,
                                     filters.timesince_or_never))
    updated = tables.Column("updated_time",
                            verbose_name=_("Updated"),
                            filters=(filters.parse_isotime,
                                     filters.timesince_or_never))
    status = tables.Column("status",
                           filters=(title, filters.replace_underscores),
                           verbose_name=_("Status"),
                           status=True,
                           status_choices=STATUS_CHOICES)

    ips = tables.Column(get_stack_ips,
                        verbose_name=_("IP Addresses"))

    def get_object_display(self, stack):
        return stack.stack_name

    class Meta:
        name = "stacks"
        verbose_name = _("Clusters")
        pagination_param = 'stack_marker'
        status_columns = ["status", ]
        row_class = StacksUpdateRow
        table_actions = (LaunchStack, DeleteStack,)
        row_actions = (RebuildCluster,DeleteStack,)
                       # ChangeStackTemplate)


def get_resource_url(obj):
    return urlresolvers.reverse('horizon:project:stacks:resource',
                                args=(obj.stack_id, obj.resource_name))


class EventsTable(tables.DataTable):

    logical_resource = tables.Column('resource_name',
                                     verbose_name=_("Cluster Resource"),
                                     link=get_resource_url)
    physical_resource = tables.Column('physical_resource_id',
                                      verbose_name=_("Resource"),
                                      link=mappings.resource_to_url)
    timestamp = tables.Column('event_time',
                              verbose_name=_("Time Since Event"),
                              filters=(filters.parse_isotime,
                                       filters.timesince_or_never))
    status = tables.Column("resource_status",
                           filters=(title, filters.replace_underscores),
                           verbose_name=_("Status"),)

    statusreason = tables.Column("resource_status_reason",
                                 verbose_name=_("Status Reason"),)

    class Meta:
        name = "events"
        verbose_name = _("Cluster Events")


class ResourcesUpdateRow(tables.Row):
    ajax = True

    def get_data(self, request, resource_name):
        try:
            stack = self.table.stack
            stack_identifier = '%s/%s' % (stack.stack_name, stack.id)
            return api.heat.resource_get(
                request, stack_identifier, resource_name)
        except exc.HTTPNotFound:
            # returning 404 to the ajax call removes the
            # row from the table on the ui
            raise Http404
        except Exception as e:
            messages.error(request, e)


class ResourcesTable(tables.DataTable):
    STATUS_CHOICES = (
        ("Create Complete", True),
        ("Create Failed", False),
    )

    logical_resource = tables.Column('resource_name',
                                     verbose_name=_("Cluster Resource"),
                                     link=get_resource_url)
    physical_resource = tables.Column('physical_resource_id',
                                      verbose_name=_("Resource"),
                                      link=mappings.resource_to_url)
    resource_type = tables.Column("resource_type",
                                  verbose_name=_("Cluster Resource Type"),)
    updated_time = tables.Column('updated_time',
                                 verbose_name=_("Date Updated"),
                                 filters=(filters.parse_isotime,
                                          filters.timesince_or_never))
    status = tables.Column("resource_status",
                           filters=(title, filters.replace_underscores),
                           verbose_name=_("Status"),
                           status=True,
                           status_choices=STATUS_CHOICES)

    statusreason = tables.Column("resource_status_reason",
                                 verbose_name=_("Status Reason"),)

    def __init__(self, request, data=None,
                 needs_form_wrapper=None, **kwargs):
        super(ResourcesTable, self).__init__(
            request, data, needs_form_wrapper, **kwargs)
        self.stack = kwargs['stack']

    def get_object_id(self, datum):
        return datum.resource_name

    class Meta:
        name = "resources"
        verbose_name = _("Cluster Resources")
        status_columns = ["status", ]
        row_class = ResourcesUpdateRow
