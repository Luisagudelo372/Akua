from django.shortcuts import render, redirect
from django.contrib import messages
from .models import UserProfile
from .forms import UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI
import os
from dotenv import load_dotenv
from .models import UserProfile, Place, Review
from .forms import UserProfileForm, ReviewForm
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from .models import Place

User = get_user_model()

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
    """Vista para listar todas las reviews"""
    reviews_list = Review.objects.select_related(
        'user', 
        'place'
    ).all()
    
    context = {
        'reviews': reviews_list,
    }
    return render(request, 'core/reviews_list.html', context)

@login_required
def edit_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if review.user != request.user:
        messages.error(request, "No tienes permiso para editar esta reseña.")
        return redirect('reviews')

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Reseña actualizada correctamente.")
            return redirect('reviews')
    else:
        form = ReviewForm(instance=review)

    return render(request, 'core/write_review.html', {'form': form, 'editing': True})

@login_required
def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if review.user != request.user:
        messages.error(request, "No tienes permiso para eliminar esta reseña.")
        return redirect('reviews')

    if request.method == 'POST':
        review.delete()
        messages.success(request, "Reseña eliminada.")
        return redirect('reviews')

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

def profile(request):
    # Si no está autenticado, redirigir al login
    if not request.user.is_authenticated:
        messages.info(request, 'Debes iniciar sesión para ver tu perfil.')
        return redirect('login')
    
    # Obtener o crear el perfil del usuario
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        
        if form.is_valid():
            # Guardar el perfil
            profile = form.save()
            
            # Actualizar datos del User (email y nombre)
            user = request.user
            user.email = form.cleaned_data.get('email', '')
            user.first_name = form.cleaned_data.get('first_name', '')
            user.last_name = form.cleaned_data.get('last_name', '')
            user.save()
            
            messages.success(request, '¡Perfil actualizado exitosamente!')
            return redirect('profile')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = UserProfileForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile,
    }
    return render(request, 'core/profile.html', context)

def public_profile(request, username):
    """
    Public profile page for a user.
    Shows name, avatar, interests, visited places and biography (read-only).
    """
    user_obj = get_object_or_404(User, username=username)
    # try to access a related profile object if present
    profile = getattr(user_obj, 'profile', None)
    # you can also fetch related data like reviews if needed
    user_reviews = getattr(user_obj, 'review_set', None)
    context = {
        'user_obj': user_obj,
        'profile': profile,
        # optionally show number of reviews or a list:
        # 'reviews': user_obj.review_set.all()[:10],
    }
    return render(request, 'core/public_profile.html', context)

def places(request):
    """Vista de listado de lugares"""
    places_list = Place.objects.all()
    
    context = {
        'places': places_list
    }
    return render(request, 'core/places.html', context)

def place_detail(request, slug):
    """Vista de detalle de un lugar específico"""
    place = get_object_or_404(Place, slug=slug)
    
    context = {
        'place': place
    }
    return render(request, 'core/place_detail.html', context)

@login_required
def write_review(request):
    """Vista para crear una nueva review"""
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.save()
            messages.success(request, '¡Tu reseña ha sido publicada exitosamente!')
            return redirect('reviews')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = ReviewForm()
    
    context = {
        'form': form,
    }
    return render(request, 'core/write_review.html', context)