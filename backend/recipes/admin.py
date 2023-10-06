from django.contrib.admin import ModelAdmin, display, register
from .models import Ingredient, Recipe, Tag


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


@register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ('id', 'name', 'slug', 'color')
    list_filter = ('name',)
    search_fields = ('name',)


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = ('id', 'author', 'name', 'pub_date', 'in_favorite')
    list_filter = ('pub_date', 'author', 'name', 'tags')
    search_fields = ('name',)

    @display(description='Число добалений в избранное')
    def in_favorite(self, obj):
        return obj.in_favorite.all().count()
