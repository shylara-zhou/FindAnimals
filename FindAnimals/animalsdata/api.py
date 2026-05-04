from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.db.models import Count
from rest_framework import viewsets, mixins, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from .models import Park, Animal, AnimalStatusUpdate, AnimalComment
from .serializers import ParkSerializer, AnimalSerializer, AnimalListPublicSerializer, StatusUpdateSerializer, CommentSerializer, UserSimpleSerializer
from django.contrib.auth import get_user_model, authenticate
import json
import urllib.request


def std(data=None, code=200, msg='ok', pagination=None):
    return Response({'code': code, 'msg': msg, 'data': data, 'pagination': pagination})


class ParkViewSet(viewsets.ModelViewSet):
    queryset = Park.objects.all()
    serializer_class = ParkSerializer
    filterset_fields = ['name', 'enabled']
    search_fields = ['name', 'address', 'description']
    ordering_fields = ['created_at', 'updated_at', 'name']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset().filter(enabled=True) if not request.user.is_staff else self.get_queryset()
        page = self.paginate_queryset(qs)
        ser = self.get_serializer(page, many=True)
        
        # 添加未探索的留白区域
        parks_data = ser.data
        
        # 创建未探索区域的虚拟公园对象
        unexplored_park = {
            'id': 'unexplored',
            'name': '未探索的留白区域',
            'description': '这里是尚未探索的区域，等待你的发现和贡献！',
            'cover_url': 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=空白区域%20留白%20简约风格&image_size=landscape_4_3',
            'enabled': True
        }
        
        # 将未探索区域添加到公园列表末尾
        parks_data.append(unexplored_park)
        
        return std(parks_data, pagination=self.get_paginated_response({}).data.get('pagination', None))


class PaginationMetaMixin:
    def _pagination_meta(self):
        page = self.paginator.page.number if hasattr(self, 'paginator') and getattr(self.paginator, 'page', None) else 1
        page_size = self.paginator.get_page_size(self.request) if hasattr(self, 'paginator') else 20
        total = self.paginator.page.paginator.count if hasattr(self, 'paginator') and getattr(self.paginator, 'page', None) else 0
        total_pages = self.paginator.page.paginator.num_pages if hasattr(self, 'paginator') and getattr(self.paginator, 'page', None) else 0
        return {'total': total, 'page': page, 'page_size': page_size, 'total_pages': total_pages}


class RateLimitMixin:
    def check_rate_limit(self, model_class, user, message="请勿频繁提交，请一分钟后再试"):
        one_minute_ago = timezone.now() - timedelta(minutes=1)
        # Check if user is staff/admin, they might need to bypass rate limit for testing/admin purposes
        if user.is_staff:
            return None
        
        last_submission = model_class.objects.filter(
            **{self.get_user_field(model_class): user},
            created_at__gte=one_minute_ago
        ).exists()
        
        if last_submission:
            return std(code=429, msg=message)
        return None

    def get_user_field(self, model_class):
        if model_class == Animal:
            return 'discoverer'
        return 'user'


