from django.db import models
import random
from django.utils.text import slugify
from users.models import CustomUser


# Create your models here.

class BlogPostCategory(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class BlogPostTag(models.Model):
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name


def rand_slug():
    return ''.join(str(random.randint(0, 9)) for _ in range(10))


class BlogPost(models.Model):
    title = models.CharField(max_length=50)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default=None)
    short_description = models.CharField(max_length=255)
    image = models.ImageField(upload_to="uploads/")
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ManyToManyField(BlogPostCategory)
    tag = models.ManyToManyField(BlogPostTag)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            for post in BlogPost.objects.all():
                if post.slug == self.title:
                    self.slug = slugify(self.title + rand_slug())
                    break
            else:
                self.slug = slugify(self.title)
        super(BlogPost, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class BlogPostComment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.PROTECT, default=None)
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE)
    comment_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.post.title + self.created_at.strftime("%Y/%m/%d")
