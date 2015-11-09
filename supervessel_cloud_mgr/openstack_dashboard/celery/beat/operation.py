import logging

from celery.schedules import crontab
from celery.task import periodic_task
from django.db.models import Count
from django.template import loader
from django.utils.datetime_safe import date
from django.utils.timezone import now, timedelta, localtime
from django.utils.dateparse import parse_datetime
from datetime import datetime
import jsonpickle
import pytz
from openstack_dashboard.celery.task.user_operation import send_mail_task

from openstack_dashboard.models import OperationHistory, LAUNCH_INSTANCE, LOGIN, ACTIVE, DELETED

LOG = logging.getLogger(__name__)
REGIONS = [
    {"name": "Beijing"},
    {"name": "Hangzhou"}]

REPORT_LIST = [
    'shaol@cn.ibm.com',
    'linyh@cn.ibm.com',
    'bjhtyue@cn.ibm.com',
    'sunkewei@cn.ibm.com',
    'bjzhuc@cn.ibm.com',
    'hangliu@cn.ibm.com',
    'gongyan@cn.ibm.com',
    'linzhbj@cn.ibm.com',
]


@periodic_task(name='check_user_operation',
               run_every=crontab(hour="0", minute="0", day_of_week="*"),
               bind=True,
               default_retry_delay=5, max_retries=10)
def check_user_operation(self):
    email_template = 'report_email.html'
    topic = {}
    subject = 'SuperVessel Daily report'
    try:
        today = datetime.now(tz=pytz.utc)
        s2 = today - timedelta(days=2)
        s1 = today - timedelta(days=1)
        launch_s2 = len(OperationHistory.objects.filter(launch_time__range=(s2, s1)))
        launch_s1 = len(OperationHistory.objects.filter(launch_time__range=(s1, today)))
        number = float(abs(launch_s1 - launch_s2))
        rate = "%.0f%%" % (100 * number/launch_s2)
        topic['global_launch'] = launch_s1
        topic['rate'] = rate
        if launch_s1 > launch_s2:
            topic['rate_type'] = 'upgrade'
        else:
            topic['rate_type'] = 'downgrade'

        for region in REGIONS:
            launch_s2 = len(OperationHistory.objects.filter(launch_time__range=(s2, s1), region=region.get("name", "")))
            launch_s1 = len(OperationHistory.objects.filter(launch_time__range=(s1, today), region=region.get("name", "")))
            tmp = {"launch_count": launch_s1}
            number = float(abs(launch_s1 - launch_s2))
            if launch_s2:
                tmp['rate'] = "%.0f%%" % (100 * number/launch_s2)
            if launch_s1 > launch_s2:
                tmp['rate_name'] = "upgrade"
            else:
                tmp['rate_name'] = "downgrade"
            launch_images = OperationHistory.objects.filter(launch_time__range=(s1, today),
                                                            region=region.get("name", "")).\
                values('image_name').annotate(num_images=Count('image_name')).order_by('-num_images')
            tmp['launch_images'] = launch_images
            region.update(tmp)
        topic['regions'] = REGIONS
    except Exception, exc:
        LOG.debug('HIGHTALL %s %s', Exception, exc)
        pass

    html_content = loader.render_to_string(
        email_template,
        {
            'topic': topic
        }
    )
    send_mail_task(subject, html_content, jsonpickle.encode(REPORT_LIST))
