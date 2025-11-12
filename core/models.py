from django.db import models
import pickle
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify

class TripItem(models.Model):
    PLACE_TYPES = [
        ('event', 'Event'),
        ('restaurant', 'Restaurant'),
        ('hotel', 'Hotel'),
        ('site', 'Tourist Site'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    place_type = models.CharField(max_length=20, choices=PLACE_TYPES)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default='Colombia')

    # 💰 Presupuesto estimado (por persona)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # 📍 Distancia o duración aproximada desde el hospedaje o centro
    distance_km = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    estimated_time = models.TimeField(null=True, blank=True)

    # 🧠 Embedding generado con IA
    embedding = models.BinaryField(null=True, blank=True)

    # 📸 Imagen opcional para mostrar en las cards del frontend
    image = models.ImageField(upload_to='places/', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def set_embedding(self, vector):
        """Convierte y guarda una lista de floats como binario"""
        self.embedding = pickle.dumps(vector)

    def get_embedding(self):
        """Devuelve el vector original"""
        return pickle.loads(self.embedding) if self.embedding else None

    def __str__(self):
        return f"{self.name} ({self.place_type})"


class UserProfile(models.Model):
    BUDGET_CHOICES = [
        ('0-500', '$0 - $500'),
        ('500-1000', '$500 - $1,000'),
        ('1000-2000', '$1,000 - $2,000'),
        ('2000-3000', '$2,000 - $3,000'),
        ('3000-5000', '$3,000 - $5,000'),
        ('5000+', '$5,000+'),
    ]
    
    EVENT_CHOICES = [
        ('conciertos', 'Conciertos'),
        ('festivales', 'Festivales'),
        ('mercados', 'Mercados Locales'),
        ('cultura', 'Cultura'),
        ('naturaleza', 'Naturaleza'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    age = models.PositiveIntegerField(
        blank=True, 
        null=True,
        validators=[MinValueValidator(13), MaxValueValidator(120)]
    )
    visited_places = models.TextField(
        blank=True,
        help_text="Lugares que has visitado (uno por línea o separados por comas.)"
    )
    budget_preference = models.CharField(
        max_length=20,
        choices=BUDGET_CHOICES,
        default='500-1000',
        verbose_name="Preferencia de presupuesto"
    )
    interests = models.CharField(
        max_length=200,
        blank=True,
        help_text="Eventos de interés separados por comas"
    )
    biography = models.TextField(
        max_length=500,
        blank=True,
        verbose_name="Biografía"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Perfil de {self.user.username}"
    
    def get_interests_list(self):
        """Retorna los intereses como lista"""
        if self.interests:
            return [i.strip() for i in self.interests.split(',')]
        return []
    
    def get_visited_places_list(self):
        """Retorna los lugares visitados como lista"""
        if self.visited_places:
            # Intenta separar por líneas o por comas
            places = self.visited_places.replace('\n', ',').split(',')
            return [p.strip() for p in places if p.strip()]
        return []
    
    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuarios"



class Place(models.Model):
    # ID como Primary Key (auto-incremental)
    id = models.AutoField(primary_key=True)
    
    # Nombre del lugar
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="Nombre del Lugar"
    )
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    
    # Foto principal
    photo = models.ImageField(
        upload_to='places_photos/',
        verbose_name="Foto Principal",
        blank=True,
        null=True
    )
    
    # Descripción
    short_description = models.CharField(
        max_length=200,
        verbose_name="Descripción Breve",
        help_text="Descripción corta para las tarjetas"
    )
    
    # Información del modelo de la imagen
    events = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Eventos",
        help_text="Eventos disponibles en el lugar"
    )
    
    restaurants = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Restaurantes",
        help_text="Restaurantes recomendados"
    )
    
    hotels = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Hoteles",
        help_text="Hoteles cercanos"
    )
    
    estimated_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Costo Estimado"
    )
    
    category = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Categoría",
        help_text="Ej: Playa, Montaña, Cultural"
    )
    
    rating_average = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        verbose_name="Calificación Promedio"
    )
    
    # Campos adicionales útiles
    city = models.CharField(max_length=100, blank=True, verbose_name="Ciudad")
    department = models.CharField(max_length=100, blank=True, verbose_name="Departamento")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Lugar"
        verbose_name_plural = "Lugares"
        ordering = ['-rating_average', 'name']

