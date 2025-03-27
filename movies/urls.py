from django.urls import path
from . import views
from .views import upload_movie_video

urlpatterns = [
    path('', views.movie_list, name='movie_list'),
    path('<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('<int:movie_id>/like/', views.like_movie, name='like_movie'),
    path('<int:movie_id>/upload_video/', views.upload_movie_video, name='upload_movie_video'),  # Убрал лишний 'movie/'
    path('profile/comments/', views.user_comments, name='user_comments'),
]