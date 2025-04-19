from django.contrib.auth.models import AbstractUser
from django.db import models
from movies.models import Movie

class User(AbstractUser):
    # Удаляем все старые поля (name, login, password - они уже есть в AbstractUser)
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

class Liked(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'movie')