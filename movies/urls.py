from django.urls import path
from . import views
from .views import upload_movie_video

urlpatterns = [
    path('', views.movie_list, name='movie_list'),
    path('<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('<int:movie_id>/like/', views.like_movie, name='like_movie'),
    path('<int:movie_id>/upload_video/', views.upload_movie_video, name='upload_movie_video'),  # Убрал лишний 'movie/'
    path('complaints/', views.complaint_list, name='complaint_list'),
    path('complaints/submit/', views.submit_complaint, name='submit_complaint'),
    path('complaints/resolve/<int:complaint_id>/', views.resolve_complaint, name='resolve_complaint'),
    path('<int:movie_id>/rate/', views.rate_movie, name='rate_movie'),
    path('movie/<int:movie_id>/comment/', views.user_comments, name='user_comments'),
]