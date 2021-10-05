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

    name = models.CharField(_('tag'), max_length=200, unique=True)
    color = models.CharField(_('color'), max_length=7,
                             validators=[color_validator], unique=True)
    slug = models.SlugField(_('slug'), max_length=200, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = _('Ingredient')
        verbose_name_plural = _('Ingredients')

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    '''
    Ingredient model for recipes
    '''
    name = models.CharField(_('ingredient'), max_length=200, unique=True)
    measurement_unit = models.CharField(_('measure'), max_length=64)

    class Meta:
        ordering = ['name']
        verbose_name = _('Ingredient')
        verbose_name_plural = _('Ingredients')

    def __str__(self):
        return f'{self.name}: {self.measurement_unit}'


class IngredientsInRecipes(models.Model):
    recipe = models.ForeignKey(
        'Recipe', verbose_name=_('Recipe'),
        on_delete=models.CASCADE,
        related_name='amounts'
    )
    ingredient = models.ForeignKey(
        'Ingredient', verbose_name=_('Ingredient'),
        on_delete=models.CASCADE,
        related_name='amounts'
    )
    amount = models.PositiveSmallIntegerField(
        _('amount'), validators=[MinValueValidator(1), ], default=1
    )

    class Meta:
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
        'Tag', verbose_name=_('Tags'), related_name='recipes'
    )
    author = models.ForeignKey(
        User,
        verbose_name=_('author'),
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        verbose_name=_('Ingredients'),
        related_name='recipes',
        through='IngredientsInRecipes'
    )
    image = models.ImageField(
        _('image'), upload_to='recipes/'
    )
    text = models.TextField(_('description'), )
    cooking_time = models.PositiveSmallIntegerField(
        _('minutes'), default=1, validators=[MinValueValidator(1), ]
    )


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorite'
    )
    recipe = models.ForeignKey(
        'Recipe', on_delete=models.CASCADE, related_name='favorite'
    )


class Shopping(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='shopping'
    )
    recipe = models.ForeignKey(
        'Recipe', on_delete=models.CASCADE, related_name='shopping'
    )
