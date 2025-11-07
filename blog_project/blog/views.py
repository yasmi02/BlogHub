from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Post, Comment
from .forms import PostForm, CommentForm


def home(request):
    """Display all blog posts with pagination and search"""
    posts_list = Post.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        posts_list = posts_list.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query) |
            Q(tags__name__icontains=search_query)
        ).distinct()
    
    # Tag filtering
    tag_slug = request.GET.get('tag', '')
    if tag_slug:
        posts_list = posts_list.filter(tags__slug=tag_slug)
    
    # Pagination
    paginator = Paginator(posts_list, 6)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    context = {
        'posts': posts,
        'search_query': search_query,
        'tag_slug': tag_slug,
    }
    return render(request, 'blog/home.html', context)


def post_detail(request, slug):
    """Display single post with comments"""
    post = get_object_or_404(Post, slug=slug)
    comments = post.comments.all()
    user_has_liked = False
    
    if request.user.is_authenticated:
        user_has_liked = post.likes.filter(id=request.user.id).exists()
    
    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.user = request.user
            new_comment.save()
            messages.success(request, 'Comment added successfully!')
            return redirect('post_detail', slug=post.slug)
    else:
        comment_form = CommentForm()
    
    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'user_has_liked': user_has_liked,
    }
    return render(request, 'blog/post_detail.html', context)


@login_required
def create_post(request):
    """Create a new blog post"""
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            form.save_m2m()  # Save tags
            messages.success(request, 'Post created successfully!')
            return redirect('post_detail', slug=new_post.slug)
    else:
        form = PostForm()
    
    return render(request, 'blog/post_form.html', {'form': form, 'title': 'Create New Post'})


@login_required
def edit_post(request, slug):
    """Edit an existing post"""
    post = get_object_or_404(Post, slug=slug)
    
    # Check if user is the author
    if post.author != request.user:
        messages.error(request, 'You can only edit your own posts!')
        return redirect('post_detail', slug=slug)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated successfully!')
            return redirect('post_detail', slug=post.slug)
    else:
        form = PostForm(instance=post)
    
    return render(request, 'blog/post_form.html', {'form': form, 'title': 'Edit Post', 'post': post})


@login_required
def delete_post(request, slug):
    """Delete a post"""
    post = get_object_or_404(Post, slug=slug)
    
    if post.author != request.user:
        messages.error(request, 'You can only delete your own posts!')
        return redirect('post_detail', slug=slug)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted successfully!')
        return redirect('home')
    
    return render(request, 'blog/post_confirm_delete.html', {'post': post})


@login_required
def like_post(request, slug):
    """Toggle like on a post"""
    post = get_object_or_404(Post, slug=slug)
    
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        messages.info(request, 'Post unliked.')
    else:
        post.likes.add(request.user)
        messages.success(request, 'Post liked!')
    
    return redirect('post_detail', slug=slug)


@login_required
def delete_comment(request, comment_id):
    """Delete a comment"""
    comment = get_object_or_404(Comment, id=comment_id)
    post_slug = comment.post.slug
    
    if comment.user != request.user:
        messages.error(request, 'You can only delete your own comments!')
        return redirect('post_detail', slug=post_slug)
    
    comment.delete()
    messages.success(request, 'Comment deleted successfully!')
    return redirect('post_detail', slug=post_slug)


def posts_by_tag(request, tag_slug):
    """Display posts filtered by tag"""
    posts_list = Post.objects.filter(tags__slug=tag_slug)
    paginator = Paginator(posts_list, 6)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    context = {
        'posts': posts,
        'tag_slug': tag_slug,
    }
    return render(request, 'blog/home.html', context)
