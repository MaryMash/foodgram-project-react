from django.contrib import admin

from .models import (Favourite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingList, Tag)


@admin.register(Tag)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'color', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author', 'added_to_favourites')
    list_filter = ('name', 'author', 'tags')
    readonly_fields = ('added_to_favourites',)

    @admin.display()
    def added_to_favourites(self, obj):
        return obj.favourites.count()


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'ingredient', 'amount')
    autocomplete_fields = ('ingredient',)


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'user')


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'user')
