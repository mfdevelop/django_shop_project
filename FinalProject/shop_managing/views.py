from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, DetailView, FormView, CreateView, DeleteView, View
from .forms import *
from django.views.generic.edit import UpdateView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from .filters import *
from django.http import JsonResponse
from django.db.models import Sum, F
from django.template.defaulttags import register


class PanelPage(LoginRequiredMixin, ListView):
    model = Shop
    paginate_by = 10
    template_name = 'panel.html'
    login_url = reverse_lazy('shop_login')

    def get_context_data(self, *, object_list=None, **kwargs):
        shops = Shop.objects.filter(creator=self.request.user).filter(status='accepted')
        context = {'shops': shops}
        return context


class CreateShop(LoginRequiredMixin, FormView):
    model = Shop
    shop_form = CreateShopForm
    fields = ['name', 'type']
    login_url = reverse_lazy('shop_login')

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)

    def get(self, *args, **kwargs):
        if Shop.objects.filter(status='in progress').filter(creator=self.request.user).count() != 0:
            messages.error(self.request, 'you have an un accepted shop please wait for finish it proces')
            return redirect(reverse('panel'))
        else:
            return render(self.request, 'add_shop.html', {'shop_form': self.shop_form})

    def post(self, *args, **kwargs):
        form = self.shop_form(self.request.POST)
        tempt_shop_form = form.save(commit=False)
        tempt_shop_form.creator = self.request.user
        tempt_shop_form.status = "in progress"
        if form.is_valid():
            form.save()
            messages.success(self.request, 'shop added to progress successfully')
            return redirect(reverse_lazy('panel'))
        messages.error(self.request, 'invalid inputs !!')
        return render(self.request, 'add_shop.html', {'shop_form': self.shop_form})


class DeleteShop(LoginRequiredMixin, DeleteView):
    model = Shop
    template_name = 'delete_shop.html'
    login_url = reverse_lazy('shop_login')

    def delete(self, request, *args, **kwargs):
        shop = Shop.objects.get(slug=kwargs['slug'])
        shop.status = 'trash'
        shop.save()
        print("%" * 100)
        print(shop.status)
        print("%" * 100)
        success_url = reverse_lazy('panel')
        return HttpResponseRedirect(success_url)


class EditShop(LoginRequiredMixin, UpdateView):
    model = Shop
    fields = ['name', 'type']
    template_name = 'edit_shop.html'
    success_url = reverse_lazy('panel')
    login_url = reverse_lazy('shop_login')

    def post(self, request, *args, **kwargs):
        super(EditShop, self).post(self, request, *args, **kwargs)
        shop = Shop.objects.get(slug=kwargs['slug'])
        shop.status = "in progress"
        shop.save()
        return HttpResponseRedirect(self.get_success_url())


class ShopPage(LoginRequiredMixin, DetailView):
    model = Shop
    template_name = 'shop_page.html'
    login_url = reverse_lazy('shop_login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.filter(creator=self.request.user).filter(
            shop=kwargs['object'])
        return context


class AddProduct(LoginRequiredMixin, CreateView):
    product_form = CreateProductForm
    login_url = reverse_lazy('shop_login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop'] = get_object_or_404(Shop, id=kwargs['id'])
        global id
        id = kwargs['id']
        return context

    success_url = reverse_lazy('panel')

    def get(self, *args, **kwargs):
        shop = get_object_or_404(Shop, id=kwargs['id'])
        return render(self.request, 'add_product.html', {'product_form': self.product_form, 'shop': shop})

    def post(self, *args, **kwargs):
        form = self.product_form(self.request.POST or None, self.request.FILES or None)
        tempt_product_form = form.save(commit=False)
        tempt_product_form.creator = self.request.user
        tempt_product_form.shop = get_object_or_404(Shop, id=kwargs['id'])
        if form.is_valid():
            form.save()
            messages.success(self.request, 'product added successfully')
            tempt_slug = get_object_or_404(Shop, id=kwargs['id']).slug
            return redirect(reverse_lazy('shop_page', kwargs={'slug': tempt_slug}))
        messages.error(self.request, 'invalid inputs !!')
        return render(self.request, 'add_product.html', {'product_form': self.product_form})


