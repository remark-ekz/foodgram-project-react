from django.contrib import admin

from .models import (CountIngredients, FavoriteRecipes, Ingredients, Recipes,
                     ShoppingCart, Tags)


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
        'measurement_unit')
    list_editable = ('name',)
    search_fields = ('name',)


@admin.register(Recipes)
class RecipesAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'author',
        'cooking_time',
    )

    list_editable = (
        'name',
        'cooking_time',
        'author')
    list_filter = (
        'name',
        'author',
        'tags')
    empty_value_display = '-пусто-'


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
