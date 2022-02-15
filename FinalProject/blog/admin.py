from django.contrib import admin
from .views import*
# Register your models here.
admin.site.register(BlogPostComment)
admin.site.register(BlogPostCategory)
admin.site.register(BlogPost)
admin.site.register(BlogPostTag)
