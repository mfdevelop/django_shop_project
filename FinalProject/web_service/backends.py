from django.contrib.auth.backends import ModelBackend
from rest_framework import status

from users.models import CustomUser
import redis
from rest_framework.response import Response
from .views import redis
from django.contrib.auth.models import User


class CustomUserBackendPhonePass(ModelBackend):
    def authenticate(self, request, phone_number=None, password=None, **kwargs):
        if phone_number in kwargs.keys() and password in kwargs.keys():
            phone_number = kwargs['phone_number']
            password = kwargs['password']
        try:
            custom_user = CustomUser.objects.get(phone_number=phone_number)
            if custom_user.password == password:
                return custom_user
        except CustomUser.DoesNotExist:
            return None


class CustomUserBackendPhoneOtp(ModelBackend):
    def authenticate(self, request, **kwargs):
        phone_number = kwargs['phone_number']
        otp = kwargs['otp']
        try:
            custom_user = CustomUser.objects.get(phone_number=phone_number)
            if custom_user:
                if redis.exists(phone_number):
                    if redis.get(phone_number) == otp:
                        custom_user.phone_number_verify = True
                        custom_user.save()
                        return Response({"message": "phone number verified successfully"})
                    return Response({"message": "otp code not matched"}, status.HTTP_400_BAD_REQUEST)
                return Response({"message": "otp code expired"}, status.HTTP_400_BAD_REQUEST)
            return Response({"message": "phone number not recognized"}, status.HTTP_401_UNAUTHORIZED)
        except CustomUser.DoesNotExist:
            return None
