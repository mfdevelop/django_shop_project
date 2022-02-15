from django.urls import path
from .views import *
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', home_page_render, name='home'),
    path('dashboard/', dashboard_page_render, name='dashboard'),
    path('user_register/', register_user, name='register'),
    path('user_login/', login_user, name='login'),
    path('user_logout/', logout_user, name='logout'),
    path('posts_list/', Posts_list_page_class_base.as_view(), name='posts'),
    path('tags_list/', Tag_list_page_render.as_view(), name='tags'),
    path('add_tag/', login_required(AddTagView.as_view(), login_url='login'), name='add_tag'),
    path('add_cattegory/', login_required(AddCategoryView.as_view(), login_url='login'), name='add_category'),
    path('edit_tag/<int:tag_id>/', edit_tag, name='edit_tag'),
    path('edit_post/<slug:slug>/', edit_post, name='edit_post'),
    path('delete_post/<slug:slug>/', delete_post_form, name='delete_post'),
    path('add_post/', login_required(AddPostView.as_view(), login_url='login'), name='add_post'),
    path('add_comment/<slug:slug>', login_required(AddCommentView.as_view(), login_url='login'), name='add_comment'),
    path('edit_category/<int:id>/', edit_category, name='edit_category'),
    path('delete_tag/<int:tag_id>/', delete_tag_form, name='delete_tag'),
    path('delete_category/<int:id>/', delete_category_form, name='delete_category'),
    path('post_detail/<slug:slug>/', post_detail_page_render, name='post_detail'),
    path('post_comments/<slug:slug>/', each_post_comments_list, name='post_comments'),
    path('post_categories/', Categories_list.as_view(), name='categories_list'),
    path('category_detail/<int:id>/', category_detail, name='category_detail'),
    path('search/', search, name='search'),
]
