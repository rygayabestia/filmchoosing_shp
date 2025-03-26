from django.urls import path, include
from django.views.generic import RedirectView
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('movies/', include('movies.urls')),
    path('users/', include('users.urls')),
    # Перенаправляем корневой URL на список фильмов
    path('', RedirectView.as_view(url='/movies/')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)