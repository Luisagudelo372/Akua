from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, Review, Place

class UserProfileForm(forms.ModelForm):
    # Campo adicional para el email del User
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'tu@email.com'
        })
    )
    
    # Campos para nombre (first_name y last_name del User)
    first_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre'
        })
    )
    
    last_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellido'
        })
    )
    
    class Meta:
        model = UserProfile
        fields = ['photo', 'age', 'visited_places', 'budget_preference', 'interests', 'biography']
        widgets = {
            'photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Edad',
                'min': '13',
                'max': '120'
            }),
            'visited_places': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Ej: Cartagena, Bogotá, Medellín, Santa Marta...'
            }),
            'budget_preference': forms.Select(attrs={
                'class': 'form-select'
            }),
            'interests': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: conciertos, festivales, naturaleza'
            }),
            'biography': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Cuéntanos un poco sobre ti y tus intereses de viaje...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Prellenar campos del User si existe
        if self.instance and self.instance.pk and self.instance.user:
            self.fields['email'].initial = self.instance.user.email
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name


# ============================================
# FORMS PARA REVIEWS
# ============================================

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['title', 'place', 'qualification', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Paradise Found in Colombia\'s Caribbean Coast'
            }),
            'place': forms.Select(attrs={
                'class': 'form-select'
            }),
            'qualification': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Comparte tu experiencia en este lugar...'
            }),
        }
        labels = {
            'title': 'Título de la Reseña',
            'place': 'Lugar',
            'qualification': 'Calificación',
            'description': 'Tu Experiencia'
        }