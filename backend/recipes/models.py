from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=64,
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения',
        max_length=16,
    )


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=64,
        unique=True,
    )
    color = models.CharField(
        verbose_name='Цвет',
        max_length=64,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name='Индекс',
        max_length=64,
        unique=True,
    )


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=128,
        unique=True,
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipes/',
    )
    text = models.TextField(
        verbose_name='Описание',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        on_delete=models.CASCADE,
        through='RecipeIngredient',
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
        on_delete=models.SET_NULL,
        through='RecipeTag',
        related_name='recipes',
        blank=True,
        null=True,
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
    )


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='ingredient',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        related_name='recipe',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
    )


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='tag',
    )
    tag = models.ForeignKey(
        Tag,
        verbose_name='Тэг',
        on_delete=models.CASCADE,
        related_name='recipe',
    )
