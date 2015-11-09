import logging
from openstack_dashboard.api.nova import Hypervisor
from openstack_dashboard.utils.base_api.nova import get_nova_client

import json

LOG = logging.getLogger(__name__)


def get_capi_count(region="Beijing", fpga_board=""):
    min_time = 9999999999999
    nc = get_nova_client(region_name=region)
    hypervisors = nc.hypervisors.list()
    fpga_list = []
    for hypervisor in hypervisors:
        hyper = Hypervisor(hypervisor)
        hyper_info = hyper._apidict._info
        extra_resources = hyper_info.get("extra_resources", None)
        if extra_resources:
            resource_dict = json.loads(extra_resources)
            fpga_capi = resource_dict.get("fpga_capi", None)
            if fpga_capi:
                fpga_list.append(fpga_capi)

    for fpga_capi in fpga_list:
        for k, v in fpga_capi.items():
            LOG.debug('HIGHTALL %s %s', v, fpga_board)
            if v[0] != fpga_board:
                continue
            remain_times = v[1]
            if remain_times == 0:
                return True, 0
            elif remain_times < min_time:
                min_time = remain_times

    return False, min_time
