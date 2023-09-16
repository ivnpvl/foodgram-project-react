from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения',
        max_length=200,
    )

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
        unique=True,
    )
    color = models.CharField(
        verbose_name='Цвет в HEX',
        max_length=7,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name='Уникальный слаг',
        max_length=200,
        unique=True,
    )


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True,
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
        unique=True,
    )
    image = models.ImageField(
        verbose_name='Картинка, закодированная в Base64',
        upload_to='recipes/',
    )
    text = models.TextField(
        verbose_name='Описание',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Список ингредиентов',
        through='RecipeIngredient',
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Список id тэгов',
        through='RecipeTag',
        related_name='recipes',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления в минутах',
        validators=[MaxValueValidator(1440), MinValueValidator(1)],
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
        validators=[MinValueValidator(1)],
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


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='is_favorite',
    )

    class Meta:
        ordering = ('user',)
        constraints = [
            models.UniqueConstraint(
                name='unique_favorite_recipe',
                fields=['user', 'recipe'],
            ),
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shoping_cart',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_shoping_cart',
    )

    class Meta:
        ordering = ('user',)
        constraints = [
            models.UniqueConstraint(
                name='unique_recipe_in_cart',
                fields=['user', 'recipe'],
            ),
        ]
