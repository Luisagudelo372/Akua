# Register your models here.
from django.contrib import admin
from .models import UserProfile, Place

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