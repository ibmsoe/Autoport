from django.contrib.gis.geoip import GeoIP
import pytz
from openstack_dashboard.celery.base.email import send_html_email
from openstack_dashboard.models import MarketImageInfo, OperationHistory, DELETED, ACC_TYPE_NONE, PointRate, \
    ResourcePoint
from openstack_dashboard.utils import transfer_points
import jsonpickle
from openstack_dashboard.utils.user_api import get_client_ip
from datetime import datetime

__author__ = 'yuehaitao'
import logging
from celery import task

LOG = logging.getLogger(__name__)


@task(name='send-email-operation', bind=True, default_retry_delay=60, max_retries=12)
def send_mail_task(self, subject, content, user_json_list):
    user_list = jsonpickle.decode(user_json_list)
    try:
        send_html_email(subject, content, user_list)
    except Exception as exc:
        LOG.error("send mail %s", exc)
        raise self.retry(exc=exc)


@task(name='transaction_user_points', bind=True, default_retry_delay=10, max_retries=12)
def transaction_user_points(self, _from, _to, points):
    try:
        transfer_points(_from, _to, points)
    except Exception as exc:
        raise self.retry(exc=exc)


@task(name='update_custom_image_data', bind=True, default_retry_delay=10, max_retries=12)
def update_custom_image_data(self, image_id=""):
    try:
        market_image = MarketImageInfo.objects.get(final_image_id=image_id)
    except Exception:
        pass
    else:
        market_image.downloads += 1
        market_image.save()


@task(name='reward_user')
def reward_user(image_id=""):
    try:
        market_image = MarketImageInfo.objects.get(final_image_id=image_id)
    except Exception:
        pass
    else:
        creator = market_image.creator
        transaction_user_points("supernova@admin.grp", creator, 10)


@task(name='add_operation', bind=True, default_retry_delay=10, max_retries=12)
def add_operation(self, json_request=None, json_dt=None):
    request = jsonpickle.decode(json_request)
    dt = jsonpickle.decode(json_dt)
    if request.user.username == "admin":
        return
    operation = OperationHistory()
    operation.user_id = request.user.id
    operation.instance_id = dt.get("instance_id", "")
    operation.image_name = dt.get("image_name", "")
    operation.user_name = request.user.username
    operation.region = request.user.services_region
    operation.image_id = dt.get("image_id", "")
    operation.flavor_id = dt.get("flavor_id", "")
    operation.floating_ip = dt.get("floating_ip", "")
    operation.private_ip = dt.get("private_ip", "")
    operation.virtual_type = dt.get("virtual_type", "")
    operation.os_type = dt.get("os_type", "")
    operation.use_accelerator = dt.get("use_accelerator", False)
    operation.sys_type = dt.get("sys_type", "")
    operation.architecture = dt.get("architecture", "")
    operation.accelerator_type = dt.get("accelerator_type", "")
    operation.launch_time = datetime.now(tz=pytz.timezone('Asia/Shanghai'))
    g = GeoIP()
    country = ""
    city = ""
    ip = ""
    try:
        ip = get_client_ip(request)
        geoip = g.city(ip)
        country = geoip.get("country_name", "")
        city = geoip.get("city", "")
    except Exception:
        pass
    operation.country = country
    operation.city = city
    operation.ip = ip

    operation.save()


@task(name='update_operation', bind=True, default_retry_delay=10, max_retries=12)
def update_operation(self, json_request, instance_id="", status=DELETED):
    request = jsonpickle.decode(json_request)
    if request.user.username == "admin":
        return
    try:
        operation = OperationHistory.objects.get(instance_id=instance_id)
        operation.status = status
        if status == DELETED:
            operation.delete_time = datetime.now(tz=pytz.timezone('Asia/Shanghai'))
            operation.floating_ip = ""
            operation.private_ip = ""
        operation.save()
    except Exception, ex:
        LOG.error("%s %s", Exception, ex)
        pass


@task(name="recount_resource", bind=True, default_retry_delay=10, max_retries=12)
def recount_resource(self, instance_id="", region=""):
    virtual_type = "docker"
    instance = OperationHistory.objects.filter(instance_id=instance_id).first()
    if instance:
        virtual_type = instance.virtual_type
    try:
        vm_resource = ResourcePoint.objects.get(name=virtual_type, region=region)
        count = vm_resource.count + 1
        if count > vm_resource.max_value:
            count = vm_resource.max_value
        vm_resource.count = count
        vm_resource.save()
    except Exception as exc:
        pass
