from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    # Поля, которые будут отображаться в списке пользователей
    list_display = ('login', 'name', 'is_staff')

    # Поля, по которым можно фильтровать пользователей
    list_filter = ('is_staff', 'is_superuser', 'is_active')

    # Поля, которые будут использоваться при редактировании пользователя
    fieldsets = (
        (None, {'fields': ('login', 'password')}),
        ('Personal info', {'fields': ('name',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )

    # Поля, которые будут использоваться при создании пользователя
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('login', 'name', 'password1', 'password2'),
        }),
    )

    # Поля, по которым можно искать
    search_fields = ('login', 'name')
    ordering = ('login',)


# Регистрируем модель с кастомным UserAdmin
admin.site.register(User, CustomUserAdmin)