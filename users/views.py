from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from movies.models import Movie
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import Liked


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Пароль автоматически хэшируется
            auth_login(request, user)  # Автовход после регистрации
            return redirect('profile')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)  # Стандартный вход Django
            return redirect('profile')
        return render(request, 'users/login.html', {'error': 'Неверные данные'})
    return render(request, 'users/login.html')

def user_logout(request):
    auth_logout(request)  # Стандартный выход
    return redirect('movie_list')

@login_required
def profile(request):
    liked_movies = request.user.liked_movies.all()  # Доступ через related_name
    return render(request, 'users/profile.html', {
        'user': request.user,
        'liked_movies': liked_movies
    })

def edit_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = CustomUserChangeForm(instance=request.user)
    return render(request, 'users/edit_profile.html', {'form': form})


def like_movie(request, movie_id):
    if not request.session.get('user_id'):
        return redirect('login')

    user_id = request.session['user_id']
    user = User.objects.get(id=user_id)

    try:
        movie = Movie.objects.get(id=movie_id)
    except Movie.DoesNotExist:
        return redirect('movie_list')

    if not Liked.objects.filter(user=user, movie=movie).exists():
        Liked.objects.create(user=user, movie=movie)

    return redirect('movie_detail', movie_id=movie_id)