from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = models.CharField(
        'Логин',
        max_length=150,
        unique=True
        )
    password = models.CharField(
        'Пароль',
        max_length=150
        )
    email = models.EmailField(
        'Адрес электронной почты',
        max_length=254,
        unique=True
        )
    first_name = models.CharField(
        'Имя',
        max_length=150
        )
    last_name = models.CharField(
        'Фамилия',
        max_length=150
        )
    admin = models.BooleanField('Админ', default=False)
    bloked = models.BooleanField('Заблокирован', default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        ordering = ['-id']
        verbose_name = 'Пользователь',
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.is_superuser


class Subscriptions(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name=' Подписан на'
    )

    class Meta:
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscribe'
            )
        ]

    def __str__(self) -> str:
        return f'{self.user} subscribed to {self.author}'
