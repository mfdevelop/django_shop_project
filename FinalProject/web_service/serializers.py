from rest_framework.serializers import ModelSerializer
from shop_managing.models import Shop, CartItem, Cart, Category, Tag, Type, Product
from users.models import CustomUser
from .models import *


class UserRegisterSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'phone_number', 'password']


class UserLoginSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['phone_number', 'password']


class UserProfileSerializer(ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['user', 'profile_image', 'first_name', 'last_name', 'address', 'post_code', 'birth_day']


class ShopsSerializer(ModelSerializer):
    class Meta:
        model = Shop
        fields = ['name', 'type']


class ShopTypesSerializer(ModelSerializer):
    class Meta:
        model = Type
        fields = ['title']


class ProductsSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'price', 'count', 'tag']


class CartSerializer(ModelSerializer):
    class Meta:
        model = Cart
        fields = ['user', 'status']


class CartItemSerializer(ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['product', 'status', 'count', 'cart']


class UserVerifyPhoneNumberAndRegisterSerializerGetCode(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['phone_number', 'otp']

# class VerifyPhoneNumberAndRegister(ModelSerializer):
#     class Meta:
#         model = CustomUser
#         fields = ['']

