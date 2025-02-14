from django.shortcuts import render, get_object_or_404
from .models import Movie
from django.shortcuts import redirect
from users.models import User
from django.core.paginator import Paginator
from users.models import Liked

def movie_list(request):
    all_movies = Movie.objects.all()
    genres = set()
    for movie in all_movies:
        for genre, value in movie.genres.items():
            if value == 'A':
                genres.add(genre)

    selected_genres = request.GET.getlist('genres')
    movies = []
    if selected_genres:
        for movie in all_movies:
            if all(movie.genres.get(genre) == 'A' for genre in selected_genres):
                movies.append(movie)

    # Получаем список лайкнутых фильмов для текущего пользователя
    liked_movie_ids = []
    if request.session.get('user_id'):
        user_id = request.session['user_id']
        liked_movie_ids = Liked.objects.filter(user_id=user_id).values_list('movie_id', flat=True)

    paginator = Paginator(movies, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'movies/movie_list.html', {
        'movies': movies,  # Передаем отфильтрованные фильмы
        'genres': sorted(genres),  # Сортируем жанры для удобства
        'selected_genres': selected_genres,  # Передаем выбранные жанры
        'liked_movie_ids': liked_movie_ids,  # Передаем список лайкнутых фильмов
    })

def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, movie_id=movie_id)
    filtered_genres = {genre: value for genre, value in movie.genres.items() if value == 'A'}
    return render(request, 'movies/movie_detail.html', {
        'movie': movie,
        'filtered_genres': filtered_genres,
    })

def like_movie(request, movie_id):
    if not request.session.get('user_id'):  # Проверяем, авторизован ли пользователь
        return redirect('login')  # Если нет, перенаправляем на страницу входа

    user_id = request.session['user_id']
    user = User.objects.get(id=user_id)
    movie = get_object_or_404(Movie, id=movie_id)  # Используем get_object_or_404

    # Проверяем, не лайкнул ли пользователь фильм ранее
    if not Liked.objects.filter(user=user, movie=movie).exists():
        Liked.objects.create(user=user, movie=movie)  # Создаем запись о лайке

    return redirect('movie_detail', movie_id=movie_id)  # Перенаправляем на страницу описания фильма
