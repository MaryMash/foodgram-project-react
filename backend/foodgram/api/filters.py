from django_filters import FilterSet, filters

from recipes.models import Recipe, Tag


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(field_name='tags__slug',
                                             queryset=Tag.objects.all(),
                                             to_field_name='slug')
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        pass

    def filter_is_in_shopping_cart(self, queryset, name, value):
        pass

    class Meta:
        model = Recipe
        fields = ['tags', 'author']
