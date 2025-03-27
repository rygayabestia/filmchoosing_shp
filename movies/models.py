from django.db import models
from django.conf import settings

class Movie(models.Model):
    title = models.CharField(max_length=255)
    genres = models.JSONField()
    movie_id = models.IntegerField(unique=True)
    video_file = models.FileField(upload_to='movies/videos/', null=True, blank=True)


    def __str__(self):
        return self.title

class Comment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Исправлено с Movie на пользователя
        on_delete=models.CASCADE,
    )
    movie = models.ForeignKey(
        'movies.Movie',
        on_delete=models.CASCADE,
        related_name='comments'  # Перенесено сюда
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.username} - {self.movie.title}"