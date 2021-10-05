from django_filters import rest_framework as filters
from django_filters.filters import (
    AllValuesMultipleFilter, BooleanFilter, CharFilter,
)

from .models import Ingredient, Recipe


class IngredientFilter(filters.FilterSet):
    name = CharFilter(label='name', field_name='name', lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeFilter(filters.FilterSet):
    tags = AllValuesMultipleFilter(label='tags', field_name='tags__slug',
                                   conjoined=False)
    author = CharFilter(label='author', field_name='author__id')
    favorite = BooleanFilter(
        label='is_favorited',
        field_name='is_favorited',
        method='filter_favorite'
    )
    shopping = BooleanFilter(
        label='is_in_shopping_cart',
        field_name='is_in_shopping_cart',
        method='filter_shopping'
    )

    def filter_favorite(self, queryset, name, value):
        return queryset.filter(is_favorited=value)

    def filter_shopping(self, queryset, name, value):
        return queryset.filter(is_in_shopping_cart=value)

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'favorite', 'shopping']
