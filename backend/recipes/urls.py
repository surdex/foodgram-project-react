from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet, RecipeViewSet, TagViewSet

router = DefaultRouter()
router.register('tags', TagViewSet, basename='Tags')
router.register('ingredients', IngredientViewSet, basename='Ingredients')
router.register('recipes', RecipeViewSet, basename='Recipes')


urlpatterns = [
    path('', include(router.urls)),
]
