from django.urls import path
from .views import *

urlpatterns = [
    path('', PanelPage.as_view(), name='panel'),
    path('shop_create/', CreateShop.as_view(), name='create_shop'),
    path('delete_shop/<slug:slug>/', DeleteShop.as_view(), name='delete_shop'),
    path('update_shop/<slug:slug>/', EditShop.as_view(), name='edit_shop'),
    path('shop_page/<slug:slug>/', ShopPage.as_view(), name='shop_page'),
    path('add_product/<int:id>/', AddProduct.as_view(), name='add_product'),
    path('carts/<slug:slug>/', CartsListView.as_view(), name='carts'),
    path('cart_detail/<int:pk>/', CartDetails.as_view(), name='cart_details'),
    path('change_status/<int:pk>/', change_status, name='change_status'),
    path('register/', shop_register_user, name='shop_register'),
    path('login/', shop_login_user, name='shop_login'),
    path('logout/', logout_user, name='shop_logout'),
    path('shop_report/', EachShopReport.as_view(), name='shop_report_charts'),
    path('render_charts/', RenderCharts.as_view(), name='render_charts'),
    path('customers_information/', CustomersTable.as_view(), name='customers_information'),
    # path('')
]
