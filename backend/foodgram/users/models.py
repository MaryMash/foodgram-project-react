from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(
        max_length=254,
        verbose_name='email',
        unique=True
    )
    username = models.CharField(
        max_length=150,
        verbose_name='username',
        unique=True
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='first_name'
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='first_name'
    )

    class Meta:
        ordering = ('username',)

    def __str__(self) -> str:
        return f'{self.username}: {self.email}'


class Subscription(models.Model):
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='recipe_author',
        verbose_name='Автор',
        help_text='Автор рецепта'
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик',
        help_text='Подписчика автора рецепта'
    )
    subscription_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата',
        help_text='Дата подписки'
    )

    class Meta:
        ordering = ('-subscription_date',)
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='%(app_label)s_%(class)s_user_author_unique'
            ),
            models.CheckConstraint(
                check=~models.Q(author=models.F('user')),
                name='self_subscription_not_allowed'
            )

        ]

    def __str__(self) -> str:
        return f'Автор {self.author} - подписчик {self.user}'
