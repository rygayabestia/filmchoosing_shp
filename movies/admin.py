from django.contrib import admin
from .models import Movie, Comment, Liked, MovieRating, Complaint


class MovieAdmin(admin.ModelAdmin):
    # Поля, отображаемые в списке
    list_display = ('title', 'rating', 'rating_count')

    # Поля в форме редактирования
    fieldsets = (
        (None, {'fields': ('title', 'genres', 'movie_id')}),
        ('Медиа', {'fields': ('video_file',)}),  # Важно: добавили video_file
        ('Рейтинги', {'fields': ('rating', 'rating_count')}),
    )

    # Поля для поиска
    search_fields = ('title',)

    # Фильтры
    list_filter = ('rating',)


admin.site.register(Movie, MovieAdmin)
admin.site.register(Comment)
admin.site.register(Liked)
admin.site.register(MovieRating)
admin.site.register(Complaint)