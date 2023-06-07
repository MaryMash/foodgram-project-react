from django.core.validators import MinValueValidator, validate_slug
from django.db import models

from core.validators import hex_validator
from users.models import CustomUser


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Тег',
        help_text='Тег рецепта'
    )
    color = models.CharField(
        max_length=7,
        unique=True,
        verbose_name='Цвет',
        help_text='Цвет тега',
        validators=[hex_validator]
    )
    slug = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Слаг',
        help_text='Слаг тега',
        validators=[validate_slug]
    )

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Название',
        help_text='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Название',
        help_text='Название ед. измерения'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='ingredient_unique'
            ),

        ]

    def __str__(self) -> str:
        return f'{self.name} {self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
        help_text='Автор рецепта'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Название рецепта'
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipes/images/',
        blank=True
    )
    text = models.TextField(
        verbose_name='Текст',
        help_text='Текст рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиент',
        help_text='Ингредиент рецепта'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        help_text='Теги рецепта',
        related_name='recipes',
    )
    cooking_time = models.IntegerField(
        default=1,
        verbose_name='Время приготовления',
        help_text='Время приготовления в минутах',
        validators=[
            MinValueValidator(
                limit_value=1,
                message="Vaule should be bigger than 0"
            ),
        ]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        help_text='Дата публикации поста'
    )

    class Meta:
        ordering = ('-pub_date',)

        constraints = [
            models.UniqueConstraint(
                fields=['name', 'author'],
                name='recipe_unique'
            ),
            models.CheckConstraint(
                check=models.Q(cooking_time__gte=1),
                name="cooking_time_gte_1"
            )

        ]

    def __str__(self) -> str:
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient',
        verbose_name='Рецепт',
        help_text='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Ингредиент',
        help_text='Ингредиент'
    )
    amount = models.IntegerField(
        default=1,
        verbose_name='Кол-во',
        help_text='Кол-во ингредиента',
        validators=[
            MinValueValidator(
                limit_value=1,
                message="Vaule should be bigger than 0"
            ),
        ]
    )

    class Meta:
        ordering = ('recipe',)

        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='recipe_ingredient_unique'
            ),
            models.CheckConstraint(
                check=models.Q(amount__gte=1),
                name="amount_gte_1"
            )

        ]

    def __str__(self) -> str:
        return f'{self.recipe} {self.ingredient}'
