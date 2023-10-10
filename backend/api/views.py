from django.db.models import Sum
from django.http.response import HttpResponse
from djoser.views import UserViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
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
from .utils import UserRelationActions


class CustomUserViewSet(UserViewSet, UserRelationActions):
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
        return self._create_relation(Subscription, SubscribeSerializer, id)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id):
        return self._delete_relation(Subscription, SubscribeSerializer, id)

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


class RecipeViewSet(ModelViewSet, UserRelationActions):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilterSet

    @action(detail=True, methods=('post',))
    def favorite(self, request, pk):
        return self._create_relation(Favorite, RecipeResponseSerializer, pk)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self._delete_relation(Favorite, RecipeResponseSerializer, pk)

    @action(detail=True, methods=('post',))
    def shopping_cart(self, request, pk):
        return self._create_relation(
            ShoppingCart,
            RecipeResponseSerializer,
            pk,
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return self._delete_relation(
            ShoppingCart,
            RecipeResponseSerializer,
            pk,
        )

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
