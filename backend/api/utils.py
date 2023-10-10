from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.serializers import ModelSerializer
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
)

from recipes.models import RecipeIngredient, RecipeTag


def add_tags_ingredients(recipe, tags, ingredients):
    RecipeTag.objects.bulk_create([
        RecipeTag(recipe=recipe, tag=tag) for tag in tags
    ])
    RecipeIngredient.objects.bulk_create([
        RecipeIngredient(
            recipe=recipe,
            ingredient=ingredient_data.get('id'),
            amount=ingredient_data.get('amount'),
        ) for ingredient_data in ingredients
    ])


def remove_tags_ingredients(recipe):
    RecipeTag.objects.filter(recipe=recipe).delete()
    RecipeIngredient.objects.filter(recipe=recipe).delete()


class UserRelationActions:
    def _create_relation(self, model, serializer, id):
        target = get_object_or_404(self.queryset, id=id)
        try:
            model.objects.create(user=self.request.user, id=id)
        except Exception:
            return Response(
                {'errors': 'Данная запись уже существует.'},
                HTTP_400_BAD_REQUEST,
            )
        return Response(serializer(target).data, HTTP_201_CREATED)

    def _delete_relation(self, model, serializer, id):
        target = get_object_or_404(self.queryset, id=id)
        try:
            model.objects.delete(user=self.request.user, id=id)
        except Exception:
            return Response(
                {'errors': 'Данной записи не существует.'},
                HTTP_400_BAD_REQUEST,
            )
        return Response(serializer(target).data, HTTP_204_NO_CONTENT)


class ReadOnlyModelSerializer(ModelSerializer):
    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)
        for field in fields:
            fields[field].read_only = True
        return fields
