from django.urls import include, path
from rest_framework.routers import SimpleRouter

app_name = 'api'

router = SimpleRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
