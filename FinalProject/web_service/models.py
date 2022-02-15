from django.db import models

# Create your models here.
from users.models import CustomUser


class UserProfile(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to='uploads/', null=True, blank=True)
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    address = models.TextField()
    post_code = models.CharField(max_length=15)
    birth_day = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.first_name
