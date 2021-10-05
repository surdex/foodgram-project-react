from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from users.models import Follow
from users.serializers import CustomUserSerializer

from .models import Ingredient, IngredientsInRecipes, Recipe, Tag

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']
        read_only_fields = ['id', 'name', 'color', 'slug']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class AuthorRecipeSerializer(CustomUserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return Follow.objects.filter(user=request.user, author=obj.pk).exists()


class IngredientsInRecipesSerializer(serializers.ModelSerializer):
    ingredient = serializers.SlugRelatedField(
        slug_field='name', read_only=True
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True
    )
    amount = serializers.IntegerField(min_value=1, read_only=True)

    class Meta:
        model = IngredientsInRecipes
        fields = ['id', 'ingredient', 'measurement_unit', 'amount']


class RecipeSerializer(serializers.ModelSerializer):
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(min_value=1, read_only=True)
    tags = TagSerializer(many=True)
    author = AuthorRecipeSerializer(read_only=True)
    ingredients = IngredientsInRecipesSerializer(
        label='ingredients', source='amounts', many=True, read_only=True
    )

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'tags', 'author',
                  'ingredients', 'image', 'text',
                  'cooking_time', 'is_in_shopping_cart', 'is_favorited']


class IngredientsSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField()
    id = serializers.SlugRelatedField(
        slug_field='id', queryset=Ingredient.objects.all()
    )

    class Meta:
        model = IngredientsInRecipes
        fields = ['amount', 'id']


class CreateRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(min_value=1)
    ingredients = IngredientsSerializer(
        label='ingredients', many=True, source='amounts'
    )
    tags = serializers.SlugRelatedField(
        slug_field='id',
        queryset=Tag.objects.all(),
        many=True
    )

    class Meta:
        model = Recipe
        fields = ['ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time']

    def to_representation(self, instance):
        serializer = RecipeSerializer(instance)
        return serializer.data

    def create(self, validated_data):
        ingredients = validated_data.pop('amounts')
        tags = validated_data.pop('tags')
        recipe = self.Meta.model.objects.create(**validated_data)
        for tag in tags:
            recipe.tags.add(tag)
        for ingredient in ingredients:
            IngredientsInRecipes.objects.create(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount'],
            )
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('amounts')
        tags = validated_data.pop('tags')
        IngredientsInRecipes.objects.filter(recipe=instance).delete()
        instance.tags.clear()
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        for tag in tags:
            instance.tags.add(tag)
        for ingredient in ingredients:
            IngredientsInRecipes.objects.create(
                recipe=instance,
                ingredient=ingredient['id'],
                amount=ingredient['amount'],
            )
        return instance


class ShotRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']
        extra_kwargs = {field: {'read_only': True} for field in fields}
