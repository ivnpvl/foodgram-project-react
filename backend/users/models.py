from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db.models import (
    Model,
    CharField,
    EmailField,
    ForeignKey,
    CASCADE,
    CheckConstraint,
    UniqueConstraint,
    Q,
    F,
)

from backend.constants import MAX_LENGTH_EMAIL, MAX_LENGTH_USER_INFO


class CustomUser(AbstractUser):
    email = EmailField(
        verbose_name='Адрес электронной почты',
        max_length=MAX_LENGTH_EMAIL,
        unique=True,
    )
    username = CharField(
        verbose_name='Уникальный юзернэйм',
        max_length=MAX_LENGTH_USER_INFO,
        validators=(UnicodeUsernameValidator,),
        unique=True,
    )
    first_name = CharField(
        verbose_name='Имя',
        max_length=MAX_LENGTH_USER_INFO,
    )
    last_name = CharField(
        verbose_name='Фамилия',
        max_length=MAX_LENGTH_USER_INFO,
    )
    password = CharField(
        verbose_name='Пароль',
        max_length=MAX_LENGTH_USER_INFO,
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username


class Subscription(Model):
    user = ForeignKey(
        CustomUser,
        on_delete=CASCADE,
        related_name='subscriptions',
    )
    author = ForeignKey(
        CustomUser,
        on_delete=CASCADE,
        related_name='subscribers',
    )

    class Meta:
        ordering = ('user',)
        constraints = (
            UniqueConstraint(
                name='unique_subscription',
                fields=('user', 'author'),
            ),
            CheckConstraint(
                name='prevent_self_follow',
                check=~Q(user=F('author')),
            ),
        )

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
