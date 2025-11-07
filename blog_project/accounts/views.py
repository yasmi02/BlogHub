from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from blog.models import Post


def register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request, username=None):
    """User profile view"""
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user

    # Get user's posts
    posts_list = Post.objects.filter(author=user)
    paginator = Paginator(posts_list, 6)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    # Get liked posts
    liked_posts = user.liked_posts.all()[:5]

    context = {
        'profile_user': user,
        'posts': posts,
        'liked_posts': liked_posts,
        'total_posts': posts_list.count(),
        'total_likes': sum(post.total_likes() for post in posts_list),
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile(request):
    """Edit user profile"""
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=request.user.profile
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('user_profile', username=request.user.username)
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'accounts/edit_profile.html', context)


@login_required
def follow_user(request, username):
    """Follow or unfollow a user"""
    user_to_follow = get_object_or_404(User, username=username)

    if user_to_follow == request.user:
        messages.error(request, "You cannot follow yourself!")
        return redirect('user_profile', username=username)

    if request.user in user_to_follow.profile.followers.all():
        user_to_follow.profile.followers.remove(request.user)
        messages.info(request, f'You unfollowed {user_to_follow.username}')
    else:
        user_to_follow.profile.followers.add(request.user)
        messages.success(request, f'You are now following {user_to_follow.username}!')

    return redirect('user_profile', username=username)