from rest_framework.exceptions import ValidationError
from rest_framework import serializers, status
from djoser.serializers import UserSerializer
from django.contrib.auth.hashers import make_password
import base64
from django.core.files.base import ContentFile

from users.models import User, Subscriptions
from recipes.models import (
    Tags,
    Recipes,
    Ingredients,
    FavoriteRecipes,
    ShoppingCart,
    CountIngredients)


class Base64ImageField(serializers.ImageField):
    '''Функция для декодирования изображений'''
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class CustomUserSerializer(UserSerializer):
    '''Сериализатор пользователей'''
    is_subscribed = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed',
        )

    def validate(self, data):
        invalid_username = ['me', 'set_password', 'subscriptions', 'subscribe']
        if data['username'] in invalid_username:
            raise ValidationError('Недопустимый логин')
        return data

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return Subscriptions.objects.filter(user=user, author=obj).exists()
        return False

    def create(self, validated_data):
        validated_data['password'] = (
            make_password(validated_data.pop('password'))
        )
        return super().create(validated_data)


class SetPasswordSerializer(UserSerializer):
    '''Изменение пароля'''
    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = (
            'new_password',
            'current_password',
        )


class RecipesSerializer(serializers.ModelSerializer):
    '''Спикок рецептов без тегов и ингредиентов'''
    image = Base64ImageField(read_only=True)
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = Recipes
        fields = (
            'id',
            'name',
            'image',
            'cooking_time')


class SubscribeSerializer(CustomUserSerializer):
    '''Подписка на пользователей'''
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    email = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    recipes = RecipesSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes_count',
            'recipes'
        )
        read_only_fields = (
            'email',
            'username',
            'first_name',
            'last_name'
            )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return (
            self.context.get('request').user.is_authenticated
            and Subscriptions.objects.filter(
                user=user,
                author=obj).exists()
                )

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if user == author:
            raise serializers.ValidationError(
                detail='Нельзя подписаться на самого себя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        if Subscriptions.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError(
                detail='Подписка на этого пользователя уже есть!',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data


# ________________________________________________


class TagSerializer(serializers.ModelSerializer):
    '''Список тегов'''
    class Meta:
        model = Tags
        fields = (
            'id',
            'name',
            'color',
            'slug')
        read_only_fields = (
            'name',
            'color',
            'slug')


class IngredientSerializer(serializers.ModelSerializer):
    '''Список ингредиентов'''
    class Meta:
        model = Ingredients
        fields = (
            'id',
            'name',
            'measure_unit',
            )


class CountIngredientReadSerializer(serializers.ModelSerializer):
    '''Список игредиентов и их количество в рецепте'''
    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.ReadOnlyField(source='ingredients.name')
    measure_unit = serializers.ReadOnlyField(source='ingredients.measure_unit')

    class Meta:
        model = CountIngredients
        fields = (
            'id',
            'name',
            'measure_unit',
            'amount',
            )


class RecipesReadSerializer(serializers.ModelSerializer):
    '''Список рецептов'''
    tags = TagSerializer(many=True)
    ingredients = CountIngredientReadSerializer(
        many=True,
        source='count_in_recipe'
        )
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipes
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return FavoriteRecipes.objects.filter(
                user=user,
                recipe=obj
                ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return ShoppingCart.objects.filter(
                user=user,
                recipe=obj
                ).exists()
        return False


class CountIngredientWriteSerializer(serializers.ModelSerializer):
    '''Ингредиенты и их количество для создания рецепта'''
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredients.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = CountIngredients
        fields = (
            'id',
            'amount'
            )


class RecipesWriteSerializer(serializers.ModelSerializer):
    '''Создание, изменение, и удаление рецепта'''
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tags.objects.all())
    ingredients = CountIngredientWriteSerializer(
        many=True,
        source='count_in_recipe'
        )
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipes
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def tag_selection(self, recipe, tags):
        for tag in tags:
            recipe.tags.add(tag)

    def ingredient_selection(self, recipe, ingredients):
        for ingredient in ingredients:
            print(ingredient)
            ingredient_id = ingredient['id']
            print(ingredient_id)
            amount = ingredient.get('amount')
            CountIngredients.objects.create(
                recipe=recipe,
                ingredients=ingredient_id,
                amount=amount
            )

    def create(self, validated_data):
        print(validated_data)
        ingredients = validated_data.pop('count_in_recipe')
        print(ingredients)
        tags = validated_data.pop('tags')
        recipe = Recipes.objects.create(
            author=self.context.get('request').user,
            **validated_data)
        self.tag_selection(recipe, tags)
        self.ingredient_selection(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
            )
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('count_in_recipe')
        CountIngredients.objects.filter(recipe=instance).all().delete()
        self.tag_selection(instance, tags)
        self.ingredient_selection(instance, ingredients)
        instance.save()
        return instance

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return FavoriteRecipes.objects.filter(
                user=user,
                recipe=obj
                ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return ShoppingCart.objects.filter(
                user=user,
                recipe=obj
                ).exists()
        return False


class FavoriteSerializer(RecipesSerializer):
    '''Добавление и удаление избранного рецепта'''
    class Meta:
        model = Recipes
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )

    def validate(self, data):
        recipe = self.instance
        user = self.context.get('request').user
        if FavoriteRecipes.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                detail='Этот рецепт уже в ибранном!',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data


class ShoppingSerializer(RecipesSerializer):
    '''Список покупок. Добавление и удаление'''
    class Meta:
        model = Recipes
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )

    def validate(self, data):
        recipe = self.instance
        user = self.context.get('request').user
        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                detail='Этот рецепт уже в списке!',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data
