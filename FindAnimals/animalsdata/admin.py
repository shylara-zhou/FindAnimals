from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Animals, Park, Animal, AnimalStatusUpdate, AnimalComment
@admin.register(Animals)
class LegacyAnimalsAdmin(admin.ModelAdmin):
    list_display = ('animal_Id', 'animal_Name', 'animal_Species', 'animal_Family')
@admin.register(Park)
class ParkAdmin(admin.ModelAdmin):
    list_display = ('name', 'enabled', 'created_at')
    list_filter = ('enabled',)
    search_fields = ('name', 'address')
@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ('name', 'park', 'discoverer', 'audit_status', 'views_count', 'created_at')
    list_filter = ('audit_status', 'park')
    search_fields = ('name', 'scientific_name')
    readonly_fields = ('views_count',)
@admin.register(AnimalStatusUpdate)
class AnimalStatusUpdateAdmin(admin.ModelAdmin):
    list_display = ('animal', 'user', 'created_at')
    search_fields = ('content',)
@admin.register(AnimalComment)
class AnimalCommentAdmin(admin.ModelAdmin):
    list_display = ('animal', 'user', 'created_at')
    search_fields = ('content',)
