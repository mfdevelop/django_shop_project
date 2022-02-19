from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import CustomUserManager
from phonenumber_field.modelfields import PhoneNumberField


# from rest_framework_simplejwt.views import TokenObtainPairView

# Create your models here.


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField('email address', null=True, blank=True)
    phone_number = PhoneNumberField(null=False, blank=False, unique=True)
    has_shop = models.BooleanField(default=False)
    phone_number_verify = models.BooleanField(default=False)
    otp = models.CharField(max_length=10, null=True, blank=True)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        if self.email:
            return self.email
        return str(self.phone_number)

