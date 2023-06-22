from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import SetPasswordSerializer
from recipes.models import (Favourite, Ingredient, Recipe,
                            ShoppingList, Tag)
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from users.models import CustomUser, Subscription

from .constants import TRUE_FILTER
from .filters import RecipeFilter
from .paginators import CustomPagination
from .permissions import AuthorOrReadOnly
from .serializers import (CustomUserCreateSerializer, CustomUserSerializer,
                          IngredientSerializer, RecipeCreateSerializer,
                          RecipeSerializer, RecipeShoppingFavouriteSerializer,
                          SubscriptionsSerializer, TagSerializer)


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
            serializer = CustomUserSerializer(user,
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

    @action(methods=['get'], detail=False,
            permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        subscriptions = CustomUser.objects.filter(
            recipe_author__user=request.user)
        page = self.paginate_queryset(subscriptions)
        if page is not None:
            serializer = SubscriptionsSerializer(subscriptions, many=True,
                                                 context={'request': request})
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True,
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, *args, **kwargs):
        author = get_object_or_404(CustomUser, id=kwargs['pk'])
        if Subscription.objects.filter(user=request.user,
                                       author=author).exists():
            return Response({'errors': 'Подписка уже оформлена'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = SubscriptionsSerializer(author, data=request.data,
                                             context={'request': request})
        if serializer.is_valid():
            Subscription.objects.create(user=request.user, author=author)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, *args, **kwargs):
        author = get_object_or_404(CustomUser, id=kwargs['pk'])
        if Subscription.objects.filter(user=request.user,
                                       author=author).exists():
            Subscription.objects.filter(user=request.user,
                                        author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Вы не подписаны на этого автора'},
                        status=status.HTTP_400_BAD_REQUEST)


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

    def get_queryset(self):
        queryset = Recipe.objects.all()
        if self.request.user.is_anonymous:
            return queryset
        is_favorited = self.request.query_params.get('is_favorited')
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart')
        if is_favorited == TRUE_FILTER:
            queryset = queryset.filter(favourites__user=self.request.user)
        if is_in_shopping_cart == TRUE_FILTER:
            queryset = queryset.filter(list__user=self.request.user)
        return queryset

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

    @action(methods=['post'], detail=True,
            permission_classes=(IsAuthenticated,)
            )
    def shopping_cart(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        if ShoppingList.objects.filter(recipe=recipe,
                                       user=request.user).exists():
            return Response(
                {'errors': 'Рецепт уже добавлен в список покупок'},
                status=status.HTTP_400_BAD_REQUEST)
        serializer = RecipeShoppingFavouriteSerializer(
            recipe, data=request.data, context={'request': request})
        if serializer.is_valid():
            ShoppingList.objects.create(recipe=recipe, user=request.user)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        if ShoppingList.objects.filter(recipe=recipe,
                                       user=request.user).exists():
            ShoppingList.objects.filter(recipe=recipe,
                                        user=request.user).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Объекта не существует'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=False,
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        ingredients = (Ingredient.objects
                       .filter(recipe__recipe__list__user=request.user)
                       .values('name').annotate(total=Sum('recipe__amount'))
                       .values_list('name', 'measurement_unit', 'total'))

        data = []
        for ingredient in ingredients:
            data.append('{} ({}) - {}'.format(*ingredient))

        response = HttpResponse('\n'.join(data),
                                content_type='text/plain; charset=UTF-8')
        response['Content-Disposition'] = (
            f'attachment; filename={"Список покупок"}')
        return response

    @action(methods=['post'], detail=True,
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        if Favourite.objects.filter(recipe=recipe,
                                    user=request.user).exists():
            return Response({'errors': 'Рецепт уже добавлен в избранное'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = RecipeShoppingFavouriteSerializer(
            recipe, data=request.data, context={'request': request})
        if serializer.is_valid():
            Favourite.objects.create(recipe=recipe, user=request.user)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    @favorite.mapping.delete
    def delete_favorite(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        if Favourite.objects.filter(recipe=recipe,
                                    user=request.user).exists():
            Favourite.objects.filter(recipe=recipe,
                                     user=request.user).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Объекта не существует'},
                        status=status.HTTP_400_BAD_REQUEST)


class IgredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    filter_backends = (filters.SearchFilter, )
    search_fields = ('^name',)
