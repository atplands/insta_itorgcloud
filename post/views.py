from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect

from post.models import Post, Tag, Follow, Stream, Likes, PostImage
from django.contrib.auth.models import User
from post.forms import NewPostform, EditPostForm
from authy.models import Profile
from django.urls import resolve
from comment.models import Comment
from comment.forms import NewCommentForm
from django.core.paginator import Paginator

from django.db.models import Q

from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt
# from post.models import Post, Follow, Stream




@login_required
def index(request):
    user = request.user
    user = request.user
    all_users = User.objects.all()
    follow_status = Follow.objects.filter(following=user, follower=request.user).exists()

    profile = Profile.objects.all()

    posts = Stream.objects.filter(user=user)
    group_ids = []

    
    for post in posts:
        group_ids.append(post.post_id)
        
    post_items = Post.objects.filter(id__in=group_ids).all().order_by('-posted')

    query = request.GET.get('q')
    if query:
        users = User.objects.filter(Q(username__icontains=query))

        paginator = Paginator(users, 6)
        page_number = request.GET.get('page')
        users_paginator = paginator.get_page(page_number)


    context = {
        'post_items': post_items,
        'follow_status': follow_status,
        'profile': profile,
        'all_users': all_users,
        # 'users_paginator': users_paginator,
    }
    return render(request, 'index.html', context)


@login_required
def NewPost(request):
    user = request.user
    profile = get_object_or_404(Profile, user=user)
    tags_obj = []
    
    if request.method == "POST":
        form = NewPostform(request.POST, request.FILES)
        if form.is_valid():
            # picture = form.cleaned_data.get('picture')
            img = request.FILES.getlist('post-picture')[0]
            caption = form.cleaned_data.get('caption')
            tag_form = form.cleaned_data.get('tags')
            tag_list = list(tag_form.split(','))

            for tag in tag_list:
                t, created = Tag.objects.get_or_create(title=tag)
                tags_obj.append(t)
            p, created = Post.objects.get_or_create(caption=caption, user=user) # picture=picture, 
            p.tags.set(tags_obj)
            p.save()
            post_img_obj = PostImage.objects.create(post=p, image=img)
            return redirect('profile', request.user.username)
    else:
        form = NewPostform()
    context = {
        'form': form
    }
    return render(request, 'landbook/newpost.html', context)
from django.core.files import File

@login_required
def EditPost(request, post_id):
    user = request.user
    post = get_object_or_404(Post, id=post_id, user=user)
    
    if request.method == "POST":
       
        image_ids_to_delete_str = request.POST.get('imageIDsToDelete')
        if len(image_ids_to_delete_str) > 0:
            imageIDsToDelete_list = [int(img_id) for img_id in image_ids_to_delete_str.split(",")]
            PostImage.objects.filter(id__in=imageIDsToDelete_list).delete()


        form = EditPostForm(request.POST, request.FILES) # request.FILES.getlist('featured_images')
        

        if form.is_valid():
            post_images_to_add = request.FILES.getlist('imageUpload')
            for post_img in post_images_to_add:
                post_img_obj = PostImage(post=post, image=post_img) #  user=request.user
                post_img_obj.save()
                

            caption = form.cleaned_data.get('caption')
            post.caption = caption
            post.save()
            tag_form = form.cleaned_data.get('tags')
            tag_list = list(tag_form.split(','))
            for tag in tag_list:
                tag_obj, created = Tag.objects.get_or_create(title=tag)
                post.tags.add(tag_obj)

            return redirect('profile', request.user.username)
    else:
        form = EditPostForm(instance=post)
         
    context = {
        'form': form
    }
    return render(request, 'landbook/edit_post.html', context)   

        

from django.contrib import messages        
from django.shortcuts import get_object_or_404
@csrf_exempt
@login_required
def deletePost(request, post_id):
    obj = get_object_or_404(Post, id=post_id)
    obj.delete()
    messages.success(request, f"Post deleted successfully.",
                         extra_tags='alert alert-primary alert-dismissible fade show')
    return redirect('profile', request.user.username)
       
        



@login_required
def PostDetail(request, post_id):
    user = request.user
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post=post).order_by('-date')

    if request.method == "POST":
        form = NewCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = user
            comment.save()
            return HttpResponseRedirect(reverse('post-details', args=[post.id]))
    else:
        form = NewCommentForm()

    context = {
        'post': post,
        'form': form,
        'comments': comments
    }

    return render(request, 'postdetail.html', context)

@login_required
def Tags(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)
    posts = Post.objects.filter(tags=tag).order_by('-posted')

    context = {
        'posts': posts,
        'tag': tag

    }
    return render(request, 'tag.html', context)


# Like function
@login_required
def like(request, post_id):
    user = request.user
    post = Post.objects.get(id=post_id)
    current_likes = post.likes
    liked = Likes.objects.filter(user=user, post=post).count()

    if not liked:
        Likes.objects.create(user=user, post=post)
        current_likes = current_likes + 1
    else:
        Likes.objects.filter(user=user, post=post).delete()
        current_likes = current_likes - 1
        
    post.likes = current_likes
    post.save()
    # return HttpResponseRedirect(reverse('post-details', args=[post_id]))
    return HttpResponseRedirect(reverse('post-details', args=[post_id]))

@login_required
def favourite(request, post_id):
    user = request.user
    post = Post.objects.get(id=post_id)
    profile = Profile.objects.get(user=user)

    if profile.favourite.filter(id=post_id).exists():
        profile.favourite.remove(post)
    else:
        profile.favourite.add(post)
    return HttpResponseRedirect(reverse('post-details', args=[post_id]))


