import json

from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from model_mommy import mommy
# from model_mommy import foreign_key

from shop_managing.models import Shop, Type
from .models import *
from PIL import Image
import io
from django.test.client import Client


# Create your tests here.

class TestWebServiceRegister(APITestCase):
    def setUp(self) -> None:
        self.register_url = reverse('web_service_register')
        self.success_data = {"email": "wsrt@gmail.com",
                             "phone_number": "+989384024575",
                             "password": "mfpass1381"}
        self.fail_data = {"email": "wsrt@gmail.com",
                          "phone_number": "+9893840245756",
                          "password": "mfpass1381"}

    def test_user_can_register(self):
        response = self.client.post(self.register_url, data=self.success_data)
        self.assertEqual(response.status_code, 201)

    def test_user_can_not_register(self):
        response = self.client.post(self.register_url, data=self.fail_data)
        self.assertEqual(response.status_code, 400)


class TestLoginWebService(APITestCase):
    def setUp(self) -> None:
        self.register_url = reverse('web_service_register')
        self.register_success_data = {"email": "wsrt@gmail.com",
                                      "phone_number": "+989384024575",
                                      "password": "mfpass1381"}
        self.login_url = reverse('web_service_login')
        self.login_success_data = {
            "phone_number": "+989384024575",
            "password": "mfpass1381"}
        self.login_fail_data = {
            "phone_number": "+989384024575",
            "password": "mfpass1383"}

    def test_user_can_register(self):
        self.client.post(self.register_url, data=self.register_success_data)
        response = self.client.post(self.login_url, data=self.login_success_data)
        self.assertEqual(response.status_code, 200)

    def test_user_can_not_register(self):
        self.client.post(self.register_url, data=self.register_success_data)
        response = self.client.post(self.login_url, data=self.login_fail_data)
        self.assertEqual(response.status_code, 401)


class TestProfileCreate(APITestCase):
    def setUp(self) -> None:
        self.register_url = reverse('web_service_register')
        self.register_success_data = {"email": "wsrt@gmail.com",
                                      "phone_number": "+989384024575",
                                      "password": "mfpass1381"}
        self.login_url = reverse('web_service_login')
        self.login_success_data = {
            "phone_number": "+989384024575",
            "password": "mfpass1381"}
        self.login_fail_data = {
            "phone_number": "+989384024575",
            "password": "mfpass1383"}
        self.profile_create_url = reverse('customer_profile_create')
        self.image_path = 'me.jpg'

    def generate_photo_file(self):
        file = io.BytesIO()
        image = Image.new('RGBA', size=(100, 100), color=(155, 0, 0))
        image.save(file, 'png')
        file.name = 'test.png'
        file.seek(0)
        return file

    def test_can_make_profile(self):
        self.client.post(self.register_url, data=self.register_success_data)
        login = self.client.post(self.login_url, data=self.login_success_data)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + login.data)
        user = CustomUser.objects.get(phone_number="+989384024575")

        data = {
            "first_name": "mmd",
            "last_name": "farahdi",
            "address": "parand",
            "post_code": "3452",
            "profile_image": self.generate_photo_file(),
        }
        response = self.client.post(self.profile_create_url, data=data)
        self.assertEqual(response.status_code, 201)

    def test_cant_make_profile(self):
        self.client.post(self.register_url, data=self.register_success_data)
        login = self.client.post(self.login_url, data=self.login_success_data)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + login.data)
        user = CustomUser.objects.get(phone_number="+989384024575")

        data = {
            "last_name": "farahdi",
            "address": "parand",
            "post_code": "3452",
            "profile_image": self.generate_photo_file(),
        }
        response = self.client.post(self.profile_create_url, data=data)
        self.assertEqual(response.status_code, 400)


