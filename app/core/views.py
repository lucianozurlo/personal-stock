from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


def login_view(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        remember_me = request.POST.get('remember_me')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            if remember_me:
                request.session.set_expiry(1209600)  # 2 semanas
            else:
                request.session.set_expiry(0)  # sesión de navegador
            return redirect('/')
        else:
            return render(request, 'login.html', {'error': 'Email o contraseña incorrectos'})

    return render(request, 'login.html')


@login_required
def home_view(request):
    context = {
        'user': request.user,
        'ps_user_data': {
            'firstName': request.user.first_name or request.user.username,
            'username': request.user.username,
            'email': request.user.email,
        }
    }
    return render(request, 'home.html', context)


def logout_view(request):
    logout(request)
    return redirect('/login/')
