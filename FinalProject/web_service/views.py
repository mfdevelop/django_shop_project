from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import mixins, status
from .serializers import *
from rest_framework_simplejwt.views import TokenObtainPairView
from kavenegar import *
import random
import time
import redis
from FinalProject.celery import send_otp

redis = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)


# Create your views here.

class RegisterUser(GenericAPIView):
    serializer_class = UserRegisterSerializer
    queryset = CustomUser.objects.filter(has_shop=False)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            register_token = str(TokenObtainPairView.serializer_class.get_token(user).access_token)
            return Response(
                {"user": serializer.data,
                 "token": register_token},
                status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginUser(GenericAPIView):
    serializer_class = UserLoginSerializer
    queryset = CustomUser.objects.filter(has_shop=False)

    def post(self, request, *args, **kwargs):
        email = request.data.get('email', None)
        password = request.data.get('password', None)
        phone_number = request.data.get('phone_number', None)
        user1 = get_object_or_404(CustomUser, phone_number=phone_number)
        if user1:
            if user1.password == password:
                login(request, user1)
                login_token = str(TokenObtainPairView.serializer_class.get_token(user1).access_token)
                return Response(login_token, status=status.HTTP_200_OK)
        return Response({"message": "invalid information"}, status=status.HTTP_401_UNAUTHORIZED)


class ProfileCreate(GenericAPIView):
    serializer_class = UserProfileSerializer
    queryset = UserProfile.objects.all()
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        tempt_user = request.user
        user = get_object_or_404(CustomUser, id=tempt_user.id)
        profile_image = request.data.dict()['profile_image']
        request.data['user'] = request.user.id
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            profile = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileRU(GenericAPIView, mixins.UpdateModelMixin, mixins.RetrieveModelMixin):
    serializer_class = UserProfileSerializer
    queryset = UserProfile.objects.all()
    lookup_field = 'id'
    lookup_url_kwarg = 'id'
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        request.data['user'] = request.user.id
        return self.update(request, *args, **kwargs)


class ShopsList(GenericAPIView, mixins.ListModelMixin):
    serializer_class = ShopsSerializer
    queryset = Shop.objects.filter(status='accepted')
    permission_classes = (IsAuthenticated,)
    filter_fields = ['type']

    def get_queryset(self):
        type = self.request.GET.get('type')
        if type is None:
            return self.queryset.all()
        else:
            return self.queryset.filter(type=type)

    def list(self, request, *args, **kwargs):
        super(ShopsList, self).list(self, request, *args, **kwargs)
        serializer = self.get_serializer(self.get_queryset(), many=True)
        for i in range(len(serializer.data)):
            serializer.data[i]['type'] = Type.objects.get(id=serializer.data[i]['type']).title
        return Response(serializer.data)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ShopTypesList(GenericAPIView, mixins.ListModelMixin):
    serializer_class = ShopTypesSerializer
    queryset = Type.objects.all()
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ProductsListOnAShop(GenericAPIView, mixins.ListModelMixin):
    serializer_class = ProductsSerializer
    queryset1 = Product.objects.filter(count__gt=0)
    lookup_field = 'shop__id'
    lookup_url_kwarg = 'shop__id'
    queryset2 = Product.objects.all()
    queryset = None
    permission_classes = (IsAuthenticated,)
    filter_fields = ['tag', 'price', 'count']

    def get_queryset(self, *args, **kwargs):
        max_price = self.request.GET.get('max_price')
        min_price = self.request.GET.get('min_price')
        existent_status = self.request.GET.get('existent_status')
        if existent_status == 'all':
            self.queryset = self.queryset2
        else:
            self.queryset = self.queryset1
        if (min_price is not None) and (max_price is not None):
            return self.queryset.filter(price__gte=min_price, price__lte=max_price)
        elif min_price is not None:
            return self.queryset.filter(price__gte=min_price)
        elif max_price is not None:
            return self.queryset.filter(price__lte=max_price)
        else:
            return self.queryset

    def list(self, request, *args, **kwargs):
        super(ProductsListOnAShop, self).list(self, request, *args, **kwargs)
        queryset = self.get_queryset().filter(shop_id=kwargs['id'])
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class CreateCart(GenericAPIView, mixins.CreateModelMixin):
    serializer_class = CartSerializer
    queryset = Cart.objects.all()
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        data = {'user': request.user.id, 'status': 'in progress'}
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        cart = serializer.save()
        product_id = request.data['product_id']
        product = Product.objects.get(id=product_id)
        count = 1
        if product.count > 0:
            data = {'product': product_id, 'status': 'in progress', 'cart': cart.id, 'count': count}
            cart_item_serializer = CartItemSerializer(data=data)
            cart_item_serializer.is_valid(raise_exception=True)
            cart_item = cart_item_serializer.save()
            headers = self.get_success_headers(serializer.data)
            return Response(cart.id, status=status.HTTP_201_CREATED, headers=headers)
        errors = {"message": "product don't exists"}
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class AddCartItemToCart(GenericAPIView, mixins.CreateModelMixin, mixins.UpdateModelMixin):
    serializer_class = CartItemSerializer
    queryset = CartItem.objects.all()
    permission_classes = (IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = CartItem.objects.filter(cart_id=request.data['cart']).get(product=request.data['product'])
        product = Product.objects.get(id=request.data['product'])
        request.data['count'] += instance.count
        if product.count >= request.data['count']:
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}
            return Response(serializer.data)
        response = {"message": f"there is only {product.count} number of {product.id}"}
        return Response(response)

    def create(self, request, *args, **kwargs):
        data = request.data
        data['status'] = 'in progress'
        product = Product.objects.get(id=data['product'])
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        if product.count >= data['count']:
            cart_item = serializer.save()
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        errors = {"message": f"there is only {product.count} number of {product.id}"}
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        if CartItem.objects.filter(cart_id=request.data['cart']).filter(product=request.data['product']).filter(
                status='in progress').exists():
            return self.update(request, *args, **kwargs)
        else:
            return self.create(request, *args, **kwargs)


class EditCart(GenericAPIView, mixins.UpdateModelMixin):
    serializer_class = CartItemSerializer
    queryset = CartItem.objects.all()
    permission_classes = (IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = CartItem.objects.filter(cart_id=request.data['cart']).get(product=request.data['product'])
        product = Product.objects.get(id=request.data['product'])
        cart = Cart.objects.get(id=request.data['cart'])
        request.data['count'] = instance.count - request.data['count']
        if request.data['count'] > 0:
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}
            return Response(serializer.data)
        elif request.data['count'] == 0:
            instance.delete()
            if CartItem.objects.filter(cart=cart.id).exists():
                response = {"message": f"cart item deleted"}
                return Response(response)
            else:
                cart.delete()
                response = {"message": f"because of being empty cart {cart.id} deleted"}
                return Response(response)
        else:
            response = {
                "message": f"there is only {instance.count} number exists from {product.name} you can't delete more"}
            return Response(response)

    def put(self, request, *args, **kwargs):
        cart = Cart.objects.get(id=request.data['cart'])
        if CartItem.objects.filter(cart=cart.id).exists():
            return self.update(request, *args, **kwargs)
        else:
            cart.delete()
            response = {"message": f"because of being empty cart {cart.id} deleted"}
            return Response(response)


class PayCart(GenericAPIView, mixins.UpdateModelMixin):
    serializer_class = CartSerializer
    queryset = Cart.objects.all()
    permission_classes = (IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        user = request.user
        cart_id = request.data['cart_id']
        response = {"message": "cart item "}
        has_paid_cart_item = False
        for cart_item in CartItem.objects.filter(cart_id=cart_id).filter(status='in progress'):
            print(cart_item)
            if cart_item.product.count >= cart_item.count:
                cart_item.status = 'paid'
                has_paid_cart_item = True
                cart_item.product.count -= cart_item.count
                cart_item.product.save()
                cart_item.save()
            else:
                cart_item.status = 'canceled'
                cart_item.save()
                response[
                    'message'] += f"{cart_item.id} has product {cart_item.product.id} that has {cart_item.product.count} number and not paid "

        cart = Cart.objects.get(id=cart_id)
        partial = kwargs.pop('partial', False)
        instance = cart
        if has_paid_cart_item:
            request.data['status'] = 'paid'
        else:
            request.data['status'] = 'canceled'
        request.data['user'] = user.id
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        if has_paid_cart_item:
            if response.get("message") != "cart item ":
                # request.data["message"] = response['message']
                print(response)
                data = {"data": serializer.data, "message": response['message']}
            return Response(data)
        else:
            return Response({"message": "cart canceled because if no paid cart_item existent"})

    def post(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class InProgressCarts(GenericAPIView, mixins.ListModelMixin):
    serializer_class = CartSerializer
    queryset = Cart.objects.filter(status='in progress')
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class PaidCarts(GenericAPIView, mixins.ListModelMixin):
    serializer_class = CartSerializer
    queryset = Cart.objects.filter(Q(status='paid') | Q(status='accepted'))

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


def random_generator():
    return ''.join(str(random.randint(0, 9)) for _ in range(8))


def token_generator():
    return int(time.time())


def redis_token_generator(phone_number):
    otp = random_generator()
    redis.psetex(phone_number, 300000, otp)
    return otp


# def send_otp(mobile, otp):
#     body = {'receptor': mobile, 'token': otp, 'template': "verifyuser"}
#     sms_res = requests.get(
#         "https://api.kavenegar.com/v1/5145587872464647743632632B6438566C78456F7435786F4A47344F2F306C4C42595342656670393446453D/verify/lookup.json",
#         params=body)


class VerifyPhoneNumberAndRegister(GenericAPIView, mixins.UpdateModelMixin):
    serializer_class = UserVerifyPhoneNumberAndRegisterSerializerGetCode
    queryset = CustomUser.objects.all()

    def get(self, request, *args, **kwargs):
        # phone_number = request.data['phone_number']
        phone_number = request.GET.dict()['phone_number']
        phone_number = "+" + phone_number[1:]
        otp = redis_token_generator(phone_number)
        phone_number = phone_number[3:]
        phone_number = "0" + phone_number
        send_otp.delay(phone_number, otp)
        phone_number = "+98" + phone_number[1:]
        data = {"phone_number": phone_number, "otp": otp}
        serializer = None
        if CustomUser.objects.filter(phone_number=phone_number).exists():
            user = CustomUser.objects.get(phone_number=phone_number)
            serializer = self.serializer_class(instance=user, data=data)
            if serializer.is_valid():
                user = serializer.save()
                return Response({"otp": otp}, status=status.HTTP_200_OK)
        else:
            serializer = self.serializer_class(data=data)
            if serializer.is_valid():
                user = serializer.save()
                return Response({"otp": otp}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        otp = request.data['otp']
        phone_number = request.data['phone_number']
        user = get_object_or_404(CustomUser, phone_number=phone_number)
        if user:
            if redis.exists(phone_number):
                if redis.get(phone_number) == otp:
                    user.phone_number_verify = True
                    user.save()
                    return Response({"message": "phone number verified successfully"})
                return Response({"message": "otp code not matched"}, status.HTTP_400_BAD_REQUEST)
            return Response({"message": "otp code expired"}, status.HTTP_400_BAD_REQUEST)
        return Response({"message": "phone number not recognized"}, status.HTTP_401_UNAUTHORIZED)


class VerifyCodeForLogin(GenericAPIView, mixins.UpdateModelMixin):
    serializer_class = UserVerifyPhoneNumberAndRegisterSerializerGetCode
    queryset = CustomUser.objects.all()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        phone_number = request.data['phone_number']
        instance = get_object_or_404(CustomUser, phone_number=phone_number)
        otp = redis_token_generator(phone_number)
        phone_number = phone_number[3:]
        phone_number = "0" + phone_number
        send_otp.delay(phone_number, otp)
        request.data['otp'] = str(otp)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            new_user = serializer.save()
            if getattr(instance, '_prefetched_objects_cache', None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}
            if new_user.phone_number_verify:
                return Response(serializer.data, status.HTTP_200_OK)
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        # serializer.is_valid(raise_exception=True)
        return Response(serializer.errors, status.HTTP_401_UNAUTHORIZED)

    def post(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class LoginWithOtpCode(GenericAPIView):
    serializer_class = UserVerifyPhoneNumberAndRegisterSerializerGetCode
    queryset = CustomUser.objects.filter(has_shop=False)

    def post(self, request, *args, **kwargs):
        phone_number = request.data['phone_number']
        otp = request.data['otp']
        user = get_object_or_404(CustomUser, phone_number=phone_number)
        if user:
            if redis.exists(phone_number):
                if redis.get(phone_number) == otp:
                    user.phone_number_verify = True
                    user.save()
                    login(request, user)
                    login_token = str(TokenObtainPairView.serializer_class.get_token(user).access_token)
                    return Response(login_token, status=status.HTTP_200_OK)
                return Response({"message": "otp code not matched"}, status.HTTP_400_BAD_REQUEST)
            return Response({"message": "otp code expired"}, status.HTTP_400_BAD_REQUEST)
        return Response({"message": "phone number not recognized"}, status.HTTP_401_UNAUTHORIZED)
