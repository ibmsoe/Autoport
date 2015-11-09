import logging
from django.conf import settings
from openstack_dashboard import api
from openstack_dashboard.utils import get_user_points

OPENSTACK_CONFIG_BACKEND = getattr(settings, 'OPENSTACK_CONFIG_BACKEND', {})

CHECK_OK = 10
QUOTA_EXCEED = 20
NO_BLUE_POINTS = 30

LOG = logging.getLogger(__name__)


def check_instance_quota(request):
    # user_points = get_user_points(request.user.username)
    total_instances_used = 0
    max_total_instances = OPENSTACK_CONFIG_BACKEND.get('global_instance_quota', 2)
    users_use_system_quota = OPENSTACK_CONFIG_BACKEND.get('users_use_system_quota', [])
    if request.user.username in users_use_system_quota:
        try:
            limits = api.nova.tenant_absolute_limits(request, reserved=True)
            max_total_instances = limits['maxTotalInstances']
            total_instances_used = limits['totalInstancesUsed']
        except Exception:
            pass
    else:
        for region in request.user.available_services_regions:
            try:
                limits = api.nova.tenant_absolute_limits(request, reserved=True, region=region)
                total_instances_used += limits['totalInstancesUsed']
            except Exception:
                pass

    if request.user.is_superuser:
        return True, CHECK_OK

    # if user_points == 0:
    #     return False, NO_BLUE_POINTS

    if total_instances_used and total_instances_used >= max_total_instances:
        return False, QUOTA_EXCEED

    return True, CHECK_OK
