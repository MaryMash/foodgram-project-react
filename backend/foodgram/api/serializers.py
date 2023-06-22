import base64

from django.core.files.base import ContentFile
from django.db import transaction
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from rest_framework import serializers
from users.models import CustomUser, Subscription


class CustomUserCreateSerializer(UserCreateSerializer):
    """Создание пользователя"""
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username',
                  'first_name', 'last_name', 'password')
        extra_kwargs = {'email': {'required': True},
                        'username': {'required': True},
                        'first_name': {'required': True},
                        'last_name': {'required': True},
                        'password': {'required': True}}


class CustomUserSerializer(UserSerializer):
    """Получение данных о пользователе"""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        if self.context['request'].user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=self.context['request'].user,
            author=obj).exists()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    "Список ингредиентов с кол-м"
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class CreateRecipeIngredientSerializer(serializers.ModelSerializer):
    "Список ингредиентов для создания рецепта"
    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')

    def to_representation(self, instance):
        amount = RecipeIngredient.objects.get(
            recipe__name=self.context['request'].data['name'],
            recipe__author=self.context['request'].user,
            ingredient=instance).amount
        representation = {'id': instance.id, 'name': instance.name,
                          'measurement_unit': instance.measurement_unit,
                          'amount': amount}
        return representation


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    """Получение рецепта"""
    tags = TagSerializer(read_only=True, many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(read_only=True, many=True,
                                             source='ingredient')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=False, allow_null=True)

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        try:
            return user.favourites.filter(recipe=obj).exists()
        except AttributeError:
            return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        try:
            return user.list.filter(recipe=obj).exists()
        except AttributeError:
            return False

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'name', 'image',
                  'text', 'cooking_time')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Создание, редактирование, удаление рецепта"""
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField(required=False, allow_null=True)
    ingredients = CreateRecipeIngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name', 'image',
                  'text', 'cooking_time')

    def validate_ingredients(self, data):
        ingredients = []
        for ingredient in data:
            if ingredient in ingredients:
                raise serializers.ValidationError(
                    'Нельзя указывать один ингредиент дважды.')
            ingredients.append(ingredient)
        return data

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        instance = Recipe.objects.create(**validated_data)
        instance.tags.set(tags)
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                amount=ingredient['amount']
            )
        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)

        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        RecipeIngredient.objects.filter(
            recipe=instance,
            ingredient__in=instance.ingredients.all()).delete()
        instance.tags.set(tags)
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                amount=ingredient['amount']
            )
        instance.save()
        return instance


class RecipeShoppingFavouriteSerializer(serializers.ModelSerializer):
    "Добавление в список покупок и избранное"
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        extra_kwargs = {'name': {'required': False}}


class RecipeSubscriptionsSerialiser(serializers.ModelSerializer):
    """Получение информации о рецепте в списке подписок"""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Получение данных о подписках пользователя"""
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    recipes = RecipeSubscriptionsSerialiser(read_only=True, many=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')
        extra_kwargs = {'email': {'required': False},
                        'username': {'required': False}
                        }

    def get_is_subscribed(self, obj):
        if self.context['request'].user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=self.context['request'].user,
            author=obj).exists()

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()
