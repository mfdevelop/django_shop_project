from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.urls import path
from .views import *

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterUser.as_view(), name='web_service_register'),
    path('login/', LoginUser.as_view(), name='web_service_login'),
    path('profile/', ProfileCreate.as_view(), name='customer_profile_create'),
    path('profile/<int:id>/', ProfileRU.as_view(), name='customer_profile_get_update'),
    path('shops/', ShopsList.as_view(), name='shops'),
    path('shop_types/', ShopTypesList.as_view(), name='types'),
    path('products/<int:id>/', ProductsListOnAShop.as_view(), name='products'),
    path('create_cart/', CreateCart.as_view(), name='create_cart'),
    path('add_cart_item/', AddCartItemToCart.as_view(), name='add_to_cart'),
    path('delete_cart_item/', EditCart.as_view(), name='edit_cart'),
    path('pay_cart/', PayCart.as_view(), name='pay_cart'),
    path('in_progress_carts/', InProgressCarts.as_view(), name='in_progress_carts'),
    path('paid_carts/', PaidCarts.as_view(), name='in_progress_carts'),
    path('verify_code_register/', VerifyPhoneNumberAndRegister.as_view(), name='verify_code_register'),
    path('verify_code_login/', VerifyCodeForLogin.as_view(), name='verify_code_login'),
    path('login_otp/', LoginWithOtpCode.as_view(), name='login_otp'),

]
