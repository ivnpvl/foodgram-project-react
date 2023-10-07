from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import (
    Model,
    CharField,
    DateTimeField,
    ImageField,
    ManyToManyField,
    PositiveSmallIntegerField,
    TextField,
    SlugField,
    ForeignKey,
    CASCADE,
    UniqueConstraint,
)

User = get_user_model()


class Ingredient(Model):
    name = CharField(verbose_name='Название', max_length=200)
    measurement_unit = CharField(
        verbose_name='Единицы измерения',
        max_length=200,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return self.name


class Tag(Model):
    name = CharField(
        verbose_name='Название',
        max_length=200,
        unique=True,
    )
    color = CharField(
        verbose_name='Цвет в HEX',
        max_length=7,
        unique=True,
    )
    slug = SlugField(
        verbose_name='Уникальный слаг',
        max_length=200,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ['name']

    def __str__(self):
        return self.name


class Recipe(Model):
    author = ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=CASCADE,
        related_name='recipes',
    )
    pub_date = DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True,
    )
    name = CharField(
        verbose_name='Название',
        max_length=200,
        unique=True,
    )
    image = ImageField(
        verbose_name='Фотография готового блюда',
        upload_to='recipes/',
    )
    text = TextField(verbose_name='Описание')
    ingredients = ManyToManyField(
        Ingredient,
        verbose_name='Список ингредиентов',
        through='RecipeIngredient',
        related_name='recipes',
    )
    tags = ManyToManyField(
        Tag,
        verbose_name='Список id тэгов',
        through='RecipeTag',
        related_name='recipes',
    )
    cooking_time = PositiveSmallIntegerField(
        verbose_name='Время приготовления в минутах',
        validators=[MaxValueValidator(1440), MinValueValidator(1)],
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['name']

    def __str__(self):
        return self.name

    def delete(self, using=None, keep_parents=False):
        self.image.storage.delete(self.image.name)
        super().delete()


class RecipeIngredient(Model):
    recipe = ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=CASCADE,
        related_name='ingredient_relations',
    )
    ingredient = ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=CASCADE,
        related_name='recipe_relations',
    )
    amount = PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(1)],
    )

    class Meta:
        ordering = ('recipe',)
        constraints = [
            UniqueConstraint(
                name='unique_ingredient_in_recipe',
                fields=('recipe', 'ingredient'),
            ),
        ]


class RecipeTag(Model):
    recipe = ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=CASCADE,
        related_name='tag_relations',
    )
    tag = ForeignKey(
        Tag,
        verbose_name='Тэг',
        on_delete=CASCADE,
        related_name='recipe_relations',
    )

    class Meta:
        ordering = ('recipe',)
        constraints = [
            UniqueConstraint(
                name='unique_tag_on_recipe',
                fields=('recipe', 'tag'),
            ),
        ]


class Favorite(Model):
    user = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='favorites',
    )
    recipe = ForeignKey(
        Recipe,
        on_delete=CASCADE,
        related_name='in_favorite',
    )

    class Meta:
        ordering = ('user',)
        constraints = [
            UniqueConstraint(
                name='unique_recipe_in_favorite',
                fields=('user', 'recipe'),
            ),
        ]


class ShoppingCart(Model):
    user = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='shopping_cart',
    )
    recipe = ForeignKey(
        Recipe,
        on_delete=CASCADE,
        related_name='in_shopping_cart',
    )

    class Meta:
        ordering = ('user',)
        constraints = [
            UniqueConstraint(
                name='unique_recipe_in_cart',
                fields=('user', 'recipe'),
            ),
        ]