class TestProfileRetriveUpdate(APITestCase):
    def setUp(self) -> None:
        self.register_url = reverse('web_service_register')
        self.register_success_data = {"email": "wsrt@gmail.com",
                                      "phone_number": "+989384024575",
                                      "password": "mfpass1381"}
        self.login_url = reverse('web_service_login')
        self.login_success_data = {
            "phone_number": "+989384024575",
            "password": "mfpass1381"}
        self.login_fail_data = {
            "phone_number": "+989384024575",
            "password": "mfpass1383"}
        self.profile_ru_url = reverse('customer_profile_get_update', kwargs={'id': 1})
        self.image_path = 'me.jpg'
        self.profile_create_url = reverse('customer_profile_create')

    def generate_photo_file(self):
        file = io.BytesIO()
        image = Image.new('RGBA', size=(100, 100), color=(155, 0, 0))
        image.save(file, 'png')
        file.name = 'test.png'
        file.seek(0)
        return file

    def test_can_get_profile(self):
        self.client.post(self.register_url, data=self.register_success_data)
        login = self.client.post(self.login_url, data=self.login_success_data)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + login.data)
        user = CustomUser.objects.get(phone_number="+989384024575")

        data = {
            "first_name": "mmd",
            "last_name": "farahdi",
            "address": "parand",
            "post_code": "3452",
            "profile_image": self.generate_photo_file(),
        }
        profile = self.client.post(self.profile_create_url, data=data)
        self.profile_ru_url = reverse('customer_profile_get_update', kwargs={'id': user.id})
        response = self.client.get(self.profile_ru_url)
        self.assertEqual(response.status_code, 200)

    def test_cant_get_profile(self):
        self.client.post(self.register_url, data=self.register_success_data)
        login = self.client.post(self.login_url, data=self.login_success_data)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + login.data)
        user = CustomUser.objects.get(phone_number="+989384024575")

        data = {
            "last_name": "farahdi",
            "address": "parand",
            "post_code": "3452",
            "profile_image": self.generate_photo_file(),
        }
        response = self.client.get(self.profile_ru_url, data=data)
        self.assertEqual(response.status_code, 404)

    def test_can_update_profile(self):
        self.client.post(self.register_url, data=self.register_success_data)
        login = self.client.post(self.login_url, data=self.login_success_data)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + login.data)
        user = CustomUser.objects.get(phone_number="+989384024575")

        data = {
            "first_name": "mmd",
            "last_name": "farahdi",
            "address": "parand",
            "post_code": "3452",
            "profile_image": self.generate_photo_file(),
        }
        data2 = {
            "first_name": "mmdedit",
            "last_name": "farahdi",
            "address": "parand",
            "post_code": "3452",
            "profile_image": self.generate_photo_file(),
        }
        profile = self.client.post(self.profile_create_url, data=data)
        self.profile_ru_url = reverse('customer_profile_get_update', kwargs={'id': user.id})
        response = self.client.put(self.profile_ru_url, data=data2)
        print(response.data)
        self.assertEqual(response.status_code, 200)


class TestShopsListWebService(APITestCase):
    def setUp(self) -> None:
        self.register_url = reverse('web_service_register')
        self.register_success_data = {"email": "wsrt@gmail.com",
                                      "phone_number": "+989384024575",
                                      "password": "mfpass1381"}
        self.login_url = reverse('web_service_login')
        self.login_success_data = {
            "phone_number": "+989384024575",
            "password": "mfpass1381"}
        self.shops_list_url = reverse('shops')

    def test_can_get_shops_list(self):
        self.client.post(self.register_url, data=self.register_success_data)
        login = self.client.post(self.login_url, data=self.login_success_data)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + login.data)
        user = CustomUser.objects.get(phone_number="+989384024575")
        type1 = Type.objects.create(title='i')
        type2 = Type.objects.create(title='m')
        type3 = Type.objects.create(title='s')
        shop1 = Shop.objects.create(creator_id=user.id, name='n', type=type1, status='in progress')
        shop2 = Shop.objects.create(creator_id=user.id, name='n', type=type1, status='in progress')
        shop3 = Shop.objects.create(creator_id=user.id, name='n', type=type2, status='in progress')
        shop4 = Shop.objects.create(creator_id=user.id, name='n', type=type2, status='in progress')
        shop5 = Shop.objects.create(creator_id=user.id, name='n', type=type3, status='in progress')
        shop6 = Shop.objects.create(creator_id=user.id, name='n', type=type3, status='in progress')
        response = self.client.get(self.shops_list_url)
        print(response)
        self.assertEqual(response.status_code, 200)


class TestVerifyPhoneNumberAndRegister(APITestCase):
    def setUp(self) -> None:
        self.data = {"phone_number": "+989024008517"}
        self.otp_register_url = reverse('verify_code_register')

    def test_can_get_otp_code(self):
        response = self.client.get(self.otp_register_url, data=self.data, content_type="application/json")
        self.assertEqual(response.status_code, 200)


"""
rest of phase 3 tests
*********
*********
*********
*********
*********
*********
*********
*********
*********
*********
*********
*********
*********
"""


class TestVerifyPhoneNumberAndRegisterWithOtp(APITestCase):
    def setUp(self) -> None:
        self.otp_register_url = reverse('verify_code_register')
        register = self.client.get(self.otp_register_url, data={"phone_number": "+989024008517"},
                                   content_type="application/json")
        self.data = {"phone_number": "+989024008517", 'otp': register.data['otp']}

    def test_can_post_otp_code(self):
        print(self.data)
        response = self.client.post(self.otp_register_url, data=self.data, content_type="application/json")
        print(response.data)
        self.assertEqual(response.status_code, 200)

class TestVerifyCodeForLogin(APITestCase):
    def setUp(self) -> None:
        self.data = {"phone_number": "+989024008517"}
        self.login_code_url = reverse('verify_code_login')
        user = CustomUser.objects.create(phone_number="+989024008517")
        user.phone_number_verify = True

    def test_can_get_verify_code(self):
        response = self.client.get(self.login_code_url, data=self.data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
