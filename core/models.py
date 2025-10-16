from django.db import models
import pickle
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

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
