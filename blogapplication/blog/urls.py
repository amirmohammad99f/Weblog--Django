from django.urls import path
from . import views

app_name = 'blog'
urlpatterns = [
    path('', views.index, name='index'),
    path('posts/', views.PostListView.as_view(), name='posts_list'),
    path('posts/<pk>', views.post_detail, name='posts_detail'),
    path('posts/<post_id>/comment', views.post_comment,
         name='posts_comment'),
    path('ticket', views.ticket, name='ticket'),
    path('profile/create_post', views.create_post, name='create_post'),
    path('search', views.post_search, name='post_search'),
    path('profile', views.profile, name='profile'),
]
