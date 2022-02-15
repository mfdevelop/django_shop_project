from .models import *
from django.db import models


class AvailableShopsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(status='trash')