class AnimalViewSet(PaginationMetaMixin, RateLimitMixin, viewsets.ModelViewSet):
    queryset = Animal.objects.select_related('park', 'discoverer')
    serializer_class = AnimalSerializer
    filterset_fields = ['park', 'audit_status']
    search_fields = ['name', 'scientific_name', 'description']
    ordering_fields = ['created_at', 'views_count', 'discovered_at']

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'search', 'by_park', 'ranking']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action in ['list', 'search', 'by_park', 'ranking']:
            return AnimalListPublicSerializer
        return super().get_serializer_class()

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset().filter(audit_status='approved')
        page = self.paginate_queryset(qs)
        ser = self.get_serializer(page, many=True)
        pagination = self._pagination_meta()
        return std(ser.data, pagination=pagination)

    @action(detail=False, methods=['get'])
    def by_park(self, request):
        park_id = request.query_params.get('park_id')
        ordering = request.query_params.get('ordering')
        qs = self.get_queryset().filter(audit_status='approved')
        if park_id:
            qs = qs.filter(park_id=park_id)
        if ordering in ['created_at', '-created_at', 'views_count', '-views_count']:
            qs = qs.order_by(ordering)
        page = self.paginate_queryset(qs)
        ser = self.get_serializer(page, many=True)
        pagination = self._pagination_meta()
        return std(ser.data, pagination=pagination)

    @action(detail=False, methods=['get'])
    def search(self, request):
        keyword = request.query_params.get('keyword')
        park_id = request.query_params.get('park_id')
        qs = self.get_queryset().filter(audit_status='approved')
        if keyword:
            qs = qs.filter(models.Q(name__icontains=keyword) | models.Q(scientific_name__icontains=keyword))
        if park_id:
            qs = qs.filter(park_id=park_id)
        page = self.paginate_queryset(qs)
        ser = self.get_serializer(page, many=True)
        pagination = self._pagination_meta()
        return std(ser.data, pagination=pagination)

    @action(detail=False, methods=['get'])
    def ranking(self, request):
        sort_type = int(request.query_params.get('sort_type', 1))
        qs = self.get_queryset().filter(audit_status='approved')
        if sort_type == 1:
            qs = qs.order_by('-views_count')
        elif sort_type == 2:
            qs = qs.order_by('-created_at')
        elif sort_type == 3:
            since = timezone.now() - timedelta(days=7)
            qs = qs.annotate(update_freq=Count('status_updates', filter=models.Q(status_updates__created_at__gte=since))).order_by('-update_freq')
        page = self.paginate_queryset(qs)
        ser = self.get_serializer(page, many=True)
        pagination = self._pagination_meta()
        return std(ser.data, pagination=pagination)

    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        Animal.objects.filter(pk=obj.pk).update(views_count=obj.views_count + 1)
        ser = self.get_serializer(obj)
        return std(ser.data)

    def create(self, request, *args, **kwargs):
        limit_resp = self.check_rate_limit(Animal, request.user)
        if limit_resp:
            return limit_resp
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        animal = ser.save()
        # ensure response uses context with request so URLs are absolute
        return std(self.get_serializer(animal).data)

    # pagination meta moved to PaginationMetaMixin


class StatusUpdateViewSet(PaginationMetaMixin, RateLimitMixin, viewsets.ModelViewSet):
    queryset = AnimalStatusUpdate.objects.select_related('animal', 'user')
    serializer_class = StatusUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        limit_resp = self.check_rate_limit(AnimalStatusUpdate, request.user)
        if limit_resp:
            return limit_resp
        return super().create(request, *args, **kwargs)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.method.lower() == 'get':
            return qs.filter(animal__audit_status='approved')
        return qs

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)
        ser = self.get_serializer(page, many=True)
        pagination = self._pagination_meta()
        return std(ser.data, pagination=pagination)


class CommentViewSet(PaginationMetaMixin, RateLimitMixin, viewsets.ModelViewSet):
    queryset = AnimalComment.objects.select_related('animal', 'user')
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['animal']

    def create(self, request, *args, **kwargs):
        limit_resp = self.check_rate_limit(AnimalComment, request.user)
        if limit_resp:
            return limit_resp
        return super().create(request, *args, **kwargs)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        # 读评论不按动物审核状态过滤，并按时间倒序，确保新评论优先显示
        return super().get_queryset().order_by('-created_at')

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)
        ser = self.get_serializer(page, many=True)
        pagination = self._pagination_meta()
        return std(ser.data, pagination=pagination)


class MyInfoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        data = UserSimpleSerializer(user).data
        total = Animal.objects.filter(discoverer=user).count()
        pending = Animal.objects.filter(discoverer=user, audit_status='pending').count()
        approved = Animal.objects.filter(discoverer=user, audit_status='approved').count()
        rejected = Animal.objects.filter(discoverer=user, audit_status='rejected').count()
        return std({'user': data, 'stats': {'total': total, 'pending': pending, 'approved': approved, 'rejected': rejected}})


