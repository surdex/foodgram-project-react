from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Ingredient, IngredientInRecipe, Recipe, Tag
from users.models import Follow
from users.serializers import CustomUserSerializer

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
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True
    )
    amount = serializers.IntegerField(min_value=1, read_only=True)

    class Meta:
        model = IngredientInRecipe
        fields = ['id', 'name', 'measurement_unit', 'amount']


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
        model = IngredientInRecipe
        fields = ['amount', 'id']


class CreateRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    cooking_time = serializers.IntegerField()
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

    def tag_and_ingredient_add(self, recipe, tags, ingredients):
        for tag in tags:
            recipe.tags.add(tag.id)
        for ingredient in ingredients:
            IngredientInRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount'],
            )
        return recipe

    def create(self, validated_data):
        ingredients = validated_data.pop('amounts')
        tags = validated_data.pop('tags')
        recipe = self.Meta.model.objects.create(**validated_data)
        return self.tag_and_ingredient_add(recipe, tags, ingredients)

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('amounts')
        tags = validated_data.pop('tags')
        IngredientInRecipe.objects.filter(recipe=instance).delete()
        instance.tags.clear()
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return self.tag_and_ingredient_add(instance, tags, ingredients)

    def validate_ingredients(self, value):
        if len(value) < 1:
            raise serializers.ValidationError(
                _('You didn\'t add any ingredients to recipe')
            )
        ingredients_id = []
        for ingredient in value:
            ingredient_id = ingredient.get('id')
            ingredient_amount = ingredient.get('amount')
            if ingredient_id in ingredients_id:
                raise serializers.ValidationError(
                    _('Ingredients must not be repeated')
                )
            if ingredient_amount < 1:
                raise serializers.ValidationError(
                    _('Amount of ingredients can\'t be less than 1')
                )
            ingredients_id.append(ingredient_id)
        return value

    def validate_tags(self, value):
        if len(value) < 1:
            raise serializers.ValidationError(
                _('You didn\'t add any tags to recipe')
            )
        tags_id = []
        for tag in value:
            tag_id = tag.id
            if tag_id in tags_id:
                raise serializers.ValidationError(
                    _('Tags must not be repeated')
                )
            tags_id.append(tag_id)
        return value

    def validate_cooking_time(self, value):
        if value < 1:
            raise serializers.ValidationError(
                _('Cooking time can\'t be less than 1')
            )
        return value


class ShotRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']
        extra_kwargs = {field: {'read_only': True} for field in fields}
