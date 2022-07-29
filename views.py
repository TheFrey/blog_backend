from django.shortcuts import render, get_object_or_404, HttpResponse, HttpResponseRedirect, Http404, redirect
from .models import Post
from .forms import EmailPostForm, CommentForm, LoginForm, UserRegistrationForm, SearchForm
from django.core.mail import send_mail
from taggit.models import Tag
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, ObjectDoesNotExist
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required


def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = Post.objects.filter(body__icontains=query)
    return render(request,
                  'blog/post/search.html',
                  {'form': form,
                   'query': query,
                   'results': results})


@login_required
def dashboard(request):
    return HttpResponseRedirect(redirect_to=post_list)


def post_detail(request, year, month, day, post):

    post = get_object_or_404(Post, slug=post, status='published', publish__year=year, publish__month=month,
                             publish__day=day)

    comments = post.comments.filter(active=True)

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)

        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm(initial={'name': request.user.username})
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.objects.filter(status="published", tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]
    likes = post.likes
    dislikes = post.dislikes
    return render(request,
                  'blog/post/detail.html',
                  {'post': post,
                   'comments': comments,
                   'comment_form': comment_form,
                   'similar_posts': similar_posts,
                   'like': likes,
                   'dislikes': dislikes})


def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    if request.method == 'POST':
        # Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} ({}) recommends you reading "{}"'.format(cd['name'], cd['email'], post.title)
            message = 'Read "{}" at {}\n\n{}\'s comments: {}'.format(post.title, post_url, cd['name'], cd['comments'])
            send_mail(subject, message, 'vitaliyteterya@gmail.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post,
                                                    'form': form,
                                                    'sent': sent})


def post_list(request, tag_slug=None, search=None):
    object_list = Post.objects.filter(status="published")
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])
    elif search:
        tag = get_object_or_404(Tag, slug=search)
        object_list = object_list.filter(content__icontains=[tag])
    form = SearchForm(request.GET)
    paginator = Paginator(object_list, 3)
    # 3 posts in each page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html', {'page': page,
                                                   'posts': posts,
                                                   'tag': tag,
                                                   'form': form})


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated successfully')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    return render(request, 'blog/account/login.html', {'form': form})


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # Create a new user object but avoid saving it yet
            new_user = user_form.save(commit=False)
            # Set the chosen password
            new_user.set_password(user_form.cleaned_data['password'])
            # Save the User object
            new_user.save()
            return render(request, 'blog/account/registration/register_done.html', {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'blog/account/registration/register.html', {'user_form': user_form})


def add_like(request, year, month, day, post):
    try:
        post = get_object_or_404(Post, slug=post, status='published', publish__year=year,
                                 publish__month=month,
                                 publish__day=day)
        post.likes += 1
        post.save()
    except ObjectDoesNotExist:
        return Http404
    return redirect(request.GET.get('next', post.get_absolute_url()))


def add_dislike(request, year, month, day, post):
    try:
        post = get_object_or_404(Post, slug=post, status='published', publish__year=year,
                                 publish__month=month,
                                 publish__day=day)
        post.dislikes += 1
        post.save()
    except ObjectDoesNotExist:
        return Http404
    return redirect(request.GET.get('next', post.get_absolute_url()))
