from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import *
from django import forms
from users.models import CustomUser
from phonenumber_field.modelfields import PhoneNumberField


class CreateShopForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = ['name', 'type']


class CreateProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'count', 'category', 'main_image', 'second_image', 'third_image']


class RegisterUser(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['phone_number', 'password', 'email', 'has_shop']


class LoginForm(forms.Form):
    phone_number = forms.CharField(max_length=15, label='username')
    password = forms.CharField(widget=forms.PasswordInput)
