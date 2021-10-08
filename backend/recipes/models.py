from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from recipes.validators import ColorTagValidator

User = get_user_model()


class Tag(models.Model):
    '''
    Tag model for recipes
    '''
    color_validator = ColorTagValidator()

    name = models.CharField(
        verbose_name=_('tag'), max_length=200, unique=True
    )
    color = models.CharField(
        verbose_name=_('color'),
        max_length=7,
        validators=[color_validator],
        unique=True
    )
    slug = models.SlugField(
        verbose_name=_('slug'), max_length=200, unique=True
    )

    class Meta:
        ordering = ['name']
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    '''
    Ingredient model for recipes
    '''
    name = models.CharField(
        verbose_name=_('ingredient'),
        max_length=200,
        unique=True)
    measurement_unit = models.CharField(
        verbose_name=_('measure'), max_length=64
    )

    class Meta:
        ordering = ['name']
        verbose_name = _('Ingredient')
        verbose_name_plural = _('Ingredients')

    def __str__(self):
        return f'{self.name}: {self.measurement_unit}'


class IngredientInRecipe(models.Model):
    '''
    Model of ingredients in recipe
    '''
    recipe = models.ForeignKey(
        'Recipe', verbose_name=_('recipe'),
        on_delete=models.CASCADE,
        related_name='amounts'
    )
    ingredient = models.ForeignKey(
        'Ingredient', verbose_name=_('ingredient'),
        on_delete=models.CASCADE,
        related_name='amounts'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name=_('amount'),
        validators=[MinValueValidator(1, _('amount can\'t be less than 1')), ],
        default=1
    )

    class Meta:
        verbose_name = _('Ingredient in recipe')
        verbose_name_plural = _('Ingredients in recipe')
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredients'
            )
        ]


class Recipe(models.Model):
    '''
    Recipe model
    '''
    name = models.CharField(
        _('recipe name'), max_length=200
    )
    tags = models.ManyToManyField(
        'Tag', verbose_name=_('tags'), related_name='recipes'
    )
    author = models.ForeignKey(
        User,
        verbose_name=_('author'),
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        verbose_name=_('ingredients'),
        related_name='recipes',
        through='IngredientInRecipe'
    )
    image = models.ImageField(
        verbose_name=_('image'), upload_to='recipes/'
    )
    text = models.TextField(verbose_name=_('description'))
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name=_('minutes'),
        default=1,
        validators=[MinValueValidator(1), ]
    )

    class Meta:
        ordering = ['-id']
        verbose_name = _('Recipe')
        verbose_name_plural = _('Recipes')

    def __str__(self):
        return self.name


class Favorite(models.Model):
    '''
    Favorite model
    '''
    user = models.ForeignKey(
        User, verbose_name=_('user'),
        on_delete=models.CASCADE,
        related_name='favorite'
    )
    recipe = models.ForeignKey(
        'Recipe', verbose_name=_('recipe'),
        on_delete=models.CASCADE,
        related_name='favorite'
    )

    class Meta:
        verbose_name = _('Favorite')
        verbose_name_plural = _('Favorites')
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]


class Shopping(models.Model):
    '''
    Shopping model
    '''
    user = models.ForeignKey(
        User, verbose_name=_('user'),
        on_delete=models.CASCADE,
        related_name='shopping'
    )
    recipe = models.ForeignKey(
        'Recipe', verbose_name=_('recipe'),
        on_delete=models.CASCADE,
        related_name='shopping'
    )

    class Meta:
        verbose_name = _('Shopping')
        verbose_name_plural = _('Shoppings')
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping'
            )
        ]
