from django.db import models
from django.conf import settings

class Movie(models.Model):
    title = models.CharField(max_length=255)
    genres = models.JSONField()
    movie_id = models.IntegerField(unique=True)
    video_file = models.FileField(upload_to='movies/videos/', null=True, blank=True)
    rating = models.FloatField(default=5.0)  # Средний рейтинг
    rating_count = models.IntegerField(default=1)  # Количество оценок

    def update_rating(self, new_rating):
        total = self.rating * self.rating_count
        self.rating = (total + new_rating) / (self.rating_count + 1)
        self.rating_count += 1
        self.save()

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


class Complaint(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Жалоба от {self.user.username}"

class MovieRating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'movie')  # Один пользователь - одна оценка