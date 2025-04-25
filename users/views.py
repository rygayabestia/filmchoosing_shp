from django.contrib import messages  # Исправленный импорт
from django.shortcuts import render, redirect, get_object_or_404

from movies.models import Movie, Liked
from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm


def register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        login = request.POST.get('login')
        password = request.POST.get('password')

        try:
            if User.objects.filter(login=login).exists():
                return render(request, 'users/register.html', {'error': 'Пользователь с таким логином уже существует'})

            user = User.objects.create_user(login=login, password=password, name=name)
            return redirect('login')
        except Exception as e:
            return render(request, 'users/register.html', {'error': 'Ошибка при регистрации'})
    return render(request, 'users/register.html')

def user_login(request):
    if request.method == 'POST':
        login = request.POST.get('login')
        password = request.POST.get('password')
        try:
            user = User.objects.get(login=login)
            if user.check_password(password):
                request.session['user_id'] = user.id
                request.session['user_login'] = user.login
                return redirect('movie_list')
            else:
                return render(request, 'users/login.html', {'error': 'Неверный логин или пароль'})
        except User.DoesNotExist:
            return render(request, 'users/login.html', {'error': 'Неверный логин или пароль'})
    return render(request, 'users/login.html')

def user_logout(request):
    if 'user_id' in request.session:
        del request.session['user_id']
    return redirect('movie_list')

def profile(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    try:
        user = User.objects.get(id=user_id)
        liked_movies = Liked.objects.filter(user=user).select_related('movie')
        return render(request, 'users/profile.html', {
            'user': user,
            'liked_movies': liked_movies
        })
    except User.DoesNotExist:
        return redirect('login')

def like_movie(request, movie_id):
    if not request.session.get('user_id'):
        return redirect('login')

    user_id = request.session['user_id']
    user = User.objects.get(id=user_id)
    movie = get_object_or_404(Movie, id=movie_id)

    try:
        liked = Liked.objects.get(user=user, movie=movie)
        liked.delete()
        messages.success(request, "Фильм удален из избранного")
    except Liked.DoesNotExist:
        Liked.objects.create(user=user, movie=movie)
        messages.success(request, "Фильм добавлен в избранное")

    return redirect('movie_detail', movie_id=movie_id)

def edit_profile(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('login')

    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            password = request.POST.get('password')
            if password:
                user.set_password(password)
            form.save()
            messages.success(request, "Профиль успешно обновлен")
            return redirect('profile')
    else:
        form = CustomUserChangeForm(instance=user)

    return render(request, 'users/edit_profile.html', {'form': form})