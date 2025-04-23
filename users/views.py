from django.shortcuts import render, redirect

from movies.models import Movie, Liked
from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        login = request.POST['login']
        password = request.POST['password']
        try:
            user = User.objects.get(login=login, password=password)
            request.session['user_id'] = user.id
            return redirect('profile')
        except User.DoesNotExist:
            return render(request, 'users/login.html', {'error': 'Invalid login or password'})
    return render(request, 'users/login.html')

def user_logout(request):
    if 'user_id' in request.session:
        del request.session['user_id']
    return redirect('movie_list')

def profile(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = User.objects.get(id=user_id)
    liked_movies = Liked.objects.filter(user=user).select_related('movie')
    return render(request, 'users/profile.html', {'user': user, 'liked_movies': liked_movies})


def edit_profile(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = CustomUserChangeForm(instance=user)

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