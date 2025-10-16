from django.urls import path, include
from . import views 
from django.conf import settings

urlpatterns = [
    path('', views.index, name='index'),  # raíz → index
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('donde-ir/', views.donde_ir, name='donde_ir'),
    path('profile/', views.profile, name='profile'),
    path('reviews/', views.reviews, name='reviews'),
    path("generar_ruta_ai/", views.generar_ruta_ai, name="generar_ruta_ai"),
    path('places/', views.places, name='places'),
    path('places/<slug:slug>/', views.place_detail, name='place_detail'),
]