class CartsListView(LoginRequiredMixin, ListView):
    model = Cart
    template_name = 'carts.html'
    paginate_by = 10
    login_url = reverse_lazy('shop_login')

    class Meta:
        ordering = ['last_change']

    def get_context_data(self, *args, **kwargs):
        carts = Cart.objects.filter(cartitem__product__shop__creator=self.request.user).distinct()
        cartFilter = CartsFilter(request=self.request.GET, queryset=carts)
        carts = cartFilter.qs
        print("!" * 100)
        print(self.request.GET)
        print(cartFilter.qs)
        print("!" * 100)
        context = {'carts': carts,
                   'cartFilter': cartFilter}
        return context


class CartDetails(LoginRequiredMixin, DetailView):
    model = Cart
    template_name = 'cart_detail.html'
    login_url = reverse_lazy('shop_login')

    def get_context_data(self, **kwargs):
        context = {'cartItems': CartItem.objects.filter(cart=kwargs['object'])}
        return context


def change_status(request, pk):
    if request.is_ajax() and request.method == 'GET':
        cart = Cart.objects.get(pk=pk)
        status = request.GET.dict().get('status')
        # shop =
        cart.status = status
        cart.save()
        return redirect(reverse_lazy('carts', kwargs={'slug': None}))


def shop_register_user(request):
    if request.user.is_authenticated:
        return render(request, "panel.html")
    else:
        form = RegisterUser()
        if request.method == "POST":
            form = RegisterUser(request.POST)
            if form.is_valid():
                form.save()
                phone_number = form.cleaned_data.get('phone_number')
                password = form.cleaned_data.get('password')
                messages.success(request, 'your account created successfully' + str(phone_number) + f"  {password}")
                return redirect(reverse_lazy('shop_login'))
        context = {'form': form}
        return render(request, 'shop_managing_register.html', context)


def shop_login_user(request):
    form = LoginForm()
    if request.user.is_authenticated:
        return render(request, "panel.html")
    else:
        if request.method == "POST":
            form = LoginForm(request.POST)
            if form.is_valid():
                phone_number = form.cleaned_data.get('phone_number')
                password = form.cleaned_data.get('password')
                # user = authenticate(request.POST, phone_number=phone_number, password=password)
                user = get_object_or_404(CustomUser, phone_number=phone_number, password=password)
                if user:
                    login(request, user)
                    return redirect(reverse_lazy('panel'))
                else:
                    messages.info(request, 'username or password is incorrect')
        context = {'form': form}
        return render(request, 'shop_managing_login.html', context)


@login_required(login_url='shop_login')
def logout_user(request):
    logout(request)
    return redirect(reverse_lazy('shop_login'))


class EachShopReport(View):

    def get(self, request, *args, **kwargs):
        shop_names = []
        shop_sold = []
        shops = Shop.objects.filter(creator=self.request.user)
        for shop in shops:
            shop_names.append(shop.name)
            income = 0
            cartItems = CartItem.objects.filter(cart__status='accepted').filter(product__shop=shop)
            if cartItems:
                for cartItem in cartItems:
                    income += cartItem.total_price
            shop_sold.append(income)
        data = {
            'shop_names': shop_names,
            'shop_sold': shop_sold,
        }
        return JsonResponse(data)


class RenderCharts(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'shops_chart_report.html', {})


class CustomersTable(View):
    def get(self, request, *args, **kwargs):
        cart_items = CartItem.objects.filter(cart__status='accepted').filter(product__shop__creator=request.user)
        customers = CustomUser.objects.filter(cart__cartitem__in=cart_items).distinct()
        each_customer_last_buy = {}
        each_customer_total_buy = {}
        each_customer_total_price = {}
        each_customer_total_product = {}
        for customer in customers:
            temptCartItems = CartItem.objects.filter(cart__user=customer).distinct()
            each_customer_last_buy[customer] = Cart.objects.filter(user=customer).latest('last_change').last_change
            each_customer_total_buy[customer] = temptCartItems.count()
            each_customer_total_price[customer] = \
                temptCartItems.annotate(T_price=F("count") * F("product__price")).aggregate(Sum('T_price'))[
                    'T_price__sum']
            each_customer_total_product[customer] = \
                temptCartItems.aggregate(Sum('count'))['count__sum']
        return render(request, 'customers_informations.html',
                      {'customers': customers, 'each_customer_last_buy': each_customer_last_buy,
                       'each_customer_total_buy': each_customer_total_buy,
                       'each_customer_total_price': each_customer_total_price,
                       'each_customer_total_product': each_customer_total_product})


@register.filter
def get_value(dictionary, key):
    return dictionary.get(key)
