from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import UserProfile, Place, Review, Route
from .forms import UserProfileForm, ReviewForm
from django.contrib.auth import authenticate, login, logout, get_user_model
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


# 🆕 FUNCIÓN AUXILIAR PARA ACTUALIZAR RATING (INCLUYE RATING INICIAL)
def update_place_rating(place):
    """
    Actualiza el rating promedio de un lugar.
    Incluye el rating inicial (ficticio) en el cálculo.
    El rating inicial cuenta como 1 voto.
    """
    reviews = place.reviews.all()
    
    if reviews.exists():
        # Sumar todas las calificaciones de reviews reales
        total_sum = sum([r.qualification for r in reviews])
        total_count = reviews.count()
        
        # SI el lugar tiene un rating inicial (ficticio), incluirlo como 1 voto
        if place.rating_average > 0:
            total_sum += float(place.rating_average)
            total_count += 1
        
        # Calcular nuevo promedio
        new_average = total_sum / total_count
        place.rating_average = round(new_average, 2)
    
    place.save()
    return place.rating_average


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
            
            # 🆕 ACTUALIZAR RATING (INCLUYE RATING INICIAL)
            new_rating = update_place_rating(review.place)
            
            messages.success(request, f'¡Tu reseña ha sido publicada! Nuevo rating: {new_rating}/5.0 ⭐')
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
            
            # 🆕 ACTUALIZAR RATING (INCLUYE RATING INICIAL)
            new_rating = update_place_rating(review.place)
            
            messages.success(request, f"Reseña actualizada correctamente. Nuevo rating: {new_rating}/5.0 ⭐")
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
        
        # 🆕 ACTUALIZAR RATING (INCLUYE RATING INICIAL)
        new_rating = update_place_rating(place)
        
        messages.success(request, f"Reseña eliminada. Nuevo rating: {new_rating}/5.0 ⭐")
        return redirect('reviews')


@login_required
def generar_ruta_ai(request):
    """Toma las opciones del usuario y genera una respuesta de IA."""
    if request.method == "POST":
        try:
            ciudad = request.POST.get("ciudad")
            pais = request.POST.get("pais")
            presupuesto = request.POST.get("presupuesto")
            dias = request.POST.get("dias")
            intereses = request.POST.getlist("intereses")
            evento = request.POST.get("evento")
            barrio = request.POST.get("barrio")

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

            SERPAPI_KEY = os.getenv("SERPAPI_KEY")
            if not SERPAPI_KEY:
                return JsonResponse({"error": "Falta la clave SERPAPI_KEY en el archivo .env"}, status=500)

            search = GoogleSearch({
                "q": f"turismo en {ciudad} {pais} {evento} {', '.join(intereses)} 2025 actividades lugares recomendados",
                "api_key": SERPAPI_KEY,
                "num": 5
            })
            results = search.get_dict()

            resumen_web = ""
            if "organic_results" in results:
                for r in results["organic_results"][:5]:
                    title = r.get("title", "")
                    snippet = r.get("snippet", "")
                    link = r.get("link", "")
                    resumen_web += f"\n- {title}: {snippet}\n{link}\n"

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
                max_tokens=2000,
                temperature=0.7
            )

            resultado = response.choices[0].message.content

            Route.objects.create(
                user=request.user,
                city=ciudad,
                country=pais,
                days=int(dias),
                budget=presupuesto,
                ai_response=resultado
            )

            return JsonResponse({"respuesta": resultado})

        except Exception as e:
            print(f"Error en generar_ruta_ai: {str(e)}")
            return JsonResponse({
                "error": f"No se pudo generar la ruta: {str(e)}"
            }, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)


def places(request):
    # collect selected categories (supports repeated ?category=A&category=B and comma lists)
    selected = request.GET.getlist('category') or []
    if not selected and request.GET.get('category'):
        selected = [s.strip() for s in request.GET.get('category').split(',') if s.strip()]

    # remove duplicates while preserving order (avoid duplicated pills)
    from collections import OrderedDict
    selected = list(OrderedDict.fromkeys([s for s in selected if s]))

    qs = Place.objects.all()

    # search bar: filter by text query
    search_query = request.GET.get('q', '').strip()
    if search_query:
        qs = qs.filter(
            Q(name__icontains=search_query) |
            Q(short_description__icontains=search_query) |
            Q(city__icontains=search_query) |
            Q(department__icontains=search_query)
    )


    # detect whether Place has a ManyToManyField named 'categories'
    has_m2m = False
    try:
        Place._meta.get_field('categories')
        has_m2m = True
    except Exception:
        has_m2m = False

    if selected:
        if has_m2m:
            # require place to have at least all selected categories (AND)
            qs = qs.annotate(
                _match_count=Count('categories', filter=Q(categories__name__in=selected), distinct=True)
            ).filter(_match_count=len(selected))
        else:
            # assume categories are in a comma-separated 'category' text field; require each to appear (AND)
            for cat in selected:
                qs = qs.filter(category__icontains=cat)

    # build list of available categories for the filter UI
    if has_m2m:
        Category = Place._meta.get_field('categories').related_model
        categories_list = list(Category.objects.values_list('name', flat=True).distinct())
    else:
        import re

        def split_raw_categories(raw):
            """
            Separa una cadena de categorías tipo:
            'Naturaleza / Aventura, Cultura & Gastronomía'
            en ['Naturaleza', 'Aventura', 'Cultura', 'Gastronomía']
            """
            # Separadores típicos: coma, slash, ampersand, ' y '
            parts = re.split(r'[,/&]| y ', raw, flags=re.IGNORECASE)
            return [p.strip() for p in parts if p.strip()]

        cats = set()
        for raw in Place.objects.values_list('category', flat=True).distinct():
            if not raw:
                continue
            for p in split_raw_categories(raw):
                cats.add(p)

        categories_list = sorted(cats)

    # pass tuples (name, is_selected) to template to avoid fragile template comparisons
    categories = [(c, c in selected) for c in categories_list]

    context = {
        'places': qs,
        'categories': categories,
        'selected_category': selected,  # list (truthy if any selected)
        'search_query': search_query,
    }
    return render(request, 'core/places.html', context)


def place_detail(request, slug):
    """Vista de detalle de un lugar específico"""
    place = get_object_or_404(Place, slug=slug)
    
    context = {
        'place': place
    }
    return render(request, 'core/place_detail.html', context)