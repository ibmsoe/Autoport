import uuid

from datetime import datetime
from django.db import models
from django.utils import timezone
from django.utils.timezone import get_current_timezone, make_aware, utc
from picklefield.fields import PickledObjectField
from jsonfield import JSONField

LOGIN = 10
LAUNCH_INSTANCE = 20
DELETE_INSTANCE = 30

ACTIVE = 1
SUSPEND = 2
DELETED = 3

ACC_TYPE_NONE = 0
CAPI = 1
PCIE = 2


class ResourcePoint(models.Model):
    name = models.CharField(max_length=250)
    count = models.IntegerField(default=32)
    max_value = models.IntegerField(default=32)
    region = models.CharField(max_length=32)

    def __unicode__(self):
        return self.name


class VpnAccount(models.Model):
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    user_id = models.CharField(max_length=64)
    region = models.CharField(max_length=32)
    link = models.CharField(max_length=128)

    def __unicode__(self):
        return self.name


class PointRate(models.Model):
    flavor_id = models.CharField(max_length=255)
    service_type = models.CharField(max_length=255)
    virtual_type = models.CharField(max_length=255)
    memory = models.IntegerField(default=0)
    disk = models.IntegerField(default=0)
    ephemeral = models.IntegerField(default=0)
    swap = models.IntegerField(default=0)
    vcpus = models.IntegerField(default=0)
    rxtx_factor = models.IntegerField(default=0)
    points = models.IntegerField(default=1)

    def __unicode__(self):
        return self.pattern


def make_uuid():
    return str(uuid.uuid4())


class MarketImageInfo(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=make_uuid, editable=True)
    final_image_id = models.CharField(max_length=36)
    base_type = models.CharField(max_length=52)
    creator_id = models.CharField(max_length=36)
    creator = models.CharField(max_length=36)
    downloads = models.BigIntegerField(default=0)
    tags = PickledObjectField()
    extra_info = PickledObjectField()
    published = models.BooleanField(default=False)


class Notification(models.Model):
    user_id = models.CharField(max_length=36)
    # notify_time = models.DateTimeField(default=timezone.localtime(timezone.now()))
    notify_time = models.DateTimeField(auto_now_add=True)
    message = PickledObjectField()
    message_type = models.IntegerField()
    read_status = models.BooleanField(default=False)


class AcceleratorInfo(models.Model):
    image_id = models.CharField(max_length=36)
    image_info = JSONField()
    points = models.IntegerField(default=1)
    chip_vendor = models.CharField(max_length=125)
    chip_sn = models.CharField(max_length=125)


class WebShellUrl(models.Model):
    url = models.CharField(max_length=128)
    ip = models.CharField(max_length=32)
    region = models.CharField(max_length=32)


class City(models.Model):
    en_name = models.CharField(max_length=36)
    cn_name = models.CharField(max_length=128, unique=True)
    longitude = models.FloatField(default=0)
    latitude = models.FloatField(default=0)


def localize_datetime(dtime):
    """Makes DateTimeField value UTC-aware and returns datetime string localized
    in user's timezone in ISO format.
    """
    tz_aware = make_aware(dtime, utc).astimezone(get_current_timezone())
    return datetime.datetime.strftime(tz_aware, '%Y-%m-%d %H:%M:%S')


class OperationHistory(models.Model):
    instance_id = models.CharField(max_length=36, default="")
    os_type = models.CharField(max_length=36, default="")
    floating_ip = models.CharField(max_length=36, default="")
    private_ip = models.CharField(max_length=36, default="")
    user_id = models.CharField(max_length=36)
    user_name = models.CharField(max_length=128)
    launch_time = models.DateTimeField(default=timezone.now)
    delete_time = models.DateTimeField(default=timezone.now)
    flavor_id = models.CharField(max_length=36, default="")
    ip = models.CharField(max_length=36, default="")
    country = models.CharField(max_length=36, default="")
    city = models.CharField(max_length=36, default="")
    image_id = models.CharField(max_length=36, default="")
    image_name = models.CharField(max_length=128, default="")
    region = models.CharField(max_length=36, default="")
    organization = models.CharField(max_length=128, default="")
    status = models.IntegerField(default=ACTIVE)
    virtual_type = models.CharField(max_length=36, default="docker")
    use_accelerator = models.BooleanField(default=False)
    sys_type = models.CharField(max_length=36, default="")
    architecture = models.CharField(max_length=36, default="")
    accelerator_type = models.CharField(max_length=36, default="")

    @property
    def created_tz(self):
        return localize_datetime(self.operation_time)


class PointOperation(models.Model):
    region = models.CharField(max_length=36, default="")
    user_id = models.CharField(max_length=36)
    user_name = models.CharField(max_length=128)
    transfer_user = models.CharField(max_length=128)
    transfer_points = models.IntegerField(default=0)
    remain_points = models.IntegerField(default=0)
    time = models.DateTimeField(auto_now_add=True)


class SnapshotHistory(models.Model):
    region = models.CharField(max_length=36, default="")
    user_id = models.CharField(max_length=36)
    user_name = models.CharField(max_length=128)
    instance_name = models.CharField(max_length=128)
    snapshot_id = models.CharField(max_length=36)
    snapshot_name = models.CharField(max_length=128)
    time = models.DateTimeField(auto_now_add=True)
