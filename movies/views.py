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

    # Получаем список лайкнутых фильмов для текущего пользователя через сессию
    liked_movie_ids = []
    if 'user_id' in request.session:
        user_id = request.session['user_id']
        liked_movie_ids = Liked.objects.filter(user_id=user_id).values_list('movie_id', flat=True)

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
    is_liked = False
    user_rating = None

    if is_authenticated:
        user_id = request.session['user_id']
        # Проверка лайка
        is_liked = Liked.objects.filter(user_id=user_id, movie=movie).exists()

        # Получение текущей оценки пользователя
        try:
            rating_obj = MovieRating.objects.get(user_id=user_id, movie=movie)
            user_rating = rating_obj.rating
        except MovieRating.DoesNotExist:
            pass

        # Обработка POST-запроса
        if request.method == 'POST':
            # Обработка комментария
            if 'text' in request.POST:
                form = CommentForm(request.POST)
                if form.is_valid():
                    comment = form.save(commit=False)
                    comment.movie = movie
                    comment.user = User.objects.get(id=user_id)
                    comment.save()
                    return redirect('movie_detail', movie_id=movie.id)

            # Обработка рейтинга
            elif 'rating' in request.POST:
                rating = int(request.POST.get('rating'))
                if 1 <= rating <= 5:  # Проверка допустимого диапазона
                    user = User.objects.get(id=user_id)
                    MovieRating.objects.update_or_create(
                        user=user,
                        movie=movie,
                        defaults={'rating': rating}
                    )
                    movie.update_rating(rating)
                    return redirect('movie_detail', movie_id=movie.id)

    return render(request, 'movies/movie_detail.html', {
        'movie': movie,
        'comments': comments,
        'form': form,
        'filtered_genres': filtered_genres,
        'is_authenticated': is_authenticated,
        'is_liked': is_liked,
        'user_rating': user_rating,
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
    user = User.objects.get(id=user_id)
    movie = get_object_or_404(Movie, id=movie_id)

    if not Liked.objects.filter(user=user, movie=movie).exists():
        Liked.objects.create(user=user, movie=movie)

    return redirect('movie_detail', movie_id=movie_id)


def rate_movie(request, movie_id):
    if 'user_id' not in request.session:
        return redirect('login')

    movie = get_object_or_404(Movie, pk=movie_id)
    if request.method == 'POST':
        rating = int(request.POST.get('rating'))
        try:
            user = User.objects.get(id=request.session['user_id'])
            MovieRating.objects.update_or_create(
                user=user,
                movie=movie,
                defaults={'rating': rating}
            )
            movie.update_rating(rating)
        except User.DoesNotExist:
            return redirect('login')

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

    # Проверяем, является ли пользователь администратором (если нужно)
    # Если вам не нужна проверка на staff, можно удалить эту проверку
    is_staff = getattr(user, 'is_staff', False)  # Безопасная проверка атрибута

    complaints = Complaint.objects.filter(is_resolved=False).order_by('-created_at')

    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            Complaint.objects.create(user=user, text=text)
            return redirect('complaint_list')

    return render(request, 'movies/complaint_list.html', {
        'complaints': complaints,
        'no_complaints': not complaints.exists(),
        'current_user': user  # Передаем пользователя в шаблон
    })

def resolve_complaint(request, complaint_id):
    if 'user_id' not in request.session or not User.objects.get(id=request.session['user_id']).is_superuser:
        return redirect('login')

    complaint = get_object_or_404(Complaint, pk=complaint_id)
    if request.method == 'POST':
        complaint.is_resolved = True
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