from django.contrib.admin import ModelAdmin, TabularInline, display, register

from .models import Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag


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


class RecipeIngredientInline(TabularInline):
    model = RecipeIngredient
    extra = 1
    verbose_name = 'Ингредиент'
    verbose_name_plural = 'Ингредиенты'


class TagIngredientInline(TabularInline):
    model = RecipeTag
    extra = 1
    verbose_name = 'Тэг'
    verbose_name_plural = 'Тэги'


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = (
        'name',
        'text',
        'author',
        'pub_date',
        'get_tags',
        'get_ingredients',
        'in_favorite',
    )
    inlines = (RecipeIngredientInline, TagIngredientInline)
    list_filter = ('name', 'author', 'tags')
    search_fields = ('-pub_date',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('tags', 'ingredients')

    @display(description='Ингредиенты')
    def get_ingredients(self, recipe):
        return ", ".join(
            [str(ingredient) for ingredient in recipe.ingredients.all()]
        )

    @display(description='Тэги')
    def get_tags(self, recipe):
        return ", ".join([str(tag) for tag in recipe.tags.all()])

    @display(description='Число добавлений в избранное')
    def in_favorite(self, obj):
        return obj.in_favorite.all().count()
