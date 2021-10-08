from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters
from django_filters.filters import (
    BooleanFilter, CharFilter, ModelChoiceFilter, ModelMultipleChoiceFilter,
)

from recipes.models import Ingredient, Recipe, Tag

User = get_user_model()


class IngredientFilter(filters.FilterSet):
    name = CharFilter(label='name', field_name='name', lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeFilter(filters.FilterSet):
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    author = ModelChoiceFilter(queryset=User.objects.all())
    is_favorited = BooleanFilter(
        field_name='is_favorited',
        method='filter_favorite'
    )
    is_in_shopping_cart = BooleanFilter(
        field_name='is_in_shopping_cart',
        method='filter_shopping'
    )

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_favorited', 'is_in_shopping_cart']

    def filter_favorite(self, queryset, name, value):
        if value:
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def filter_shopping(self, queryset, name, value):
        if value:
            return queryset.filter(shopping__user=self.request.user)
        return queryset
