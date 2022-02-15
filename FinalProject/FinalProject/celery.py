from __future__ import absolute_import, unicode_literals
import os

from celery import Celery
from celery.schedules import crontab
from celery.utils.log import get_task_logger
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FinalProject.settings')
app = Celery('FinalProject')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
logger = get_task_logger(__name__)
from kavenegar import *


# app.conf.broker_url = 'redis://localhost:6379/0'
# app.conf.broker_transport_options = {'visibility_timeout': 1}

@app.task
def send_otp(mobile, otp):
    body = {'receptor': mobile, 'token': otp, 'template': "verifyuser"}
    sms_res = requests.get(
        "https://api.kavenegar.com/v1/5145587872464647743632632B6438566C78456F7435786F4A47344F2F306C4C42595342656670393446453D/verify/lookup.json",
        params=body)
    logger.info("sms send")
