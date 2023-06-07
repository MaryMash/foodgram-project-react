from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CustomUserViewSet, IgredientViewSet, RecipeViewSet,
                    TagViewSet, TestView)

router = DefaultRouter()

router.register('users', CustomUserViewSet)
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)
router.register('ingredients', IgredientViewSet)
router.register('test', TestView)

urlpatterns = [
    path('', include(router.urls)),
    # path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),

]
