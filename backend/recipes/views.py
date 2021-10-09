from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef, Sum
from django.http.response import HttpResponse
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.filters import IngredientFilter, RecipeFilter
from recipes.models import (
    Favorite, Ingredient, IngredientInRecipe, Recipe, Shopping, Tag,
)
from recipes.pagination import CustomPagination
from recipes.permissions import IsOwnerOrReadOnly
from recipes.serializers import (
    CreateRecipeSerializer, IngredientSerializer, RecipeSerializer,
    ShotRecipeSerializer, TagSerializer,
)

User = get_user_model()


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    serializer_class = RecipeSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly
    ]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_queryset(self):
        queryset = Recipe.objects.annotate(
            is_favorited=Exists(
                Favorite.objects.filter(
                    user=self.request.user.pk, recipe=OuterRef('pk')
                )
            ),
            is_in_shopping_cart=Exists(
                Shopping.objects.filter(
                    user=self.request.user.pk, recipe=OuterRef('pk')
                )
            )
        ).order_by('-id')
        return queryset

    def get_permissions(self):
        if self.action in ('favorite',
                           'download_shopping_cart', 'shopping_cart'):
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PUT', 'PATCH'):
            return CreateRecipeSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True, methods=['get', 'delete'],
        serializer_class=ShotRecipeSerializer
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if self.request.method == 'GET':
            if Favorite.objects.filter(
                user=request.user, recipe=recipe
            ).exists():
                return Response(
                    {'errors': _(
                        'The recipe is already in your favorite list'
                    )},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorite.objects.create(
                user=request.user, recipe=recipe
            )
            serializer = self.get_serializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif self.request.method == 'DELETE':
            if not Favorite.objects.filter(
                user=request.user, recipe=recipe
            ).exists():
                return Response(
                    {'errors': _('The recipe isn\'t in your favorite list')},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorite.objects.get(user=request.user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': _('Unknown error')},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True, methods=['get', 'delete'],
        serializer_class=ShotRecipeSerializer
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if self.request.method == 'GET':
            if Shopping.objects.filter(
                user=request.user, recipe=recipe
            ).exists():
                return Response(
                    {'errors': _(
                        'The recipe is already in your shopping list'
                    )},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Shopping.objects.create(
                user=request.user, recipe=recipe
            )
            serializer = self.get_serializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif self.request.method == 'DELETE':
            if not Shopping.objects.filter(
                user=request.user, recipe=recipe
            ).exists():
                return Response(
                    {'errors': _('The recipe isn\'t in your shopping list')},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Shopping.objects.get(user=request.user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': _('Unknown error')},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        user = request.user
        shopping_list = IngredientInRecipe.objects.filter(
            recipe__shopping__user=user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        filename = f'{user.username}\'s_shopping_list.txt'
        result = []
        for ingredient in shopping_list:
            result.append(
                f'{ingredient["ingredient__name"]} - {ingredient["amount"]} '
                + f'{ingredient["ingredient__measurement_unit"]};\n')
        response = HttpResponse(result, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
