"""View module for handling requests about customer profiles"""

import datetime
from django.http import HttpResponseServerError
from django.contrib.auth.models import User
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from bangazonapi.models import Order, Customer, Product
from bangazonapi.models import OrderProduct, Favorite
from bangazonapi.models import Recommendation
from .product import ProductSerializer
from .order import OrderSerializer


class Profile(ViewSet):
    """Request handlers for user profile info in the Bangazon Platform"""

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def list(self, request):
        """
        GET /profile — returns authenticated user's profile
        """
        try:
            # OLD BUGGY CODE:
            # current_user = Customer.objects.get(user=4)
            # ^ Hard‑coded user ID meant the same profile was always returned,
            #   completely ignoring the authenticated user's token.

            # NEW FIXED CODE:
            current_user = Customer.objects.get(user=request.auth.user)
            # ^ Correctly retrieves the Customer associated with the token-authenticated user,
            #   ensuring each user receives THEIR OWN profile.

            current_user.recommends = Recommendation.objects.filter(
                recommender=current_user
            )

            serializer = ProfileSerializer(
                current_user, many=False, context={"request": request}
            )

            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)

    @action(methods=["get", "post", "delete"], detail=False)
    def cart(self, request):
        """Shopping cart manipulation"""

        current_user = Customer.objects.get(user=request.auth.user)

        if request.method == "DELETE":
            try:
                open_order = Order.objects.get(customer=current_user, payment_type=None)
                line_items = OrderProduct.objects.filter(order=open_order)
                line_items.delete()
                open_order.delete()
            except Order.DoesNotExist as ex:
                return Response(
                    {"message": ex.args[0]}, status=status.HTTP_404_NOT_FOUND
                )

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        if request.method == "GET":
            try:
                open_order = Order.objects.get(customer=current_user, payment_type=None)
                line_items = OrderProduct.objects.filter(order=open_order)
                line_items = LineItemSerializer(
                    line_items, many=True, context={"request": request}
                )

                cart = {}
                cart["order"] = OrderSerializer(
                    open_order, many=False, context={"request": request}
                ).data
                cart["order"]["line_items"] = line_items.data
                cart["order"]["size"] = len(line_items.data)

            except Order.DoesNotExist as ex:
                return Response(
                    {"message": ex.args[0]}, status=status.HTTP_404_NOT_FOUND
                )

            return Response(cart["order"])

        if request.method == "POST":
            try:
                open_order = Order.objects.get(customer=current_user)
                print(open_order)
            except Order.DoesNotExist as ex:
                open_order = Order()
                open_order.created_date = datetime.datetime.now()
                open_order.customer = current_user
                open_order.save()

            line_item = OrderProduct()
            line_item.product = Product.objects.get(pk=request.data["product_id"])
            line_item.order = open_order
            line_item.save()

            line_item_json = LineItemSerializer(
                line_item, many=False, context={"request": request}
            )

            return Response(line_item_json.data)

        return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(methods=["get"], detail=False)
    def favoritesellers(self, request):
        customer = Customer.objects.get(user=request.auth.user)
        favorites = Favorite.objects.filter(customer=customer)

        serializer = FavoriteSerializer(
            favorites, many=True, context={"request": request}
        )
        return Response(serializer.data)


class LineItemSerializer(serializers.HyperlinkedModelSerializer):
    product = ProductSerializer(many=False)

    class Meta:
        model = OrderProduct
        fields = ("id", "product")
        depth = 1


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")
        depth = 1


class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Customer
        fields = (
            "id",
            "user",
        )


class ProfileProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "id",
            "name",
        )


class RecommenderSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()
    product = ProfileProductSerializer()

    class Meta:
        model = Recommendation
        fields = (
            "product",
            "customer",
        )


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False)
    recommends = RecommenderSerializer(many=True)

    class Meta:
        model = Customer
        fields = (
            "id",
            "url",
            "user",
            "phone_number",
            "address",
            "payment_types",
            "recommends",
        )
        depth = 1


class FavoriteUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "username")
        depth = 1


class FavoriteSellerSerializer(serializers.HyperlinkedModelSerializer):
    user = FavoriteUserSerializer(many=False)

    class Meta:
        model = Customer
        fields = (
            "id",
            "url",
            "user",
        )
        depth = 1


class FavoriteSerializer(serializers.HyperlinkedModelSerializer):
    seller = FavoriteSellerSerializer(many=False)

    class Meta:
        model = Favorite
        fields = ("id", "seller")
        depth = 2
