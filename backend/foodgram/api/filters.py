from django_filters import FilterSet, filters
from recipes.models import Recipe, Tag


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(field_name='tags__slug',
                                             queryset=Tag.objects.all(),
                                             to_field_name='slug')

    class Meta:
        model = Recipe
        fields = ['tags', 'author']
