from django.urls import path
from . import views
from .views import upload_movie_video

urlpatterns = [
    path('', views.movie_list, name='movie_list'),
    path('<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('<int:movie_id>/like/', views.like_movie, name='like_movie'),
    path('movie/<int:movie_id>/upload_video/', upload_movie_video, name='upload_movie_video'),
]