"""View module for handling requests about products"""

from rest_framework.decorators import action
from bangazonapi.models.recommendation import Recommendation
import base64
from django.core.files.base import ContentFile
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from bangazonapi.models import Product, Customer, ProductCategory
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.parsers import MultiPartParser, FormParser


class ProductSerializer(serializers.ModelSerializer):
    """JSON serializer for products"""

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "price",
            "number_sold",
            "description",
            "quantity",
            "created_date",
            "location",
            "image_path",
            "average_rating",
            "can_be_rated",
        )
        depth = 1


class Products(ViewSet):
    """Request handlers for Products in the Bangazon Platform"""

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def create(self, request):
        """Handle POST operations for creating a new product"""
        new_product = Product()
        new_product.name = request.data["name"]
        new_product.price = request.data["price"]
        new_product.description = request.data["description"]
        new_product.quantity = request.data["quantity"]
        new_product.location = request.data["location"]

        customer = Customer.objects.get(user=request.auth.user)
        new_product.customer = customer

        product_category = ProductCategory.objects.get(pk=request.data["category_id"])
        new_product.category = product_category

        if "image_path" in request.data:
            format, imgstr = request.data["image_path"].split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(
                base64.b64decode(imgstr),
                name=f'{new_product.id}-{request.data["name"]}.{ext}',
            )
            new_product.image_path = data

        new_product.save()

        serializer = ProductSerializer(new_product, context={"request": request})

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """Handle GET requests for a single product"""
        try:
            product = Product.objects.get(pk=pk)
            serializer = ProductSerializer(product, context={"request": request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def update(self, request, pk=None):
        """Handle PUT requests for updating a product"""
        product = Product.objects.get(pk=pk)
        product.name = request.data["name"]
        product.price = request.data["price"]
        product.description = request.data["description"]
        product.quantity = request.data["quantity"]
        product.created_date = request.data["created_date"]
        product.location = request.data["location"]

        customer = Customer.objects.get(user=request.auth.user)
        product.customer = customer

        product_category = ProductCategory.objects.get(pk=request.data["category_id"])
        product.category = product_category
        product.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a product"""
        try:
            product = Product.objects.get(pk=pk)
            product.delete()
            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except Product.DoesNotExist as ex:
            return Response({"message": ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response(
                {"message": ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def list(self, request):
        """Handle GET requests for all products, including filtering and ordering"""
        products = Product.objects.all()

        category = self.request.query_params.get("category", None)
        quantity = self.request.query_params.get("quantity", None)
        order = self.request.query_params.get("order_by", None)
        direction = self.request.query_params.get("direction", None)
        number_sold = self.request.query_params.get("number_sold", None)

        if order is not None:
            order_filter = order
            if direction is not None and direction == "desc":
                order_filter = f"-{order}"
            products = products.order_by(order_filter)

        if category is not None:
            products = products.filter(category__id=category)

        if quantity is not None:
            products = products.order_by("-created_date")[: int(quantity)]

        if number_sold is not None:

            def sold_filter(product):
                """Filter helper to return products sold >= requested amount"""
                # OLD BUGGY CODE:
                # if product.number_sold <= int(number_sold):
                #     return True

                # NEW FIXED CODE:
                if product.number_sold >= int(number_sold):
                    return True

                return False

            products = filter(sold_filter, products)

        serializer = ProductSerializer(
            products, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @action(methods=["post"], detail=True)
    def recommend(self, request, pk=None):
        """Custom action to recommend a product to another user"""
        if request.method == "POST":
            rec = Recommendation()
            rec.recommender = Customer.objects.get(user=request.auth.user)
            rec.customer = Customer.objects.get(user__id=request.data["recipient"])
            rec.product = Product.objects.get(pk=pk)
            rec.save()
            return Response(None, status=status.HTTP_204_NO_CONTENT)

        return Response(None, status=status.HTTP_405_METHOD_NOT_ALLOWED)
