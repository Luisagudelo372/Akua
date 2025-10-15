from django.db import models
import pickle

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

