from django.contrib.auth.models import AbstractUser
from django.db import models
from users.models import CustomUser
import random
from django.utils.text import slugify


# Create your models here.

class Type(models.Model):
    title = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.title


def rand_slug():
    return ''.join(str(random.randint(0, 9)) for _ in range(10))


class Shop(models.Model):
    STATUS_CHOICE = (
        ('in progress', 'in progress'),
        ('accepted', 'accepted'),
        ('trash', 'trash'),
    )
    name = models.CharField(max_length=50)
    type = models.ForeignKey(Type, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICE)
    create_time = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            for post in Shop.objects.all():
                if post.slug == self.name:
                    self.slug = slugify(self.name + rand_slug())
                    break
            else:
                self.slug = slugify(self.name)
        super(Shop, self).save(*args, **kwargs)
        # if not self.slug:
        #     print("**slug nadare**")
        #     if Shop.objects.filter(slug=self.name).exists():
        #         print("&&&esmesh slug shode&&&")
        #         self.slug = slugify(self.name + rand_slug())
        #         print("#"*100)
        #         print(self.slug)
        #         print("#"*100)
        #     else:
        #         self.slug = slugify(self.name)
        # super(Shop, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Category(models.Model):
    title = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.title


class Tag(models.Model):
    title = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.title


class Product(models.Model):
    name = models.CharField(max_length=70)
    price = models.IntegerField(verbose_name='price')
    count = models.IntegerField(verbose_name='product_count')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    tag = models.ManyToManyField(Tag)
    main_image = models.ImageField(upload_to='uploads/')
    second_image = models.ImageField(upload_to='uploads/')
    third_image = models.ImageField(upload_to='uploads/')
    create_time = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    creator = models.ForeignKey(CustomUser, on_delete=models.PROTECT)

    def save(self, *args, **kwargs):
        if not self.slug:
            for post in Product.objects.all():
                if post.slug == self.name:
                    self.slug = slugify(self.name + rand_slug())
                    break
            else:
                self.slug = slugify(self.name)
        super(Product, self).save(*args, **kwargs)
        # if not self.slug:
        #     if Shop.objects.filter(slug=self.name).exists():
        #         self.slug = slugify(self.name + rand_slug())
        #     else:
        #         self.slug = slugify(self.name)
        # super(Product, self).save(*args, **kwargs)

    @property
    def is_available(self):
        if self.count > 0:
            return True
        else:
            return False

    def __str__(self):
        return self.name


class Cart(models.Model):
    STATUS_CHOICE = (
        ('in progress', 'in progress'),
        ('paid', 'paid'),
        ('accepted', 'accepted'),
        ('canceled', 'canceled'),
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    status = models.CharField(max_length=15, choices=STATUS_CHOICE)
    last_change = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.phone_number}"


class CartItem(models.Model):
    STATUS_CHOICE = (
        ('in progress', 'in progress'),
        ('paid', 'paid'),
        ('accepted', 'accepted'),
        ('canceled', 'canceled'),

    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    status = models.CharField(max_length=15, choices=STATUS_CHOICE, default='in progress')
    count = models.IntegerField('cart_item_product_count')
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)

    # shop = models.ForeignKey(Shop, on_delete=models.CASCADE, default=None)

    @property
    def total_price(self):
        return self.count * self.product.price

    def __str__(self):
        return f"{self.count}-{self.product}"
