# Register your models here.
from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'age', 'budget_preference', 'updated_at']
    search_fields = ['user__username', 'user__email']
    list_filter = ['budget_preference', 'created_at']