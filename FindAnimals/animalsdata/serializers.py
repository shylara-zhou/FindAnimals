from django.utils import timezone
from rest_framework import serializers
from .models import Park, Animal, AnimalStatusUpdate, AnimalComment
from django.contrib.auth import get_user_model
from django.conf import settings


class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'nickname', 'avatar_url']


class ParkSerializer(serializers.ModelSerializer):
    cover_url = serializers.SerializerMethodField()

    class Meta:
        model = Park
        fields = ['id', 'name', 'address', 'lng', 'lat', 'description', 'enabled', 'cover_url', 'created_at', 'updated_at']

    def get_cover_url(self, obj):
        request = self.context.get('request')
        if getattr(obj, 'cover', None):
            if request:
                # 强制使用 HTTPS 协议
                url = request.build_absolute_uri(obj.cover.url)
                return url.replace('http://', 'https://')
            return obj.cover.url
        # If no explicit cover, try use top-viewed approved animal's photo as implicit cover
        top = obj.animals.filter(audit_status='approved', photo__isnull=False).order_by('-views_count').first()
        if top and top.photo:
            if request:
                # 强制使用 HTTPS 协议
                url = request.build_absolute_uri(top.photo.url)
                return url.replace('http://', 'https://')
            return top.photo.url
        # fallback to existing default image
        default_path = settings.MEDIA_URL + 'img/default_animal.jpg'
        if request:
            # 强制使用 HTTPS 协议
            url = request.build_absolute_uri(default_path)
            return url.replace('http://', 'https://')
        return default_path


class AnimalSerializer(serializers.ModelSerializer):
    discoverer = UserSimpleSerializer(read_only=True)
    discoverer_id = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all(), write_only=True, source='discoverer')
    park_name = serializers.CharField(source='park.name', read_only=True)
    photo_url = serializers.SerializerMethodField()
    photo = serializers.ImageField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Animal
        fields = [
            'id', 'name', 'species', 'scientific_name', 'description', 'photo', 'photo_url', 'park', 'park_name',
            'discoverer', 'discoverer_id', 'discovered_at', 'status', 'views_count',
            'audit_status', 'audit_by', 'audit_opinion', 'audit_time', 'created_at', 'updated_at'
        ]
        read_only_fields = ['views_count', 'audit_status', 'audit_by', 'audit_opinion', 'audit_time', 'created_at', 'updated_at']

    def get_photo_url(self, obj):
        request = self.context.get('request')
        if obj.photo:
            if request:
                # 强制使用 HTTPS 协议
                url = request.build_absolute_uri(obj.photo.url)
                return url.replace('http://', 'https://')
            return obj.photo.url
        # fallback to default image under MEDIA_URL
        default_path = settings.MEDIA_URL + 'img/default_animal.jpg'
        if request:
            # 强制使用 HTTPS 协议
            url = request.build_absolute_uri(default_path)
            return url.replace('http://', 'https://')
        return default_path

    def create(self, validated_data):
        validated_data['audit_status'] = 'pending'
        return super().create(validated_data)


class AnimalListPublicSerializer(serializers.ModelSerializer):
    discoverer = UserSimpleSerializer(read_only=True)
    park_name = serializers.CharField(source='park.name', read_only=True)
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Animal
        fields = ['id', 'name', 'species', 'photo_url', 'discoverer', 'discovered_at', 'park_name', 'views_count', 'created_at']

    def get_photo_url(self, obj):
        request = self.context.get('request')
        if obj.photo:
            if request:
                # 强制使用 HTTPS 协议
                url = request.build_absolute_uri(obj.photo.url)
                return url.replace('http://', 'https://')
            return obj.photo.url
        default_path = settings.MEDIA_URL + 'img/default_animal.jpg'
        if request:
            # 强制使用 HTTPS 协议
            url = request.build_absolute_uri(default_path)
            return url.replace('http://', 'https://')
        return default_path


class StatusUpdateSerializer(serializers.ModelSerializer):
    user = UserSimpleSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all(), write_only=True, source='user')
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = AnimalStatusUpdate
        fields = ['id', 'animal', 'user', 'user_id', 'content', 'photo_url', 'created_at']

    def get_photo_url(self, obj):
        request = self.context.get('request')
        if obj.photo:
            if request:
                # 强制使用 HTTPS 协议
                url = request.build_absolute_uri(obj.photo.url)
                return url.replace('http://', 'https://')
            return obj.photo.url
        # status updates may not have default; return None
        return None


class CommentSerializer(serializers.ModelSerializer):
    user = UserSimpleSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all(), write_only=True, source='user')

    class Meta:
        model = AnimalComment
        fields = ['id', 'animal', 'user', 'user_id', 'content', 'parent', 'created_at']