class Category(models.Model):
    """Categorías de lugares (Nature, Culture, Adventure, etc.)"""
    name = models.CharField(max_length=100, verbose_name="Nombre")
    slug = models.SlugField(unique=True)
    
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Review(models.Model):
    """Reseñas de lugares"""
    QUALIFICATION_CHOICES = [
        (1, '1 Estrella'),
        (2, '2 Estrellas'),
        (3, '3 Estrellas'),
        (4, '4 Estrellas'),
        (5, '5 Estrellas'),
    ]
    
    title = models.CharField(
        max_length=200, 
        verbose_name="Título de la Reseña"
    )
    description = models.TextField(verbose_name="Descripción")
    qualification = models.IntegerField(
        choices=QUALIFICATION_CHOICES,
        verbose_name="Calificación"
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='reviews',
        verbose_name="Usuario"
    )
    place = models.ForeignKey(
        Place, 
        on_delete=models.CASCADE, 
        related_name='reviews',
        verbose_name="Lugar"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Reseña"
        verbose_name_plural = "Reseñas"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def get_category(self):
        """Obtiene la categoría del lugar asociado"""
        return self.place.category if self.place else None
    
    def get_time_ago(self):
        """Retorna hace cuánto tiempo se creó la review"""
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        diff = now - self.created_at
        
        if diff < timedelta(minutes=1):
            return "just now"
        elif diff < timedelta(hours=1):
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif diff < timedelta(days=1):
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff < timedelta(days=7):
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff < timedelta(days=30):
            weeks = diff.days // 7
            return f"{weeks} week{'s' if weeks != 1 else ''} ago"
        elif diff < timedelta(days=365):
            months = diff.days // 30
            return f"{months} month{'s' if months != 1 else ''} ago"
        else:
            years = diff.days // 365
            return f"{years} year{'s' if years != 1 else ''} ago"

class Route(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='routes')
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    days = models.IntegerField()
    budget = models.CharField(max_length=50)
    ai_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.city}, {self.country} - {self.days}"

    def get_complete_route_url(self):
        """
        Genera URL de Google Maps:
        1. Tu ubicación actual
        2. Ciudad destino (ej: Montería)
        3. Lugares extraídos de la ruta
        """
        import re
        from urllib.parse import quote

        # Destino principal
        destination = f"{self.city}, {self.country}"

        # Lista para guardar los lugares en orden
        places_ordered = []

        # Dividir la respuesta en líneas
        lines = self.ai_response.split('\n')

        for line in lines:
            # Buscar patrones como: - **Catedral de San Jerónimo**
            matches = re.findall(r'\*\*([^*]+)\*\*', line)

            for match in matches:
                place_clean = match.strip()

                # Palabras clave que NO son lugares
                excluded_keywords = [
                    'día', 'mañana', 'tarde', 'noche', 'costo', 'total', 'presupuesto',
                    'descripción', 'recomendación', 'almuerzo', 'cena', 'desayuno',
                    'actividades', 'entrada', 'aproximado', 'estimado', 'gratuita',
                    'ruta', 'turística', 'personalizada', 'final', 'local',
                    'típica', 'transporte', 'hospedaje', 'zona', 'visita'
                ]

                # Verificar si el texto contiene palabras excluidas
                is_valid_place = True
                place_lower = place_clean.lower()

                for keyword in excluded_keywords:
                    if keyword in place_lower:
                        is_valid_place = False
                        break

                # Filtrar si es muy corto o tiene $ o números al inicio
                if len(place_clean) < 5 or re.match(r'^[\$\d]', place_clean):
                    is_valid_place = False

                # Agregar solo si es válido y no está duplicado
                if is_valid_place and place_clean not in places_ordered:
                    places_ordered.append(place_clean)

        # Tomar máximo 9 lugares
        waypoints = places_ordered[:9]

        # Construir URL
        if waypoints:
            # Codificar waypoints correctamente
            waypoints_list = []
            for place in waypoints:
                # Agregar ciudad para mejor precisión
                place_full = f"{place}, {self.city}, {self.country}"
                waypoints_list.append(quote(place_full))

            waypoints_str = "|".join(waypoints_list)
            destination_encoded = quote(destination)

            # URL correcta de Google Maps
            url = (
                f"https://www.google.com/maps/dir/?api=1"
                f"&destination={destination_encoded}"
                f"&waypoints={waypoints_str}"
                f"&travelmode=driving"
            )
        else:
            # Si no hay waypoints, solo ruta al destino
            destination_encoded = quote(destination)
            url = f"https://www.google.com/maps/dir/?api=1&destination={destination_encoded}&travelmode=driving"

        return url
