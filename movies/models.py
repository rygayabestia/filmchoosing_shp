from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.conf import settings

class Movie(models.Model):
    title = models.CharField(max_length=255)
    genres = models.JSONField()
    movie_id = models.IntegerField(unique=True)
    video_file = models.FileField(upload_to='movies/videos/', null=True, blank=True)
    rating = models.FloatField(default=5.0)
    rating_count = models.IntegerField(default=1)

    def update_rating(self):
        from django.db.models import Avg, Count
        result = self.ratings.aggregate(
            avg=Avg('rating'),
            count=Count('id')
        )
        self.rating = result['avg'] or 0
        self.rating_count = result['count'] or 0
        self.save(update_fields=['rating', 'rating_count'])

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
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=False,  # Явно указываем, что NULL не допустим
        blank=False,
        verbose_name='Пользователь'
    )
    movie = models.ForeignKey(
        'Movie',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Фильм'
    )
    text = models.TextField(verbose_name='Текст комментария')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    is_resolved = models.BooleanField(default=False, verbose_name='Решен')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f"Комментарий от {self.user.username}"

class MovieRating(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    movie = models.ForeignKey(
        'Movie',
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    rating = models.PositiveSmallIntegerField(
        choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')],
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'movie')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.movie.title} - {self.rating}★"

class Complaint(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Complaint from {self.user.name}"