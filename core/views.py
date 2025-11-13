from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import UserProfile, Place, Review, Route
from .forms import UserProfileForm, ReviewForm
from django.contrib.auth import authenticate, login, logout, get_user_model  # ← AGREGAR get_user_model aquí
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI
import os
from dotenv import load_dotenv
from django.db.models import Count, Q, Avg
from serpapi import GoogleSearch
import re

User = get_user_model()

# Cargar variables desde apikey.env
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'openAI.env')
load_dotenv(dotenv_path)

# Inicializar cliente de OpenAI con la API key del archivo .env
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


def index(request):
    """Vista principal - Home con lugares top"""
    # Obtener los 6 lugares mejor calificados
    top_places = Place.objects.all().order_by('-rating_average', 'name')[:6]
    
    context = {
        'top_places': top_places,
    }
    return render(request, "core/index.html", context)


def login_view(request): 
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Intentar autenticar con username
        user = authenticate(request, username=username, password=password)
        
        # Si no funciona, intentar con email
        if user is None:
            try:
                user_obj = User.objects.get(email=username)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
            return render(request, 'core/login.html')

    return render(request, 'core/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente')
    return redirect('login')


def register_view(request):
    if request.method == 'POST':
        # Obtener datos del formulario
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        # Validaciones
        if password1 != password2:
            messages.error(request, 'Las contraseñas no coinciden')
            return render(request, 'core/register.html')
        
        if len(password1) < 8:
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres')
            return render(request, 'core/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya existe')
            return render(request, 'core/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'El email ya está registrado')
            return render(request, 'core/register.html')
        
        # Crear usuario
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name
        )
        
        # Crear perfil automáticamente
        UserProfile.objects.create(user=user)
        
        # Iniciar sesión automáticamente
        login(request, user)
        
        messages.success(request, '¡Cuenta creada exitosamente! Completa tu perfil para empezar.')
        return redirect('profile')
    
    return render(request, "core/register.html")


@login_required
def dashboard(request):
    # Obtener rutas generadas del usuario
    routes = Route.objects.filter(user=request.user)[:5]
    
    # Obtener lugares visitados
    profile = getattr(request.user, 'profile', None)
    visited_from_profile = []
    
    if profile and profile.visited_places:
        visited_from_profile = [
            place.strip() 
            for place in profile.visited_places.split(',') 
            if place.strip()
        ]
    
    # Obtener lugares de las reviews
    reviewed_places = Review.objects.filter(user=request.user).values_list('place__name', flat=True).distinct()
    
    # Combinar y eliminar duplicados
    all_visited = list(set(visited_from_profile + list(reviewed_places)))
    
    context = {
        'routes': routes,
        'visited_places': all_visited[:10],
    }
    return render(request, 'core/dashboard.html', context)


def donde_ir(request):
    """Renderiza la página principal de búsqueda."""
    tags = [
        "Naturaleza", "Aventura", "Cultura", "Gastronomía", "Vida nocturna",
        "Relax", "Historia", "Deportes", "Arte", "Compras", "Familiar"
    ]
    return render(request, "core/donde_ir.html", {"tags": tags})


@login_required
def profile(request):
    # Obtener o crear el perfil del usuario
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        
        if form.is_valid():
            # Guardar el perfil
            profile = form.save()
            
            # Actualizar datos del User
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
    """Vista del perfil público de un usuario"""
    user_obj = get_object_or_404(User, username=username)
    profile = getattr(user_obj, 'profile', None)
    
    context = {
        'user_obj': user_obj,
        'profile': profile,
    }
    return render(request, 'core/public_profile.html', context)


def reviews(request):
    """Vista para listar todas las reviews"""
    reviews_list = Review.objects.select_related('user', 'place').all()
    
    context = {
        'reviews': reviews_list,
    }
    return render(request, 'core/reviews_list.html', context)


@login_required
def write_review(request):
    """Vista para crear una nueva review"""
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.save()
            
            # Actualizar rating promedio del lugar
            place = review.place
            avg_rating = place.reviews.aggregate(Avg('qualification'))['qualification__avg']
            place.rating_average = round(avg_rating, 2) if avg_rating else 0
            place.save()
            
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
            
            # Actualizar rating promedio
            place = review.place
            avg_rating = place.reviews.aggregate(Avg('qualification'))['qualification__avg']
            place.rating_average = round(avg_rating, 2) if avg_rating else 0
            place.save()
            
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
        place = review.place
        review.delete()
        
        # Actualizar rating promedio
        avg_rating = place.reviews.aggregate(Avg('qualification'))['qualification__avg']
        place.rating_average = round(avg_rating, 2) if avg_rating else 0
        place.save()
        
        messages.success(request, "Reseña eliminada.")
        return redirect('reviews')


