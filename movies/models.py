from django.db import models
from django.conf import settings

class Movie(models.Model):
    title = models.CharField(max_length=255)
    genres = models.JSONField()
    movie_id = models.IntegerField(unique=True)
    video_file = models.FileField(upload_to='movies/videos/', null=True, blank=True)
    rating = models.FloatField(default=5.0)
    rating_count = models.IntegerField(default=1)

    def update_rating(self, new_rating):
        ratings = self.ratings.all()
        if ratings.exists():
            total = sum(r.rating for r in ratings)
            self.rating = total / ratings.count()
            self.rating_count = ratings.count()
            self.save()

    def __str__(self):
        return self.title

class Liked(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    movie = models.ForeignKey('Movie', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'movie')

    def __str__(self):
        return f'{self.user.name} likes {self.movie.title}'

class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    movie = models.ForeignKey('Movie', on_delete=models.CASCADE, null=True, blank=True)  # Добавлено поле movie
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Comment from {self.user.name} for {self.movie.title if self.movie else 'no movie'}"
class MovieRating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ratings')
    movie = models.ForeignKey('Movie', on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'movie')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.name}: {self.rating} for {self.movie.title}"

class Complaint(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Complaint from {self.user.name}"