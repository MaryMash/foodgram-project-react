from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CustomTokenCreateView, CustomUserViewSet

router = DefaultRouter()

router.register('users', CustomUserViewSet)

urlpatterns = [
    path('auth/token/login/', CustomTokenCreateView.as_view()),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),

]
