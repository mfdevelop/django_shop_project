from django.contrib import admin
from .models import *


# Register your models here.

@admin.register(UserProfile)
class CustomUser(admin.ModelAdmin):
    search_fields = ('user',)
