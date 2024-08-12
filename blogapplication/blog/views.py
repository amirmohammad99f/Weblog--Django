from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from .models import *
from .forms import *
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView, DetailView
from django.views.decorators.http import require_POST
from django.db.models import Q
# from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.contrib.postgres.search import TrigramSimilarity


# Create your views here.

def index(request):
    return render(request, 'blog/index.html')


# def post_list(request):
#     posts = Post.published.all()
#     paginator = Paginator(posts, 3)
#     page_number = request.GET.get('page', 1)
#     try:
#         posts = paginator.get_page(page_number)
#     except EmptyPage:
#         posts = paginator.get_page(paginator.num_pages)
#     except PageNotAnInteger:
#         posts = paginator.get_page(1)
#     context = {'posts': posts}
#     return render(request, 'blog/list.html', context)


# ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^
# | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | |
class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/list.html'


def post_detail(request, pk):
    post = get_object_or_404(Post, id=pk, status=Post.Status.PUBLISHED)
    comments = post.comments.filter(active=True)
    form = CommentForm()
    context = {'post': post,
               'form': form,
               'comments': comments
               }
    return render(request, 'blog/detail.html', context)


# ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^
# | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | |
# class PostDetailView(DetailView):
#     model = Post
#     template_name = 'blog/detail.html'


def ticket(request):
    if request.method == "POST":
        form = TicketForm(request.POST)
        print(require_POST)
        print(request)
        if form.is_valid():
            cd = form.cleaned_data
            Ticket.objects.create(message=cd['message'], name=cd['name'],
                                  phone=cd['phone'], email=cd['email'],
                                  subject=cd['subject'])
            return redirect("blog:ticket")
    else:
        form = TicketForm()
    return render(request, "forms/ticket.html", {"form": form})


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
    context = {
        'post': post,
        'form': form,
        'comment': comment,
    }
    return render(request, "forms/comment.html", context)


def post_search(request):
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            # search_query = SearchQuery(query)
            # search_vector = SearchVector('title') + SearchVector(
            #     'description') + SearchVector('slug')
            # results = Post.published.annotate(search=search_vector,
            #                                   rank=SearchRank(search_vector,
            #                                                   search_query)).filter(
            #     search=search_query).order_by('-rank')
            results1 = Post.published.annotate(
                similarity=TrigramSimilarity('title', query) +
                           TrigramSimilarity('description', query)
            ).filter(similarity__gte=0.1)

            results2 = Image.objects.annotate(
                similarity=TrigramSimilarity('title', query) +
                           TrigramSimilarity('description', query)
            ).filter(similarity__gte=0.1)

            # Combine results
            results = list(results1) + list(results2)
            results.sort(key=lambda x: x.similarity, reverse=True)
    context = {
        'query': query,
        'results': results
    }
    return render(request, 'blog/search.html', context)


def profile(request):
    user = request.user
    posts = Post.published.filter(author=user)
    return render(request, 'blog/profile.html', {"posts": posts})


def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            Image.objects.create(image_file=form.cleaned_data['image1'],
                                 post=post)
            Image.objects.create(image_file=form.cleaned_data['image2'],
                                 post=post)
            post.images.add(form.cleaned_data['image2'])

            return redirect('blog:create_post')
    else:
        form = PostForm()
    context = {
        'form': form,
    }
    return render(request, 'forms/create_post.html', context)
