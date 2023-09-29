from django.urls import include, path
from rest_framework.routers import SimpleRouter
from .views import IngredientViewSet, TagViewSet, RecipeViewSet

app_name = 'api'

router = SimpleRouter()
router.register('ingredients', IngredientViewSet, 'ingredients')
router.register('recipes', RecipeViewSet, 'recipes')
router.register('tags', TagViewSet, 'tags')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
