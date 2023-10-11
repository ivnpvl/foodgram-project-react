from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import Sum
from django.http.response import HttpResponse
from djoser.views import UserViewSet
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
)
from rest_framework.viewsets import ModelViewSet

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    ShoppingCart,
    Tag,
    User,
)
from users.models import Subscription
from .filters import IngredientFilterSet, RecipeFilterSet
from .mixins import RetriveListViewSet
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    IngredientSerializer,
    RecipeSerializer,
    RecipeResponseSerializer,
    SubscribeSerializer,
    TagSerializer,
)


class CustomUserViewSet(UserViewSet):
    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()

    @action(detail=True, methods=('post',))
    def subscribe(self, request, id):
        if request.user.id == id:
            return Response(
                {'errors': 'Нельзя подписаться на самого себя.'},
                HTTP_400_BAD_REQUEST,
            )
        author = get_object_or_404(User, id=id)
        try:
            Subscription.objects.create(user=request.user, author=author)
        except IntegrityError:
            return Response(
                {'errors': 'Подписка уже существует.'},
                HTTP_400_BAD_REQUEST,
            )
        return Response(
            SubscribeSerializer(author, context={'request': request}).data,
            HTTP_201_CREATED,
        )

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        try:
            Subscription.objects.get(
                user=request.user,
                author=author,
            ).delete()
        except ObjectDoesNotExist:
            return Response(
                {'errors': 'Подписки на данного автора не существует.'},
                HTTP_400_BAD_REQUEST,
            )
        return Response(
            SubscribeSerializer(author, context={'request': request}).data,
            HTTP_204_NO_CONTENT,
        )

    @action(detail=False, methods=('get',))
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


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilterSet

    @staticmethod
    def create_relation(model, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        try:
            model.objects.create(user=request.user, recipe=recipe)
        except IntegrityError:
            return Response(
                {'errors': 'Рецепт уже добавлен.'},
                HTTP_400_BAD_REQUEST,
            )
        return Response(
            RecipeResponseSerializer(recipe).data,
            HTTP_201_CREATED,
        )

    @staticmethod
    def delete_relation(model, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        try:
            model.objects.get(user=request.user, recipe=recipe).delete()
        except ObjectDoesNotExist:
            return Response(
                {'errors': 'Рецепт не был добавлен.'},
                HTTP_400_BAD_REQUEST,
            )
        return Response(
            RecipeResponseSerializer(recipe).data,
            HTTP_204_NO_CONTENT,
        )

    @action(detail=True, methods=('post',))
    def favorite(self, request, pk):
        return self.create_relation(Favorite, request, pk)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.delete_relation(Favorite, request, pk)

    @action(detail=True, methods=('post',))
    def shopping_cart(self, request, pk):
        return self.create_relation(ShoppingCart, request, pk)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return self.delete_relation(ShoppingCart, request, pk)

    @action(detail=False, methods=('get',))
    def download_shopping_cart(self, request):
        ingredients = Ingredient.objects.filter(
            recipes__in_shopping_cart__user=request.user
        ).values(
            'name',
            'measurement_unit',
        ).annotate(total_amount=Sum('recipe_relations__amount'))
        template = '{name} ({measurement_unit}) - {total_amount}'
        file_data = 'Список покупок:\n' + ',\n'.join(
            template.format(**ingredient) for ingredient in ingredients
        )
        filename = 'shopping_list.txt'
        response = HttpResponse(file_data, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
