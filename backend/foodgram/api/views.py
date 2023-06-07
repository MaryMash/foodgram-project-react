from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import SetPasswordSerializer
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from recipes.models import Ingredient, Recipe, Tag, RecipeIngredient
from users.models import CustomUser

from .filters import RecipeFilter
from .paginators import CustomPagination
from .permissions import AuthorOrReadOnly
from .serializers import (CustomUserCreateSerializer, CustomUserSerializer,
                          IngredientSerializer, RecipeCreateSerializer,
                          RecipeSerializer, TagSerializer, CreateRecipeIngredientSerializer)


class TestView(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [AllowAny]
    serializer_class = CreateRecipeIngredientSerializer


class CustomUserViewSet(viewsets.ModelViewSet):
    """Получение данных о пользователях, изменение пароля"""
    queryset = CustomUser.objects.all()
    pagination_class = CustomPagination
    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.action == 'retrieve':
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return CustomUserSerializer
        else:
            return CustomUserCreateSerializer

    @action(methods=['get'], detail=False,
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        user = request.user
        if user.is_authenticated:
            serializer = self.get_serializer(user,
                                             context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            {"detail": "Authentication credentials were not provided."},
            status=status.HTTP_401_UNAUTHORIZED)

    @action(methods=['post'], detail=False,
            permission_classes=(IsAuthenticated,))
    def set_password(self, request):
        serializer = SetPasswordSerializer(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)

        self.request.user.set_password(serializer.data["new_password"])
        self.request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        else:
            return RecipeCreateSerializer

    def get_permissions(self):
        if self.action in ('update', 'partial_update', 'destroy'):
            self.permission_classes = [AuthorOrReadOnly]
        return super().get_permissions()


class IgredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
