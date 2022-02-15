from django.contrib import admin
from django.shortcuts import get_object_or_404

from .models import *
from django.utils.html import format_html
from FinalProject.settings import BASE_DIR
from django.contrib.auth.models import Group

# Register your models here.

admin.site.site_header = 'Karaj Molayi Admin'


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'status', 'create_time')
    list_filter = ('status',)
    list_editable = ('status',)
    search_fields = ('name', 'type',)
    date_hierarchy = 'create_time'
    list_per_page = 5
    actions = ['accept_all']

    # @admin.action()
    def accept_all(self, request, queryset):
        queryset.update(status='accepted')
        # Shop.objects.all().update(status='accepted')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'count', 'category', 'create_time', 'image',)
    list_filter = ('category',)
    search_fields = ('name', 'category',)
    date_hierarchy = 'create_time'
    list_per_page = 5

    # @admin.display(empty_value='_', description='image')
    def image(self, obj):
        if obj.main_image:
            print(BASE_DIR)
            print(obj.main_image.url)
            default_image_url = "/media/uploads/unknown.png"
            return format_html(
                '<img src="{}" onerror="this.onerror=null;this.src="{}";width=100 height=100 />',
                obj.main_image.url,
                default_image_url,
            )


@admin.register(Tag)
class TegAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)
    list_per_page = 10


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)
    list_per_page = 10


@admin.register(Type)
class TypeAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)
    list_per_page = 10


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'count', 'total_price')
    list_filter = ('product',)
    search_fields = ('product',)
    list_per_page = 5


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('status', 'last_change')
    list_filter = ('status',)
    search_fields = ('status', 'last_change')
    list_per_page = 3


@admin.register(CustomUser)
class CustomUser(admin.ModelAdmin):
    exclude = ('password',)
    search_fields = ('email',)

