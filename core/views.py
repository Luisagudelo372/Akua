from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


def index(request):
    return render(request, "core/index.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            context = {'error_message': 'Nombre de usuario o contraseña incorrectos.'}
            return render(request, 'core/login.html', context)

    return render(request, 'core/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def register_view(request):
    return render(request, "core/register.html")



def dashboard(request):
    return render(request, "core/dashboard.html")



def donde_ir(request):
    tags = [
        "Adventure","Culture","Food","Nature","History","Photography",
        "Beach","Mountains","Coffee","Wildlife","Architecture","Nightlife"
    ]
    return render(request, "core/donde_ir.html", {"tags": tags})



def profile(request):
    return render(request, "core/profile.html")



def reviews(request):
    data = [
        ("Paradise Found in Colombia's Caribbean Coast", "Tayrona National Park", "Santa Marta, Magdalena", 5),
        ("Authentic Coffee Culture Immersion", "Coffee Farm Experience", "Salento, Quindío", 4),
    ]
    return render(request, "core/reviews.html", {"reviews": data})
