from django.contrib.auth import get_user_model
from django.db.models import F
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import (
    IntegerField,
    ModelSerializer,
    PrimaryKeyRelatedField,
    SerializerMethodField,
)
from recipes.models import Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag
from .utils import Base64ImageField, ReadOnlyModelSerializer

User = get_user_model()


class UserSerializer(ModelSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed',
        )
        extra_kwargs = {
            'id': {'read_only': True},
            'password': {'write_only': True},
        }

    def get_is_subscribed(self, author):
        user = self.context.get('request').user
        return bool(
            user.is_authenticated
            and user.subscriptions.filter(author=author).exists()
        )


class IngredientSerializer(ReadOnlyModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientResponseSerializer(ReadOnlyModelSerializer):
    amount = IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class TagSerializer(ReadOnlyModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeIngredientSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeSerializer(ModelSerializer):
    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        allow_empty=False,
    )
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='ingredient_relations',
        many=True,
        allow_empty=False,
    )
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate_tags(self, value):
        if len(value) != len(set(value)):
            raise ValidationError(
                {'tags': 'Запрещено передавать повторяющиеся тэги.'}
            )
        return value

    def validate_ingredients(self, value):
        ingredient_ids = [ingredient.get('id') for ingredient in value]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise ValidationError(
                {'ingredients':
                    'Запрещено передавать повторяющиеся ингредиенты.'}
            )
        return value

    def get_is_favorited(self, recipe):
        user = self.context.get('request').user
        return bool(
            user.is_authenticated
            and user.favorites.filter(recipe=recipe).exists()
        )

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get('request').user
        return bool(
            user.is_authenticated
            and user.shopping_cart.filter(recipe=recipe).exists()
        )

    def create(self, validated_data):
        user = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredient_relations')
        recipe = Recipe.objects.create(**validated_data, author=user)
        for tag in tags:
            RecipeTag.objects.create(recipe=recipe, tag=tag)
        for ingredient_data in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient_data.get('id'),
                amount=ingredient_data.get('amount'),
            )
        return recipe

    def update(self, recipe, validated_data):
        tags = validated_data.pop('tags', None)
        if not tags:
            raise ValidationError(
                {'tags': 'Нельзя обновить рецепт без указания тэгов.'},
            )
        ingredients = validated_data.pop('ingredient_relations', None)
        if not ingredients:
            raise ValidationError(
                {'ingredients':
                    'Нельзя обновить рецепт без указания ингредиентов.'},
            )
        for attr, value in validated_data.items():
            setattr(recipe, attr, value)
        RecipeTag.objects.filter(recipe=recipe).delete()
        for tag in tags:
            RecipeTag.objects.create(recipe=recipe, tag=tag)
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        for ingredient_data in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient_data.get('id'),
                amount=ingredient_data.get('amount'),
            )
        recipe.save()
        return recipe

    def to_representation(self, recipe):
        data = super(RecipeSerializer, self).to_representation(recipe)
        tags = TagSerializer(recipe.tags, many=True).data
        ingredients = IngredientResponseSerializer(
            recipe.ingredients.annotate(amount=F('recipe_relations__amount')),
            many=True,
        ).data
        data.update(tags=tags, ingredients=ingredients)
        return data


class RecipeResponseSerializer(ReadOnlyModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(ReadOnlyModelSerializer):
    is_subscribed = SerializerMethodField()
    recipes = RecipeResponseSerializer(many=True)
    recipes_count = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_is_subscribed(self, author):
        user = self.context.get('request').user
        return bool(user.subscriptions.filter(author=author).exists())

    def get_recipes_count(self, author):
        return author.recipes.count()
