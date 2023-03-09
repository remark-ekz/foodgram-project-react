from django.db import models
from users.models import User
from django.core.validators import MaxValueValidator, MinValueValidator


class Tags(models.Model):
    name = models.CharField(
        'Имя',
        max_length=200
        )
    color = models.CharField(
        'Цвет в HEX',
        max_length=7,
        null=True)
    slug = models.SlugField(
        max_length=200,
        unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredients(models.Model):
    name = models.CharField(
        'Название',
        max_length=200)
    measure_unit = models.CharField(
        'Единица измерения',
        max_length=10)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} - {self.measure_unit}'


class Recipes(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    name = models.CharField(
        'Название рецепта',
        max_length=200)
    text = models.TextField('Текст рецепта')
    cooking_time = models.IntegerField(
        'Время приготовления, мин',
        validators=[
            MinValueValidator(1),
            MaxValueValidator(1000)
        ]
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        through='CountIngredients',
        verbose_name='Ингредиенты'
        )
    tags = models.ManyToManyField(Tags)
    image = models.ImageField(
        'Изображение',
        upload_to='recipes/images/',
        blank=True)
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class CountIngredients(models.Model):
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='count_in_recipe',
        verbose_name='Название рецепта'
        )
    ingredients = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        related_name='count_ingredients',
        verbose_name='Название ингридиента'
    )
    amount = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(100000)],
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Количество'
        verbose_name_plural = 'Количество'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredients'],
                name='unique_ingridient'
            )
        ]

    def __str__(self) -> str:
        return f'{self.ingredients} - {self.amount}'


class FavoriteRecipes(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_user',
        verbose_name='Добавить в избранное'
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='favorite_recipes',
        verbose_name='Рецепт в избранном'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]

    def __str__(self) -> str:
        return f'{self.user} favorite to {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_user',
        verbose_name='Список покупок пользователя')
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='shopping_recipe',
        verbose_name='Список покупок для рецепта'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_cart'
            )
        ]

    def __str__(self) -> str:
        return f'{self.user} add to {self.recipe}'
