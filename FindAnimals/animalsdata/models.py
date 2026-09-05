from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import datetime

# Create your models here.
from django.db import models

# Create your models here.
class Animals(models.Model):
    animal_Id = models.CharField(max_length=32)
    animal_Location = models.CharField(max_length=32)
    animal_Befinded_Date = models.CharField(max_length=32)
    animal_chuqu_Date = models.CharField(max_length=32)
    #time = models.CharField(max_length=32)
    animal_Species = models.CharField(max_length=32)
    animal_Family  = models.CharField(max_length=32)
    animal_Name  = models.CharField(max_length=32)
    animal_Pic=models.ImageField(upload_to='img',null=True)


def _date_path(prefix):
    now = datetime.now()
    return f'{prefix}/{now.year:04d}/{now.month:02d}/{now.day:02d}/'


def _upload_animal_photo(instance, filename):
    return _date_path('animal_photos') + filename


def _upload_status_photo(instance, filename):
    return _date_path('status_photos') + filename


def _upload_park_cover(instance, filename):
    return _date_path('park_covers') + filename

def _upload_comment_photo(instance, filename):
    return _date_path('comment_photos') + filename

def _validate_image_size(file):
    if file and hasattr(file, 'size'):
        if file.size > 5 * 1024 * 1024:
            raise ValidationError('image too large')


class Park(models.Model):
    name = models.CharField(max_length=64)
    address = models.CharField(max_length=256, blank=True)
    lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    description = models.TextField(blank=True)
    cover = models.ImageField(upload_to=_upload_park_cover, validators=[_validate_image_size], null=True, blank=True)
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Animal(models.Model):
    name = models.CharField(max_length=64, unique=True)
    species = models.CharField(max_length=64, default='Unknown')
    scientific_name = models.CharField(max_length=128, blank=True)
    description = models.TextField(blank=True)
    photo = models.ImageField(upload_to=_upload_animal_photo, validators=[_validate_image_size], null=True, blank=True)
    park = models.ForeignKey(Park, on_delete=models.CASCADE, related_name='animals')
    discoverer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='discovered_animals')
    discovered_at = models.DateTimeField()
    status = models.CharField(max_length=32, default='pending')
    views_count = models.PositiveIntegerField(default=0)
    audit_status = models.CharField(max_length=16, default='pending')
    audit_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='audited_animals')
    audit_opinion = models.TextField(blank=True)
    audit_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class AnimalStatusUpdate(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='status_updates')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='animal_updates')
    content = models.TextField(blank=True)
    photo = models.ImageField(upload_to=_upload_status_photo, validators=[_validate_image_size], null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class AnimalComment(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='animal_comments')
    content = models.TextField()
    photo = models.ImageField(upload_to=_upload_comment_photo, validators=[_validate_image_size], null=True, blank=True)
    photo_audit_status = models.CharField(max_length=16, default='approved')
    photo_audit_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='audited_comment_photos')
    photo_audit_opinion = models.TextField(blank=True)
    photo_audit_time = models.DateTimeField(null=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
