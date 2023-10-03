from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet

from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from .permissions import IsAdminOrReadOnly
from .serializers import (
    AddRecipeSerializer,
    IngredientSerializer,
    RecipeSerializer,
    TagSerializer,
)
from .utility import ExtraEndpoints


class CustomUserViewSet(UserViewSet):
    pass


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class RecipeViewSet(ModelViewSet, ExtraEndpoints):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        serializer_class=AddRecipeSerializer,
    )
    def favorite(self, request, pk):
        return self._add_post_delete_endpoint(
            request=request,
            pk=pk,
            related_model=Favorite,
            related_field='recipe',
            errors={
                'already_exists': 'Данный рецепт уже добавлен в избранное.',
                'not_exists': 'Данного рецепта нет в списке избранного.',
            },
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        serializer_class=AddRecipeSerializer,
    )
    def shopping_cart(self, request, pk):
        return self._add_post_delete_endpoint(
            request=request,
            pk=pk,
            related_model=ShoppingCart,
            related_field='recipe',
            errors={
                'already_exists': 'Данный рецепт уже добавлен в корзину.',
                'not_exists': 'Данного рецепта нет в корзине.',
            },
        )
