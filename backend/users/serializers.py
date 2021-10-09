from django.contrib.auth import get_user_model
from djoser.conf import settings
from djoser.serializers import UserSerializer
from rest_framework import serializers

from recipes.models import Recipe

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.BooleanField(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = tuple(User.REQUIRED_FIELDS) + (
            settings.USER_ID_FIELD,
            settings.LOGIN_FIELD,
            'is_subscribed',
        )
        extra_kwargs = {field: {'required': True} for field in fields}


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']
        extra_kwargs = {field: {'read_only': True} for field in fields}


class SubscribeUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.BooleanField(read_only=True, default=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            settings.USER_ID_FIELD,
            settings.LOGIN_FIELD,
            'is_subscribed',
            'recipes',
            'recipes_count'
        )
        extra_kwargs = {field: {'read_only': True} for field in fields}

    def get_recipes(self, obj):
        limit = None
        try:
            limit = self.context['request'].query_params['recipes_limit']
        except Exception:
            pass
        queryset = obj.recipes.all()[
            :int(limit)
        ] if limit else obj.recipes.all()
        serializer = ShortRecipeSerializer(queryset, many=True)
        return serializer.data
