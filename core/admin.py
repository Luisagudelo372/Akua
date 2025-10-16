# Register your models here.
from django.contrib import admin
from .models import UserProfile, Place, Category, Review

@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'department', 'category', 'rating_average', 'estimated_cost']
    list_filter = ['category', 'city', 'department']
    search_fields = ['name', 'city', 'short_description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['rating_average']
    ordering = ['-rating_average', 'name']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'age', 'budget_preference', 'updated_at']
    search_fields = ['user__username', 'user__email']
    list_filter = ['budget_preference', 'created_at']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'place', 'qualification', 'created_at']
    list_filter = ['qualification', 'created_at', 'place__category']
    search_fields = ['title', 'description', 'user__username', 'place__name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    list_per_page = 20
    
    # Organizar campos en el formulario de edición
    fieldsets = (
        ('Información Básica', {
            'fields': ('title', 'user', 'place')
        }),
        ('Contenido', {
            'fields': ('qualification', 'description')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )