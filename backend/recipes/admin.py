from django.contrib import admin

from .models import (
    Tags,
    Recipes,
    Ingredients,
    CountIngredients,
    FavoriteRecipes,
    ShoppingCart
    )


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'color',
        'slug')
    list_editable = (
        'name',
        'color',
        'slug')
    empty_value_display = '-пусто-'


@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'measure_unit')
    list_editable = ('name',)
    search_fields = ('name',)


@admin.register(Recipes)
class RecipesAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'author',
        'cooking_time',
        'in_favorites')
    list_editable = (
        'name',
        'cooking_time',
        'author')
    list_filter = (
        'name',
        'author',
        'tags')
    readonly_fields = ('in_favorites',)
    empty_value_display = '-пусто-'

    @admin.display(description='Избранное')
    def in_favorites(self, obj):
        return obj.favorite_recipes.count()


@admin.register(CountIngredients)
class CountIngredientsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'ingredients', 'amount')
    list_editable = ('recipe', 'ingredients', 'amount')


@admin.register(FavoriteRecipes)
class FavoriteRecipesAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    list_editable = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    list_editable = ('user', 'recipe')
