from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.views.generic import ListView, View
from .forms import *
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q


# Create your views here.


def home_page_render(request):
    posts = BlogPost.objects.all()
    return render(request, "publichome.html", {'posts': posts})


@login_required(login_url='login')
def dashboard_page_render(request):
    user_id_posts = BlogPost.objects.filter(user=request.user)
    return render(request, "dashboard.html", {'posts': user_id_posts})


def categories_page_render(request):
    return render(request, "categories.html", {})


def posts_list_page_render(request):
    posts = BlogPost.objects.all()
    return render(request, "posts_list.html", {'posts': posts})


class Posts_list_page_class_base(ListView):
    model = BlogPost
    template_name = "posts_list.html"
    context_object_name = 'posts'


class Tag_list_page_render(ListView):
    model = BlogPostTag
    template_name = "tags_list.html"
    context_object_name = "tags"


@login_required(login_url='login')
def edit_tag(request, tag_id):
    tag = get_object_or_404(BlogPostTag, id=tag_id)
    form = TagModelForm(instance=tag)
    print(request)
    print(tag_id)
    if request.method == "POST":
        form = TagModelForm(request.POST, instance=tag)
        print(request.POST)
        if form.is_valid():
            form_temp = form.save(commit=False)
            form_temp.save()
            form.save_m2m()
            return redirect(reverse('tags'))
    context = {'form': form, 'tag': tag}
    return render(request, 'edit_tag.html', context)


@login_required(login_url='login')
def edit_category(request, id):
    category = BlogPostCategory.objects.get(id=id)
    form = CategoryModelForm(instance=category)
    if request.method == "POST":
        form = CategoryModelForm(request.POST, instance=category)
        if form.is_valid():
            form_temp = form.save(commit=False)
            form_temp.save()
            form.save_m2m()
            return redirect(reverse('categories_list'))

    context = {'form': form, 'category': category}
    return render(request, 'edit_category.html', context)


@login_required(login_url='login')
def edit_post(request, slug):
    post = BlogPost.objects.get(slug=slug)
    form = PostModelForm(instance=post)
    if request.method == "POST":
        form = PostModelForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect(reverse('dashboard'))
    context = {'form': form, 'post': post}
    return render(request, 'edit_post.html', context)


class AddTagView(View):
    form = TagModelForm

    def get(self, request, *args, **kwargs):
        return render(request, 'add_tag.html', {'form': self.form, })

    def post(self, request, *args, **kwargs):
        tag_form = self.form(request.POST)
        if tag_form.is_valid():
            tag_form.save()
            messages.success(request, f'تگ مورد نظر ذخیره گردید')
            return redirect(reverse('tags'))


class AddCommentView(View):
    form = CommentModelForm

    def get(self, request, *args, **kwargs):
        post = BlogPost.objects.get(slug=kwargs['slug'])
        return render(request, 'add_comment.html', {'form': self.form, 'post': post})

    def post(self, request, *args, **kwargs):
        comment_form = self.form(request.POST)
        print(kwargs)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = BlogPost.objects.get(slug=kwargs['slug'])
            comment.user = request.user
            comment.save()
            # comment_form.save()
            messages.success(request, f'کامنت مورد نظر ذخیره گردید')
            return redirect(reverse('post_comments', kwargs={'slug': kwargs['slug']}))


class AddCategoryView(View):
    form = CategoryModelForm

    def get(self, request, *args, **kwargs):
        return render(request, 'add_category.html', {'form': self.form, })

    def post(self, request, *args, **kwargs):
        category_form = self.form(request.POST)
        if category_form.is_valid():
            category_form.save()
            messages.success(request, f'دسته بندی مورد نظر ذخیره گردید')
            return redirect(reverse('categories_list'))


class AddPostView(View):
    form = PostModelForm

    def get(self, request, *args, **kwargs):
        return render(request, 'add_post.html', {'form': self.form})

    def post(self, request, *args, **kwargs):
        post_form = self.form(self.request.POST or None, self.request.FILES or None)
        tempt_post_form = post_form.save(commit=False)
        tempt_post_form.user = self.request.user
        # post_form.user = self.request.user
        if post_form.is_valid():
            post_form.save()
            messages.success(request, f'پست مورد نظر ذخیره گردید')
            return redirect(reverse('dashboard'))


@login_required(login_url='login')
def delete_tag(request, tag_id):
    tag = get_object_or_404(BlogPostTag, id=tag_id)
    tag.delete()
    return redirect(reverse('tags'))


@login_required(login_url='login')
def delete_post(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    post.delete()
    return redirect(reverse('dashboard'))


def post_detail_page_render(request, slug):
    post = BlogPost.objects.get(slug=slug)
    comments = post.comment_set.all()
    return render(request, "post_detail.html", {'post': post, 'comments': comments})


def each_post_comments_list(request, slug):
    comments = BlogPostComment.objects.filter(post=BlogPost.objects.get(slug=slug))
    post = BlogPost.objects.get(slug=slug)
    return render(request, "each_post_comments_list.html", {'comments': comments, 'post': post})


class Categories_list(ListView):
    model = BlogPostCategory
    template_name = "categories_list.html"
    context_object_name = 'categories'


def category_detail(request, id):
    category = BlogPostCategory.objects.get(id=id)
    posts = category.post_set.all()
    return render(request, "category_details.html", {"category": category, "posts": posts})


def register_user(request):
    if request.user.is_authenticated:
        return render(request, "dashboard.html")
    else:
        form = RegisterUserForm()
        if request.method == "POST":
            form = RegisterUserForm(request.POST)
            if form.is_valid():
                form.save()
                username = form.cleaned_data.get('username')
                messages.success(request, 'حساب شما با موفقیت ساخته شد' + username)
                return redirect(reverse('login'))
        context = {'form': form}
        return render(request, 'register.html', context)


def login_user(request):
    if request.user.is_authenticated:
        return render(request, "dashboard.html")
    else:
        if request.method == "POST":
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(reverse('dashboard'))
            else:
                messages.info(request, 'نام کاربری یا رمز عبور نادرست است')
        context = {}
        return render(request, 'login.html', context)


@login_required(login_url='login')
def logout_user(request):
    logout(request)
    return redirect(reverse('login'))


@login_required(login_url='login')
def delete_tag_form(request, tag_id):
    tag = get_object_or_404(BlogPostTag, id=tag_id)
    form = TagDeleteModelForm(instance=tag)
    if request.method == "POST":
        tag.delete()
        return redirect(reverse('tags'))
    return render(request, "delete_tag.html", {'form': form, 'tag': tag})


@login_required(login_url='login')
def delete_post_form(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    form = PostDeleteModelForm(instance=post)
    if request.method == "POST":
        post.delete()
        return redirect(reverse('dashboard'))
    return render(request, "delete_post.html", {'form': form, 'post': post})


@login_required(login_url='login')
def delete_category_form(request, id):
    category = get_object_or_404(BlogPostCategory, id=id)
    form = CategoryDeleteModelForm(instance=category)
    if request.method == "POST":
        category.delete()
        return redirect(reverse('categories_list'))
    return render(request, "delete_category.html", {'form': form, 'category': category})


def search(request):
    print(request.POST)
    if request.method == "POST":
        searched = request.POST['search']
        posts = BlogPost.objects.filter(Q(title__icontains=searched) | Q(short_description__icontains=searched))
        return render(request, 'search_resaults.html', {'searched': searched, 'posts': posts})
    else:
        return render(request, 'search_resaults.html', {})
