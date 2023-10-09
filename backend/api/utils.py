from abc import ABC

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
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


class ReadOnlyModelSerializer(ModelSerializer):
    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)
        for field in fields:
            fields[field].read_only = True
        return fields


class ExtraEndpoints(ABC):
    def _add_post_delete_endpoint(
            self,
            request,
            id,
            related_model,
            related_field,
            error_messages=None,
    ):
        try:
            instance = self.queryset.get(id=id)
        except ObjectDoesNotExist:
            if (
                request.method == 'POST'
                and error_messages.get('object_not_exists_400')
            ):
                return Response(
                    {'errors': error_messages.get('object_not_exists_400')},
                    HTTP_400_BAD_REQUEST,
                )
            return Response(
                {'errors': error_messages.get('object_not_exists_404')},
                HTTP_404_NOT_FOUND,
            )
        relation_exists = related_model.objects.filter(
            user=request.user,
            **{related_field: instance},
        ).exists()
        if request.method == 'POST':
            if relation_exists:
                return Response(
                    {'errors': error_messages.get('relation_exists')},
                    HTTP_400_BAD_REQUEST,
                )
            if request.user == instance:
                return Response(
                    {'errors': error_messages.get('self_following')},
                    HTTP_400_BAD_REQUEST,
                )
            related_model.objects.create(
                user=request.user,
                **{related_field: instance},
            )
            return Response(
                self.serializer_class(
                    instance,
                    context={'request': request},
                ).data,
                HTTP_201_CREATED,
            )
        if not relation_exists:
            return Response(
                {'errors': error_messages.get('relation_not_exists')},
                HTTP_400_BAD_REQUEST,
            )
        related_model.objects.filter(
            user=request.user,
            **{related_field: instance}
        ).delete()
        return Response(
            self.serializer_class(instance, context={'request': request}).data,
            HTTP_204_NO_CONTENT,
        )
