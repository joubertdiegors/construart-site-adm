from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile_list')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('accounts:profile_list')
        else:
            context = {'error': 'Usuário ou senha inválidos'}
            return render(request, 'login.html', context)

    return render(request, 'login.html')


@login_required(login_url='login')
def home_view(request):
    return redirect('accounts:profile_list')
