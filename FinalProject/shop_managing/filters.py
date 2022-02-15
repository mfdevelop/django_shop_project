import django_filters
from .models import *
from django_filters import DateFilter, CharFilter


class CartsFilter(django_filters.FilterSet):
    class Meta:
        model = Cart
        fields = '__all__'

    # @property
    # def qs(self):
    #     parent = super().qs
    #     author = getattr(self.request, 'user', None)
    #
    #     return parent.filter(is_published=True) | parent.filter(author=author)