class MyAnimalsViewSet(PaginationMetaMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = AnimalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Animal.objects.filter(discoverer=self.request.user)
        audit_status = self.request.query_params.get('audit_status')
        if audit_status:
            qs = qs.filter(audit_status=audit_status)
        return qs.order_by('-created_at')

    def list(self, request, *args, **kwargs):
        page = self.paginate_queryset(self.get_queryset())
        ser = self.get_serializer(page, many=True)
        pagination = self._pagination_meta()
        return std(ser.data, pagination=pagination)


class RegisterView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        nickname = request.data.get('nickname')
        phone = request.data.get('phone')
        
        if not username or not password:
            return std(code=400, msg='用户名和密码不能为空')
        
        User = get_user_model()
        if User.objects.filter(username=username).exists():
            return std(code=400, msg='用户名已存在')
        
        # 创建用户
        user = User.objects.create_user(
            username=username,
            password=password,
            nickname=nickname or username,
            phone=phone
        )
        
        # 生成token
        token, _ = Token.objects.get_or_create(user=user)
        
        return std({
            'token': token.key,
            'user_id': user.id,
            'username': user.username,
            'nickname': user.nickname,
            'is_staff': user.is_staff
        })


class WxLoginView(APIView):
    def post(self, request):
        # Support standard login with username/password
        username = request.data.get('username') or request.data.get('mname')
        password = request.data.get('password')
        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                token, _ = Token.objects.get_or_create(user=user)
                return std({'token': token.key, 'user_id': user.id, 'is_staff': user.is_staff})
            else:
                return std(code=400, msg='invalid credentials')

        # Compatibility mode: Login/Register with just mname (if provided and valid)
        mname = request.data.get('mname')
        if mname and mname != 'undefined':
            User = get_user_model()
            user, created = User.objects.get_or_create(username=mname, defaults={'nickname': mname})
            if created:
                user.set_unusable_password()
                user.save()
            token, _ = Token.objects.get_or_create(user=user)
            return std({'token': token.key, 'user_id': user.id, 'is_staff': user.is_staff})

        code = request.data.get('code')
        avatar_url = request.data.get('avatar_url')
        nickname = request.data.get('nickname')
        if not code:
            return std(code=400, msg='code required')
        openid = None
        if settings.WX_USE_STUB or not settings.WX_APPID or not settings.WX_SECRET:
            openid = f'stub_{code}'
        else:
            url = f'https://api.weixin.qq.com/sns/jscode2session?appid={settings.WX_APPID}&secret={settings.WX_SECRET}&js_code={code}&grant_type=authorization_code'
            try:
                with urllib.request.urlopen(url, timeout=5) as resp:
                    data = json.loads(resp.read().decode())
                    openid = data.get('openid')
            except Exception:
                return std(code=500, msg='wechat error')
        if not openid:
            return std(code=400, msg='invalid code')
        User = get_user_model()
        user, _ = User.objects.get_or_create(openid=openid, defaults={'username': openid})
        if avatar_url:
            user.avatar_url = avatar_url
        if nickname:
            user.nickname = nickname
        user.save()
        token, _ = Token.objects.get_or_create(user=user)
        return std({'token': token.key})
    def get(self, request):
        # Support standard login with username/password (GET fallback)
        username = request.query_params.get('username') or request.query_params.get('mname')
        password = request.query_params.get('password')
        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                token, _ = Token.objects.get_or_create(user=user)
                return std({'token': token.key, 'user_id': user.id, 'is_staff': user.is_staff})
            else:
                return std(code=400, msg='invalid credentials')

        # Compatibility mode: Login/Register with just mname (if provided and valid)
        mname = request.query_params.get('mname')
        if mname and mname != 'undefined':
            User = get_user_model()
            user, created = User.objects.get_or_create(username=mname, defaults={'nickname': mname})
            if created:
                user.set_unusable_password()
                user.save()
            token, _ = Token.objects.get_or_create(user=user)
            return std({'token': token.key, 'user_id': user.id, 'is_staff': user.is_staff})

        code = request.query_params.get('code')
        avatar_url = request.query_params.get('avatar_url')
        nickname = request.query_params.get('nickname')
        if not code:
            return std(code=400, msg='code required')
        openid = None
        if settings.WX_USE_STUB or not settings.WX_APPID or not settings.WX_SECRET:
            openid = f'stub_{code}'
        else:
            url = f'https://api.weixin.qq.com/sns/jscode2session?appid={settings.WX_APPID}&secret={settings.WX_SECRET}&js_code={code}&grant_type=authorization_code'
            try:
                with urllib.request.urlopen(url, timeout=5) as resp:
                    data = json.loads(resp.read().decode())
                    openid = data.get('openid')
            except Exception:
                return std(code=500, msg='wechat error')
        if not openid:
            return std(code=400, msg='invalid code')
        User = get_user_model()
        user, _ = User.objects.get_or_create(openid=openid, defaults={'username': openid})
        if avatar_url:
            user.avatar_url = avatar_url
        if nickname:
            user.nickname = nickname
        user.save()
        token, _ = Token.objects.get_or_create(user=user)
        return std({'token': token.key})
