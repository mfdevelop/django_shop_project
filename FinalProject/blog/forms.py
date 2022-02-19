from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import *
from django import forms
from users.models import CustomUser


class RegisterUserForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['phone_number', 'email', 'password1', 'password2']


class LoginUserForm(ModelForm):
    class Meta:
        model = CustomUser
        fields = ['phone_number', 'password']


# class ForgetPasswordForm(ModelForm):
#     class Meta:
#         model = CustomUser
#         fields = ['phone_number', 'otp', 'password']

class ForgetPasswordForm(forms.Form):
    phone_number = forms.CharField()
    password1 = forms.CharField()
    password2 = forms.CharField()
    otp = forms.CharField()


class SendOtpForm(forms.Form):
    phone_number = forms.CharField()


class TagModelForm(ModelForm):
    class Meta:
        model = BlogPostTag
        fields = ['name']


class CategoryModelForm(ModelForm):
    class Meta:
        model = BlogPostCategory
        fields = '__all__'


class TagDeleteModelForm(forms.ModelForm):
    class Meta:
        model = BlogPostTag
        fields = []


class CategoryDeleteModelForm(forms.ModelForm):
    class Meta:
        model = BlogPostCategory
        fields = []


class PostDeleteModelForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = []


class PostModelForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'short_description', 'image', 'category', 'tag']

    # def save(self, **kwargs):
    #     user = kwargs.pop('user')
    #     instance = super(PostModelForm, self).save(**kwargs)
    #     instance.user = user
    #     instance.save()
    #     return instance


class CommentModelForm(forms.ModelForm):
    class Meta:
        model = BlogPostComment
        fields = ['comment_text']
