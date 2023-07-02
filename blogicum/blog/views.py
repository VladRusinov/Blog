from blog.models import Category, Comment, Post, User

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone as dt

from .forms import CommentForm, EditProfileForm, PostForm

LIMIT_FOR_PAGES = 10


def paginate_posts(request, posts, limit):
    paginator = Paginator(posts, limit)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def select_posts():
    return Post.objects.select_related(
        'category',
        'location',
        'author'
    ).filter(
        category__is_published=True,
        pub_date__lte=dt.now(),
        is_published=True
    )


def index(request):
    """Главная страница"""
    posts = select_posts().annotate(
        comment_count=Count('comments')
    ).all().order_by('-pub_date')
    page_obj = paginate_posts(request, posts, LIMIT_FOR_PAGES)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'blog/index.html', context)


def post_detail(request, post_id):
    """Страница с информацией о посте"""
    post = get_object_or_404(Post.objects.select_related(
        'category',
        'location',
        'author',
    ), id=post_id)
    if request.user.id != post.author_id:
        post = get_object_or_404(select_posts(), id=post_id)
    form = CommentForm()
    comments = post.comments.select_related('author')
    context = {
        'post': post,
        'form': form,
        'comments': comments
    }
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    """Страница с категорией поста"""
    category = get_object_or_404(
        Category.objects.filter(is_published=True,),
        slug=category_slug
    )
    posts = category.posts.select_related(
        'category',
        'location',
        'author'
    ).filter(
        is_published=True,
        pub_date__lte=dt.now(),
    )
    page_obj = paginate_posts(request, posts, LIMIT_FOR_PAGES)
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'blog/category.html', context)


def profile(request, username):
    """Страница с профилем"""
    profile = get_object_or_404(
        User,
        username=username,
    )

    posts = Post.objects.select_related(
        'category',
        'location',
        'author'
    ).filter(author__username=username).annotate(
        comment_count=Count('comments')
    ).all().order_by('-pub_date')
    page_obj = paginate_posts(request, posts, LIMIT_FOR_PAGES)
    context = {
        'profile': profile,
        'page_obj': page_obj,
    }
    return render(request, 'blog/profile.html', context)


@login_required
def create_post(request):
    """Страница создания публикации"""
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )

    context = {
        'form': form
    }
    if form.is_valid():
        instance = form.save(commit=False)
        instance.author = request.user
        instance.save()
        return redirect('blog:profile', request.user.username)
    return render(request, 'blog/create.html', context)


@login_required
def edit_profile(request):
    """Страница редактирования профиля"""
    user = get_object_or_404(User, username=request.user.username)
    form = EditProfileForm(request.POST or None, instance=user)
    if form.is_valid():
        form.save()
        return redirect('blog:profile', form.cleaned_data.get("username"))
    context = {
        'form': form,
    }
    return render(request, 'blog/user.html', context)


@login_required
def edit_post(request, post_id):
    """Страница редактирования публикации"""
    post = get_object_or_404(Post, id=post_id)
    if request.user.id != post.author_id:
        return redirect('blog:post_detail', post_id)
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id)
    context = {
        'post': post,
        'form': form,
    }
    return render(request, 'blog/create.html', context)


@login_required
def delete_post(request, post_id):
    """Страница удаления публикации"""
    post = get_object_or_404(Post, id=post_id)
    if request.user.id != post.author_id:
        return redirect('blog:post_detail', post_id)
    form = PostForm(instance=post)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:index')
    context = {
        'form': form,
        'post': post
    }
    return render(request, 'blog/create.html', context)


@login_required
def add_comment(request, post_id):
    """Добавление комментария"""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    """Страница изменения комментария"""
    post = get_object_or_404(Post, id=post_id)
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user.id != comment.author_id:
        return redirect('blog:post_detail', post_id)
    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id)
    context = {
        'form': form,
        'post': post,
        'comment': comment
    }
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, post_id, comment_id):
    """Страница удаления комментария"""
    comment = get_object_or_404(Comment, id=comment_id)
    post = get_object_or_404(Post, id=post_id)
    if request.user.id != comment.author_id:
        return redirect('blog:post_detail', post_id)
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id)
    context = {
        'comment': comment,
        'post': post
    }
    return render(request, 'blog/comment.html', context)