def generar_ruta_ai(request):
    """Toma las opciones del usuario y genera una respuesta de IA."""
    if request.method == "POST":
        ciudad = request.POST.get("ciudad")
        pais = request.POST.get("pais")
        presupuesto = request.POST.get("presupuesto")
        dias = request.POST.get("dias")
        intereses = request.POST.getlist("intereses")
        evento = request.POST.get("evento")
        barrio = request.POST.get("barrio")

        # Crear prompt con la información del usuario
        prompt_usuario = (
            f"Genera una ruta turística personalizada en {ciudad}, {pais}, "
            f"para {dias} días, con un presupuesto aproximado de {presupuesto} por persona cada día. "
            f"El viajero está interesado en eventos tipo {evento}. "
            f"El hospedaje está en la zona {barrio}. "
            f"Incluye actividades, costos estimados y lugares cercanos relevantes a mi zona de hospedaje." 
            f"Necesito que devuelvas un texto conciso y completo con la información solicitada. " 
            f"Separa los días de forma visible en la respuesta, y devuelve una propuesta para cada uno de los {dias} dias"
            f"y termina siempre con una recomendación final o conclusión."
        )

        # Buscar información reciente en la web con SerpAPI
        SERPAPI_KEY = os.getenv("SERPAPI_KEY")  # ← la clave estará en tu openAI.env
        if not SERPAPI_KEY:
            return JsonResponse({"error": "Falta la clave SERPAPI_KEY en el archivo .env"}, status=500)

        query = (
            f"sitios turísticos, actividades y planes en {ciudad}, {pais} "
            f"relacionados con {evento} y {', '.join(intereses)} "
            f"con precios por persona, direcciones y recomendaciones actualizadas 2025"
        )

        params = {
            "engine": "google",
            "q": query,
            "location": f"{ciudad}, {pais}",
            "hl": "es",                        # Prioriza resultados en español
            "gl": "co",                        # Geolocalización (ajústalo según el país)
            "num": 15,                         # Máximo de resultados relevantes
            "safe": "active",                  # Evita resultados inapropiados
            "api_key": SERPAPI_KEY
        }

        search = GoogleSearch(params)
        results = search.get_dict()

        resumen_web = ""
        fuentes = []
        if "organic_results" in results:
                for r in results["organic_results"][:5]:
                    title = r.get("title", "")
                    snippet = r.get("snippet", "")
                    link = r.get("link", "")
                    resumen_web += f"\n- {title}: {snippet}\n{link}\n"
                    fuentes.append(link)

        prompt_final = (
                "Usa la siguiente información web reciente para construir una respuesta turística completa:\n"
                f"{resumen_web}\n\n"
                f"Solicitud del usuario:\n{prompt_usuario}"
            )

        response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Eres un asistente experto en turismo colombiano."},
                    {"role": "user", "content": prompt_final},
                ],
                max_tokens=10000,
                temperature=0.7
            )

        resultado = response.choices[0].message.content

        return JsonResponse({"respuesta": resultado})

    return JsonResponse({"error": "Método no permitido"}, status=405)


def places(request):
    selected = request.GET.getlist('category') or []
    if not selected and request.GET.get('category'):
        selected = [s.strip() for s in request.GET.get('category').split(',') if s.strip()]

    from collections import OrderedDict
    selected = list(OrderedDict.fromkeys([s for s in selected if s]))

    qs = Place.objects.all()

    has_m2m = False
    try:
        Place._meta.get_field('categories')
        has_m2m = True
    except Exception:
        has_m2m = False

    if selected:
        if has_m2m:
            qs = qs.annotate(
                _match_count=Count('categories', filter=Q(categories__name__in=selected), distinct=True)
            ).filter(_match_count=len(selected))
        else:
            for cat in selected:
                qs = qs.filter(category__icontains=cat)

    if has_m2m:
        Category = Place._meta.get_field('categories').related_model
        categories_list = list(Category.objects.values_list('name', flat=True).distinct())
    else:
        cats = set()
        for raw in Place.objects.values_list('category', flat=True).distinct():
            if not raw:
                continue
            for p in [x.strip() for x in raw.split(',')]:
                if p:
                    cats.add(p)
        categories_list = sorted(cats)

    categories = [(c, c in selected) for c in categories_list]

    context = {
        'places': qs,
        'categories': categories,
        'selected_category': selected,
    }
    return render(request, 'core/places.html', context)


def place_detail(request, slug):
    """Vista de detalle de un lugar específico"""
    place = get_object_or_404(Place, slug=slug)
    
    context = {
        'place': place
    }
    return render(request, 'core/place_detail.html', context)