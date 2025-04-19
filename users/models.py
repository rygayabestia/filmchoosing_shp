from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=255)
    login = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)  # Это поле будет переопределено в AbstractBaseUser

    # Обязательные поля для кастомной модели User
    REQUIRED_FIELDS = ['name']
    USERNAME_FIELD = 'login'

    # Добавляем стандартные атрибуты
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    def __str__(self):
        return self.name