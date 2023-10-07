from django.contrib.auth import get_user_model
from django.db.models import F
from django.http.response import HttpResponse
from djoser.views import UserViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.viewsets import ModelViewSet

from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from users.models import Subscription
from .filters import IngredientFilterSet, RecipeFilterSet
from .mixins import RetriveListViewSet
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    IngredientSerializer,
    IngredientResponseSerializer,
    RecipeSerializer,
    RecipeResponseSerializer,
    SubscribeSerializer,
    TagSerializer,
)
from .utils import ExtraEndpoints

User = get_user_model()


class CustomUserViewSet(UserViewSet, ExtraEndpoints):
    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        serializer_class=SubscribeSerializer,
    )
    def subscribe(self, request, id):
        return self._add_post_delete_endpoint(
            request=request,
            id=id,
            related_model=Subscription,
            related_field='author',
            error_messages={
                'object_not_exists_404':
                    'Пользователя нет в базе, проверьте id.',
                'relation_exists': 'Вы уже подписаны на данного пользователя.',
                'relation_not_exists':
                    'Вы не подписаны на данного пользователя.',
                'self_following': 'Вы не можете подписаться на самого себя.',
            },
        )

    @action(detail=False, methods=['GET'])
    def subscriptions(self, request):
        subscriptions = User.objects.filter(subscribers__user=request.user)
        page = self.paginate_queryset(subscriptions)
        if page is not None:
            serializer = SubscribeSerializer(
                page,
                context={'request': request},
                many=True,
            )
            return self.get_paginated_response(serializer.data)
        serializer = SubscribeSerializer(
            subscriptions,
            context={'request': request},
            many=True,
        )
        return Response(serializer.data, HTTP_200_OK)


class IngredientViewSet(RetriveListViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilterSet


class TagViewSet(RetriveListViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class RecipeViewSet(ModelViewSet, ExtraEndpoints):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilterSet

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        serializer_class=RecipeResponseSerializer,
    )
    def favorite(self, request, pk):
        return self._add_post_delete_endpoint(
            request=request,
            id=pk,
            related_model=Favorite,
            related_field='recipe',
            error_messages={
                'object_not_exists_400': 'Рецепта нет в базе, проверьте id.',
                'object_not_exists_404': 'Рецепта нет в базе, проверьте id.',
                'relation_exists': 'Данный рецепт уже добавлен в избранное.',
                'relation_not_exists':
                    'Данного рецепта нет в списке избранного.',
            },
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        serializer_class=RecipeResponseSerializer,
    )
    def shopping_cart(self, request, pk):
        return self._add_post_delete_endpoint(
            request=request,
            id=pk,
            related_model=ShoppingCart,
            related_field='recipe',
            error_messages={
                'object_not_exists_400': 'Рецепта нет в базе, проверьте id.',
                'object_not_exists_404': 'Рецепта нет в базе, проверьте id.',
                'relation_exists': 'Данный рецепт уже добавлен в корзину.',
                'relation_not_exists': 'Данного рецепта нет в корзине.',
            },
        )

    @action(detail=False, methods=['GET'])
    def download_shopping_cart(self, request):
        data = {}
        recipes = Recipe.objects.filter(in_shopping_cart__user=request.user)
        for recipe in recipes:
            ingredients = IngredientResponseSerializer(
                recipe.ingredients.annotate(
                    amount=F('recipe_relations__amount')
                ),
                many=True,
            ).data
            for ingredient in ingredients:
                name = (
                    f'{ingredient["name"].capitalize()} '
                    f'({ingredient["measurement_unit"]})'
                )
                data[name] = data.setdefault(name, 0) + ingredient['amount']
        file_data = 'Список покупок:\n' + ',\n'.join(
            f'{name} - {amount}' for name, amount in data.items()
        )
        filename = 'shopping_list.txt'
        response = HttpResponse(file_data, content_type='text/plain')
        response["Content-Disposition"] = f'attachment; filename={filename}'
        return response
