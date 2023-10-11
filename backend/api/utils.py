from rest_framework.serializers import ModelSerializer

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
