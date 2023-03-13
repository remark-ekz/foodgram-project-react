from django_filters import FilterSet
from django_filters import rest_framework as filters
from recipes.models import Ingredients, Recipes, Tags


class IngredientFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredients
        fields = ['name']


class CustomRecipesFilter(FilterSet):
    is_favorited = filters.BooleanFilter(
        method='favorited_filter',
        label='Поиск по избранному'
    )
    author = filters.CharFilter(
        field_name='author__id',
        label='Поиск по автору'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='shopping_cart_filter',
        label='Поиск по списку покупок'
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tags.objects.all(),
        label='Поиск по тегу'
    )

    def favorited_filter(self, queryset, name, value):
        user = self.request.user
        if value:
            return queryset.filter(favorite_recipes__user=user)
        return queryset

    def shopping_cart_filter(self, queryset, name, value):
        user = self.request.user
        if value:
            return queryset.filter(shopping_recipe__user=user)
        return queryset

    class Meta:
        model = Recipes
        fields = (
            'is_favorited',
            'author',
            'is_in_shopping_cart',
            'tags'
        )
