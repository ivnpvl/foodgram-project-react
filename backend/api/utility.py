from abc import ABC
from base64 import b64decode

from django.core.files.base import ContentFile
from rest_framework.response import Response
from rest_framework.serializers import ImageField, ModelSerializer
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
)


class ReadOnlyModelSerializer(ModelSerializer):
    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)
        for field in fields:
            fields[field].read_only = True
        return fields


class Base64ImageField(ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class ExtraEndpoints(ABC):
    def _add_post_delete_endpoint(
            self,
            request,
            pk,
            related_model,
            related_field,
            error_messages=None,
    ):
        user = request.user
        instance = self.queryset.get(id=pk)
        relation_exists = related_model.objects.filter(
            user=user,
            **{related_field: instance},
        ).exists()
        if request.method == 'POST':
            if relation_exists:
                return Response(
                    {'errors': error_messages.get('already_exists')},
                    HTTP_400_BAD_REQUEST,
                )
            related_model.objects.create(
                user=user,
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
                {'errors': error_messages.get('not_exists')},
                HTTP_400_BAD_REQUEST,
            )
        related_model.objects.filter(
            user=user,
            **{related_field: instance}
        ).delete()
        return Response(HTTP_204_NO_CONTENT)
