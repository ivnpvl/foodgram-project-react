from django.contrib.admin import ModelAdmin, register
from django.contrib.auth import get_user_model

User = get_user_model()


@register(User)
class UserAdmin(ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')
    search_fields = ('username', 'email')
    list_filter = ('username', 'email')
