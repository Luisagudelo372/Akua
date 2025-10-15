from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI
import os
from dotenv import load_dotenv

# Cargar variables desde apikey.env
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'openAI.env')
load_dotenv(dotenv_path)


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
    """Renderiza la página principal de búsqueda."""
    return render(request, "core/donde_ir.html")


def profile(request):
    return render(request, "core/profile.html")



def reviews(request):
    data = [
        ("Paradise Found in Colombia's Caribbean Coast", "Tayrona National Park", "Santa Marta, Magdalena", 5),
        ("Authentic Coffee Culture Immersion", "Coffee Farm Experience", "Salento, Quindío", 4),
    ]
    return render(request, "core/reviews.html", {"reviews": data})

# Inicializar cliente de OpenAI con la API key del archivo .env
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def generar_ruta_ai(request):
    """Toma las opciones del usuario y genera una respuesta de IA."""
    if request.method == "POST":
        # Obtener datos enviados por el usuario
        ciudad = request.POST.get("ciudad")
        pais = request.POST.get("pais")
        presupuesto = request.POST.get("presupuesto")
        dias = request.POST.get("dias")
        intereses = request.POST.getlist("intereses")
        evento = request.POST.get("evento")
        barrio = request.POST.get("barrio")

        # Crear prompt con la información del usuario
        prompt = (
            f"Genera una ruta turística personalizada en {ciudad}, {pais}, "
            f"para {dias} días, con un presupuesto aproximado de {presupuesto} por persona. "
            f"El viajero está interesado en {', '.join(intereses)} y eventos tipo {evento}. "
            f"El hospedaje está en la zona {barrio}. "
            f"Incluye actividades, costos estimados y lugares cercanos relevantes a mi zona de hospedaje."
        )

        # Llamar al modelo de OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Eres un asistente experto en turismo colombiano."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=500,
            temperature=0.8
        )

        # Extraer texto generado
        resultado = response.choices[0].message.content

        return JsonResponse({"respuesta": resultado})

    return JsonResponse({"error": "Método no permitido"}, status=405)