from django.contrib import admin

from .models import (
    Favorite, Ingredient, IngredientInRecipe, Recipe, Shopping, Tag,
)


class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    search_fields = ('name', )
    empty_value_display = '-empty-'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    search_fields = ('name', )
    empty_value_display = '-empty-'


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author')
    list_filter = ('author', 'tags')
    search_fields = ('author', 'name', 'tags')
    filter_horizontal = ('tags', 'ingredients')
    empty_value_display = '-empty-'


class IngredientInRecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'ingredient', 'amount')
    search_fields = ('recipe', 'ingredient')
    empty_value_display = '-empty-'


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'user')
    list_filter = ('user', )
    search_fields = ('recipe', 'user')
    empty_value_display = '-empty-'


class ShoppingAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'user')
    list_filter = ('user', )
    search_fields = ('recipe', 'user')
    empty_value_display = '-empty-'


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientInRecipe, IngredientInRecipeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Shopping, ShoppingAdmin)
