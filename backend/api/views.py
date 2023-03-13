from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (CountIngredients, FavoriteRecipes, Ingredients,
                            Recipes, ShoppingCart, Tags)
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import Subscriptions, User

from .filters import CustomRecipesFilter, IngredientFilter
from .paginator import CustomPaginator
from .permissions import AuthorOrReadOnly, ObjectIsAuthenticated
from .serializers import (CustomUserSerializer, FavoriteSerializer,
                          IngredientSerializer, RecipesReadSerializer,
                          RecipesWriteSerializer, SetPasswordSerializer,
                          ShoppingSerializer, SubscribeSerializer,
                          TagSerializer)


class CreateListDestroyViewSet(
        mixins.CreateModelMixin,
        mixins.ListModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet
        ):
    pass


class CreateListRetrieveViewSet(
        mixins.CreateModelMixin,
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):
    pass


class CustomUserViewSet(CreateListRetrieveViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [ObjectIsAuthenticated]
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)

    @action(
        methods=['get'],
        detail=False,
        url_path='me',
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        user = get_object_or_404(User, username=self.request.user)
        if request.method == 'GET':
            serializer = CustomUserSerializer(
                user,
                context={'request': request},
                )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return status.HTTP_401_UNAUTHORIZED

    @action(
        methods=['post'],
        detail=False,
        url_path='set_password',
        permission_classes=(IsAuthenticated,),
    )
    def set_password(self, request):
        serializer = SetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(User, username=self.request.user)
        if not user.check_password(
                serializer.validated_data['current_password']):
            return Response(
                'Неверный текущий пароль',
                status=status.HTTP_400_BAD_REQUEST
                )
        self.request.user.set_password(serializer.data["new_password"])
        self.request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['get'],
        detail=False,
        url_path='subscriptions',
        permission_classes=(IsAuthenticated,),
        pagination_class=CustomPaginator
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(subscriptions__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            page,
            context={'request': request},
            many=True)

        return self.get_paginated_response(serializer.data)

    @action(
        methods=['post', 'delete'],
        detail=True,
        url_path='subscribe',
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, **kwargs):
        user = request.user
        author = get_object_or_404(User, id=kwargs['pk'])
        if request.method == 'POST':
            serializer = SubscribeSerializer(
                author,
                data=request.data,
                context={'request': request})
            serializer.is_valid(raise_exception=True)
            Subscriptions.objects.create(
                user=user,
                author=author
                )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            subscription = get_object_or_404(
                Subscriptions,
                user=user,
                author=author)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    pagination_class = CustomPaginator
    permission_classes = [AuthorOrReadOnly]
    http_method_names = ['get', 'post', 'create', 'patch', 'delete']
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CustomRecipesFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve)'):
            return RecipesReadSerializer
        return RecipesWriteSerializer

    @action(
        methods=['post', 'delete'],
        detail=True,
        url_path='favorite',
        permission_classes=(IsAuthenticated,),
        )
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipes, id=kwargs['pk'])
        user = request.user
        if request.method == 'POST':
            serializer = FavoriteSerializer(
                recipe,
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            FavoriteRecipes.objects.create(recipe=recipe, user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            favorite_recipe = get_object_or_404(
                FavoriteRecipes,
                recipe=recipe,
                user=user)
            favorite_recipe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return

    @action(
        methods=['post', 'delete'],
        detail=True,
        url_path='shopping_cart',
        permission_classes=(IsAuthenticated,),
        )
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipes, id=kwargs['pk'])
        user = request.user
        if request.method == 'POST':
            serializer = ShoppingSerializer(
                recipe,
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            ShoppingCart.objects.create(recipe=recipe, user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            shopping_cart = get_object_or_404(
                ShoppingCart,
                recipe=recipe,
                user=user)
            shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return

    @action(
        methods=['get'],
        detail=False,
        url_path='download_shopping_cart',
        permission_classes=(IsAuthenticated,),
        )
    def download_shopping_cart(self, request):
        ingredients = CountIngredients.objects.filter(
            recipe__shopping_recipe__user=request.user).values(
            'ingredients__name', 'ingredients__measurement_unit', 'amount'
            )
        shopping_cart = {}
        for ingredient in ingredients:
            if ingredient['ingredients__name'] in shopping_cart.keys():
                shopping_cart[
                    ingredient['ingredients__name']
                    ][0][0] += ingredient['amount']
            else:
                shopping_cart[ingredient['ingredients__name']] = [
                    ingredient['amount']], [
                    ingredient['ingredients__measurement_unit']
                    ]
        text_file = []
        for key, value in shopping_cart.items():
            text_file.append(f'{key} - {value[0][0]} {value[1][0]} \n')
        name_file = 'shopping_cart.txt'
        response = HttpResponse(text_file, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={name_file}'
        return response
