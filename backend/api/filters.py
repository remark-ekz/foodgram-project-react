from django_filters import FilterSet
from django_filters import rest_framework as filters

from recipes.models import Tags, Recipes


class CustomRecipesFilter(FilterSet):
    is_favorited = filters.BooleanFilter(
        method='favorited_filter',
        label='Поиск по избранному'
    )
    author = filters.CharFilter(
        field_name='author__username',
        label='Поиск по автору'
    )
    is_shopping_cart = filters.BooleanFilter(
        method='shopping_cart_filter',
        label='Поиск по списку покупок'
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags_slug',
        to_field_name='slug',
        queryset=Tags.objects.all(),
        label='Поиск по тегу'
    )

    def favorited_filter(self, queryset, name, value):
        if value:
            return queryset.filters(favorite_recipes__author=self.request.user)
        return queryset

    def shopping_cart_filter(self, queryset, name, value):
        if value:
            return queryset.filters(shopping_recipe__author=self.request.user)
        return queryset

    class Meta:
        model = Recipes
        fields = (
            'is_favorited',
            'author',
            'is_shopping_cart',
            'tags'
        )
