import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from recipes.models import (Favourite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingList, Tag)
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

    # def get_recipes(self, obj):
    #     recipes = Recipe.objects.filter(author=obj)
    #     serializers = RecipeSerializer(recipes, many=True)
    #     return Responce(serializers.data)


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
        representation = super().to_representation(instance)
        representation['amount'] = instance.ingredients.all()[0]

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
    is_favourited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=False, allow_null=True)

    def get_is_favourited(self, obj):
        return Favourite.objects.filter(user=self.context['request'].user,
                                        recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        return ShoppingList.objects.filter(user=self.context['request'].user,
                                           recipe=obj).exists()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favourited', 'is_in_shopping_cart', 'name', 'image',
                  'text', 'cooking_time')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Создание, редактирование, удаление рецепта"""
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField(required=False, allow_null=True)
    # is_favourited = serializers.SerializerMethodField()
    # is_in_shopping_cart = serializers.SerializerMethodField()
    ingredients = CreateRecipeIngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name', 'image',
                  'text', 'cooking_time')

        # fields = ('id', 'tags', 'author', 'ingredients',
        #           'is_favourited', 'is_in_shopping_cart', 'name', 'image',
        #           'text', 'cooking_time')

    # def get_is_favourited(self, obj):
    #     return False

    # def get_is_in_shopping_cart(self, obj):
    #     return ShoppingList.objects.filter(user=self.context['request'].user,
    #                                        recipe=obj).exists()

    # if self.context['request'].user.is_anonymous:
    #         return False
    #     return Subscription.objects.filter(
    #         user=self.context['request'].user,
    #         author=obj).exists()

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

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)

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
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeSerializer(instance,
                                context=self.context).data


class RecipeShoppingFavouriteSerializer(serializers.ModelSerializer):
    "Добавление в список покупок и избранное"
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        extra_kwargs = {'name': {'required': False}}


# class ShoppingListSerializer(serializers.ModelSerializer):
#     "Список покупок: добавление удаление рецепта"
#     class Meta:
#         model = ShoppingList
#         fields = '__all__'


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
