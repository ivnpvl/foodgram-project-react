from django.contrib.auth import get_user_model
from rest_framework.serializers import (
    ModelSerializer,
    PrimaryKeyRelatedField,
    SerializerMethodField,
)
from recipes.models import Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag
from .utility import Base64ImageField, ReadOnlyModelSerializer

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

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return bool(
            user.is_authenticated
            and user.subscriptions.filter(author=obj).exists()
        )


class IngredientSerializer(ReadOnlyModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


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
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='ingredient_relations',
        many=True,
    )
    is_favorite = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorite',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorite(self, obj):
        user = self.context.get('request').user
        return bool(
            user.is_authenticated
            and user.favorites.filter(recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return bool(
            user.is_authenticated
            and user.shopping_cart.filter(recipe=obj).exists()
        )

    def create(self, validated_data):
        user = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredient_relations')
        recipe = Recipe.objects.create(**validated_data, author=user)
        for tag in tags:
            RecipeTag.objects.create(recipe=recipe, tag=tag)
        for ingredient_data in ingredients:
            ingredient = ingredient_data.get('id')
            amount = ingredient_data.get('amount')
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount,
            )
        return recipe
