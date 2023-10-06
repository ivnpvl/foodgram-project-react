from django.contrib.admin import ModelAdmin, display, register
from .models import Ingredient, Recipe, Tag


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


@register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ('name', 'slug', 'color')
    list_filter = ('name',)
    search_fields = ('name',)


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = (
        'name',
        'author',
        'pub_date',
        'get_tags',
        'get_ingredients',
        'in_favorite',
    )
    list_filter = ('pub_date', 'author', 'name', 'tags')
    search_fields = ('name',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('tags', 'ingredients')

    @display(description='Тэги')
    def get_tags(self, recipe):
        return ", ".join([str(tag) for tag in recipe.tags.all()])

    @display(description='Ингредиенты')
    def get_ingredients(self, recipe):
        return ", ".join(
            [str(ingredient) for ingredient in recipe.ingredients.all()]
        )

    @display(description='Число добалений в избранное')
    def in_favorite(self, obj):
        return obj.in_favorite.all().count()
