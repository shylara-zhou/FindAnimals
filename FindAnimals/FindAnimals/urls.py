from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from animalsdata import views
from rest_framework.routers import DefaultRouter
from animalsdata.api import ParkViewSet, AnimalViewSet, StatusUpdateViewSet, CommentViewSet, MyInfoView, MyAnimalsViewSet, WxLoginView, RegisterView, LogoutView, UserLetterView

router = DefaultRouter()
router.register(r'parks', ParkViewSet, basename='park')
router.register(r'animals', AnimalViewSet, basename='animal')
router.register(r'status', StatusUpdateViewSet, basename='status')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'my/animals', MyAnimalsViewSet, basename='my-animals')

urlpatterns = [
    path('', views.hello),
    path('admin/', admin.site.urls),
    path('animals/', views.hello),
    path('allanimalsdata/', views.allanimalsdata),
    path('animals_id/<str:name>/', views.get_animalsdata_by_Name),
    path('addanimals/<str:location>/<str:species>/<str:family>/<str:name>', views.add_animal),
    path('api-auth/', include('rest_framework.urls')),
    path('api/', include(router.urls)),
    path('wx/login/', WxLoginView.as_view()),
    path('wx_login/', WxLoginView.as_view()),
    path('api/register/', RegisterView.as_view()),
    path('api/login/', WxLoginView.as_view()),
    path('api/logout/', LogoutView.as_view()),
    path('api/user-letter/', UserLetterView.as_view()),
    path('load/', views.show_upload),
    path('upload_handle/', views.upload_handle),
]

# 在 DEBUG 模式下，使用 Django 官方推荐的方式提供媒体文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
