from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from utils.pagin import get_page_context
from django.urls import reverse

POSTS_PER_PAGE = 10
POSTS_ON_LIST = 20


def index(request):
    text = 'Последние обновления на сайте'
    post_list = Post.objects.all().order_by('-pub_date')
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'title': text,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    text = 'Группа сообщества: '
    group = get_object_or_404(Group, slug=slug)
    post_list_group = Post.objects.filter(group=group).order_by('-pub_date')
    context = {
        'group': group,
        'posts': post_list_group,
        'title': text,
    }
    context.update(get_page_context(post_list_group, request))
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    user = User.objects.get(username=username)
    posts_user = Post.objects.filter(author=user)
    posts_count = posts_user.count()
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=user
        ).exists()
    else:
        following = False
    profile = user
    context = {
        'author': user,
        'posts_count': posts_count,
        'following': following,
        'profile': profile,
    }
    context.update(get_page_context(user.posts.all(), request))
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post_info = get_object_or_404(Post, pk=post_id)
    author = Post.author
    authors_post = post_info.author.posts.count()
    form = CommentForm()
    comments = post_info.comments.all()
    context = {
        'author': author,
        'post_info': post_info,
        'authors_post': authors_post,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if request.method == 'POST':
        if not form.is_valid():
            return render(request, 'posts/create_post.html', {'form': form})
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, id=post_id, author=request.user)
    user = request.user.get_username()
    is_edit = True
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)

    if request.method == 'GET':
        if user != post.author.username:
            return redirect('posts:post_detail', post.id)

    elif request.method == 'POST':
        if form.is_valid():
            form.save()
        return redirect('posts:post_detail', post.id)

    context = {
        'form': form,
        'post': post,
        'is_edit': is_edit,
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('posts:post_detail', post_id=post_id)
    return render(request, 'posts/includes/comment.html', {
        'form': form, 'post': post})


@login_required
def follow_index(request):
    list_of_posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(list_of_posts, POSTS_ON_LIST)
    page_namber = request.GET.get('page_obj')
    page = paginator.get_page(page_namber)
    context = {'page_obj': page}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    is_follower = Follow.objects.get_or_create(user=user, author=author)
    if user != author and not is_follower.exists():
        Follow.objects.create(user=user, author=author)
    return redirect(reverse('posts:profile', args=[username]))


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    is_follower = Follow.objects.filter(user=request.user, author=author)
    if is_follower.exists():
        is_follower.delete()
    return redirect('posts:profile', username=author)
