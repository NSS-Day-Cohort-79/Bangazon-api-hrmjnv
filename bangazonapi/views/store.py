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
        """
        @api {POST} /stores POST new store
        @apiName CreateStore
        @apiGroup Store

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611

        @apiParam {String} name Name of the store
        @apiParam {String} description Description of the store
        @apiParamExample {json} Input
            {
                "name": "Steve's Shop",
                "description": "All the latest cars at unbeatable prices."
            }

        @apiSuccess (201) {Object} store Created store
        @apiSuccess (201) {Number} store.id Store Id
        @apiSuccess (201) {String} store.name Name of the store
        @apiSuccess (201) {String} store.description Description of the store
        @apiSuccessExample {json} Success
            HTTP/1.1 201 Created
            {
                "id": 1,
                "name": "Steve's Shop",
                "description": "All the latest cars at unbeatable prices."
            }
        """
        store = Store()
        store.name = request.data["name"]
        store.description = request.data["description"]
        store.user = request.auth.user
        store.save()

        serializer = StoreCreateSerializer(store, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """
        @api {GET} /stores/:id GET store
        @apiName GetStore
        @apiGroup Store

        @apiParam {Number} id Store Id

        @apiSuccess (200) {Object} store Store object
        @apiSuccess (200) {Number} store.id Store Id
        @apiSuccess (200) {String} store.name Name of the store
        @apiSuccess (200) {String} store.description Description of the store
        @apiSuccess (200) {Object} store.user Owner of the store
        @apiSuccess (200) {Object[]} store.products Products sold in the store
        @apiSuccessExample {json} Success
            {
                "id": 1,
                "name": "Steve's Shop",
                "description": "All the latest cars at unbeatable prices.",
                "user": { "id": 5, "username": "steve" },
                "products": []
            }
        """
        try:
            store = Store.objects.get(pk=pk)
            serializer = StoreSerializer(store, context={"request": request})
            return Response(serializer.data)
        except Store.DoesNotExist as ex:
            return Response({"message": ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def update(self, request, pk=None):
        """
        @api {PUT} /stores/:id PUT changes to store
        @apiName UpdateStore
        @apiGroup Store

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611

        @apiParam {Number} id Store Id to update
        @apiParam {String} name Updated name of the store
        @apiParam {String} description Updated description of the store
        @apiParamExample {json} Input
            {
                "name": "Steve's Updated Shop",
                "description": "Updated description."
            }
        @apiSuccessExample {json} Success
            HTTP/1.1 204 No Content
        """
        store = Store.objects.get(pk=pk)

        if store.user != request.auth.user:
            return Response({"message": "You do not have permission to edit this store."}, status=status.HTTP_403_FORBIDDEN)

        store.name = request.data["name"]
        store.description = request.data["description"]
        store.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """
        @api {DELETE} /stores/:id DELETE store
        @apiName DeleteStore
        @apiGroup Store

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611

        @apiParam {Number} id Store Id to delete
        @apiSuccessExample {json} Success
            HTTP/1.1 204 No Content
        """
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
        """
        @api {GET} /stores GET all stores
        @apiName ListStores
        @apiGroup Store

        @apiQuery {String} [mine] If present, returns only stores owned by the current user

        @apiSuccess (200) {Object[]} stores Array of store objects
        @apiSuccessExample {json} Success
            [
                {
                    "id": 1,
                    "name": "Steve's Shop",
                    "description": "All the latest cars at unbeatable prices.",
                    "user": { "id": 5, "username": "steve" },
                    "products": []
                }
            ]
        """
        stores = Store.objects.all()

        mine = self.request.query_params.get("mine", None)
        if mine is not None:
            stores = stores.filter(user=request.auth.user)

        serializer = StoreSerializer(stores, many=True, context={"request": request})
        return Response(serializer.data)
