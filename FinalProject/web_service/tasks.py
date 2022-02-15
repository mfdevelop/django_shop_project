from __future__ import absolute_import, unicode_literals

from kavenegar import *
from celery import shared_task
from celery.utils.log import get_task_logger

Logger = get_task_logger(__name__)

