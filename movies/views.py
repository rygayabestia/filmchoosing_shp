from sqlite3 import IntegrityError
from venv import logger

from django.core.checks import messages
from django.db import transaction
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from .models import Movie, Comment, MovieRating
from django.shortcuts import redirect
from users.models import User
from django.core.paginator import Paginator
#from users.models import Liked
from django.contrib.auth.decorators import user_passes_test
from .forms import CommentForm
from django.contrib.auth.decorators import login_required
from .models import Complaint, Liked
from .forms import ComplaintForm
from django.shortcuts import render, get_object_or_404, redirect
from .models import Movie, Comment, MovieRating, Liked
from users.models import User
from .forms import CommentForm
from django.contrib import messages
from django.db import transaction, IntegrityError

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
    if 'user_id' in request.session:
        user_id = request.session['user_id']
        liked_movie_ids = list(Liked.objects.filter(user_id=user_id).values_list('movie_id', flat=True))

    paginator = Paginator(movies, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'movies/movie_list.html', {
        'movies': movies,
        'genres': sorted(genres),
        'selected_genres': selected_genres,
        'liked_movie_ids': liked_movie_ids,
    })


def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    comments = Comment.objects.filter(movie=movie)
    filtered_genres = {genre: value for genre, value in movie.genres.items() if value == 'A'}

    form = CommentForm()
    is_authenticated = 'user_id' in request.session
    is_superuser = False
    user_rating = None
    liked_movie_ids = []

    if is_authenticated:
        try:
            user = User.objects.get(id=request.session['user_id'])
            is_superuser = user.is_superuser
            if not user.is_active:
                return redirect('login')

            liked_movie_ids = Liked.objects.filter(user=user).values_list('movie_id', flat=True)

            try:
                rating_obj = MovieRating.objects.get(user=user, movie=movie)
                user_rating = rating_obj.rating
            except MovieRating.DoesNotExist:
                pass

            if request.method == 'POST':
                if 'text' in request.POST:  # Обработка комментариев
                    form = CommentForm(request.POST)
                    if form.is_valid():
                        comment = form.save(commit=False)
                        comment.movie = movie
                        comment.user = user
                        comment.save()
                        return redirect('movie_detail', movie_id=movie.id)



                elif 'rating' in request.POST:

                    try:

                        rating = int(request.POST.get('rating'))

                        if not (1 <= rating <= 5):
                            messages.error(request, "Рейтинг должен быть от 1 до 5")

                            return redirect('movie_detail', movie_id=movie.id)

                        # Проверка существования пользователя и фильма

                        if not User.objects.filter(id=user.id).exists():
                            raise ValueError("Пользователь не существует")

                        if not Movie.objects.filter(id=movie.id).exists():
                            raise ValueError("Фильм не существует")

                        # Используем update_or_create для атомарного обновления

                        rating_obj, created = MovieRating.objects.update_or_create(

                            user=user,

                            movie=movie,

                            defaults={'rating': rating}

                        )

                        # Обновляем средний рейтинг фильма

                        movie.update_rating()

                        messages.success(request, f"Ваша оценка {rating} ★ успешно сохранена!")


                    except IntegrityError as e:

                        logger.error(f"IntegrityError: {str(e)}")

                        if "UNIQUE" in str(e):

                            messages.error(request, "Вы уже оценили этот фильм")

                        else:

                            messages.error(request, "Ошибка базы данных при сохранении")


                    except Exception as e:

                        logger.error(f"Error saving rating: {str(e)}")

                        messages.error(request, f"Ошибка: {str(e)}")

                    return redirect('movie_detail', movie_id=movie.id)
        except User.DoesNotExist:
            messages.error(request, "Пользователь не найден")
            return redirect('login')

    return render(request, 'movies/movie_detail.html', {
        'movie': movie,
        'comments': comments,
        'form': form,
        'filtered_genres': filtered_genres,
        'is_authenticated': is_authenticated,
        'liked_movie_ids': liked_movie_ids,
        'user_rating': user_rating,
        'is_superuser': is_superuser,
    })

def user_comments(request):
    # Проверяем, что пользователь аутентифицирован через сессию
    if 'user_id' not in request.session:
        return redirect('login')

    # Получаем пользователя из базы данных
    try:
        user = User.objects.get(id=request.session['user_id'])
    except User.DoesNotExist:
        return redirect('login')

    comments = Comment.objects.filter(is_resolved=False).order_by('-created_at')

    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            Comment.objects.create(user=user, text=text)
            return redirect('movie_list')

@user_passes_test(lambda u: u.is_superuser)
def upload_movie_video(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)

    if request.method == 'POST':
        video_file = request.FILES.get('video_file')
        if video_file:
            movie.video_file = video_file
            movie.save()

    return redirect('movie_detail', movie_id=movie.movie_id)


def like_movie(request, movie_id):
    if 'user_id' not in request.session:
        return redirect('login')

    user_id = request.session['user_id']
    user = get_object_or_404(User, id=user_id)
    movie = get_object_or_404(Movie, id=movie_id)

    try:
        # Проверяем, есть ли уже лайк от этого пользователя
        liked = Liked.objects.get(user=user, movie=movie)
        liked.delete()  # Удаляем лайк, если он существует
        messages.success(request, "Фильм удален из избранного")
    except Liked.DoesNotExist:
        # Если лайка нет - создаем новый
        Liked.objects.create(user=user, movie=movie)
        messages.success(request, "Фильм добавлен в избранное")

    return redirect('movie_detail', movie_id=movie_id)

def complaint_list(request):
    # Проверяем, что пользователь аутентифицирован через сессию
    if 'user_id' not in request.session:
        return redirect('login')

    # Получаем пользователя из базы данных
    try:
        user = User.objects.get(id=request.session['user_id'])
    except User.DoesNotExist:
        return redirect('login')

    # Для администратора показываем все нерешенные жалобы
    if user.is_superuser:
        complaints = Complaint.objects.filter(is_resolved=False).order_by('-created_at')
    else:
        # Для обычного пользователя показываем только его жалобы
        complaints = Complaint.objects.filter(user=user).order_by('-created_at')

    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            Complaint.objects.create(user=user, text=text)
            return redirect('complaint_list')

    return render(request, 'movies/complaint_list.html', {
        'complaints': complaints,
        'no_complaints': not complaints.exists(),
        'current_user': user,
        'is_admin': user.is_superuser
    })

def resolve_complaint(request, complaint_id):
    if 'user_id' not in request.session or not User.objects.get(id=request.session['user_id']).is_superuser:
        return redirect('login')

    complaint = get_object_or_404(Complaint, pk=complaint_id)
    if request.method == 'POST':
        complaint.is_resolved = not complaint.is_resolved  # Переключаем статус
        complaint.save()
    return redirect('complaint_list')


def submit_complaint(request):
    if 'user_id' not in request.session:
        return redirect('login')

    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            user_id = request.session['user_id']
            user = User.objects.get(id=user_id)
            Complaint.objects.create(user=user, text=text)
            return redirect('movie_list')
    return redirect('movie_list')