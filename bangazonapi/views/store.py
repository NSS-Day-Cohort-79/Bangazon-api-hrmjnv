"""View module for handling requests about stores"""
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from bangazonapi.models import Store
from .product import ProductSerializer


class StoreSerializer(serializers.ModelSerializer):
    """JSON serializer for stores"""
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Store
        fields = ('id', 'user', 'name', 'description', 'products')
        depth = 1


class StoreCreateSerializer(serializers.ModelSerializer):
    """JSON serializer for creating and updating stores"""
    class Meta:
        model = Store
        fields = ('id', 'name', 'description')


class StoreViewSet(ViewSet):
    """Request handlers for Stores in the Bangazon Platform"""
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def create(self, request):
        """Handle POST operations"""
        store = Store()
        store.name = request.data["name"]
        store.description = request.data["description"]
        store.user = request.auth.user
        store.save()

        serializer = StoreCreateSerializer(store, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """Handle GET request for a single store"""
        try:
            store = Store.objects.get(pk=pk)
            serializer = StoreSerializer(store, context={"request": request})
            return Response(serializer.data)
        except Store.DoesNotExist as ex:
            return Response({"message": ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def update(self, request, pk=None):
        """Handle PUT requests for a store"""
        store = Store.objects.get(pk=pk)

        if store.user != request.auth.user:
            return Response({"message": "You do not have permission to edit this store."}, status=status.HTTP_403_FORBIDDEN)

        store.name = request.data["name"]
        store.description = request.data["description"]
        store.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a store"""
        try:
            store = Store.objects.get(pk=pk)

            if store.user != request.auth.user:
                return Response({"message": "You do not have permission to delete this store."}, status=status.HTTP_403_FORBIDDEN)

            store.delete()
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        except Store.DoesNotExist as ex:
            return Response({"message": ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def list(self, request):
        """Handle GET requests for all stores"""
        stores = Store.objects.all()

        mine = self.request.query_params.get("mine", None)
        if mine is not None:
            stores = stores.filter(user=request.auth.user)

        serializer = StoreSerializer(stores, many=True, context={"request": request})
        return Response(serializer.data)
