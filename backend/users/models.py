from django.contrib.auth import get_user_model
from django.db import models

from recipes.models import Recipe


User = get_user_model()


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscryer',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscription',
    )

    class Meta:
        ordering = ('user',)
        constraints = [
            models.UniqueConstraint(
                name='unique_subscription',
                fields=['user', 'author'],
            ),
            models.CheckConstraint(
                name='prevent_self_follow',
                check=~models.Q(user=models.F('author')),
            ),
        ]


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='is_favorite',
    )

    class Meta:
        ordering = ('user',)
        constraints = [
            models.UniqueConstraint(
                name='unique_favorite_recipe',
                fields=['user', 'recipe'],
            ),
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shoping_cart',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_shoping_cart',
    )

    class Meta:
        ordering = ('user',)
        constraints = [
            models.UniqueConstraint(
                name='unique_recipe_in_cart',
                fields=['user', 'recipe'],
            ),
        ]
