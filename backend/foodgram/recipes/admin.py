from django.contrib import admin

from .models import Ingredient, Recipe, RecipeIngredient, ShoppingList, Tag


@admin.register(Tag)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'color', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')


# class IngredientInline(admin.TabularInline):
#     model = Recipe.ingredients.through


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author')
    list_filter = ('name', 'author', 'tags')
    # fields = ['tags', 'author',']
    # inlines = (IngredientInline,)


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'ingredient', 'amount')


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'user')
