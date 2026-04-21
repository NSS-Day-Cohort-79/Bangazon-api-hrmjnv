"""View module for handling requests about line items"""

from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from bangazonapi.models import OrderProduct, Order, Product, Customer


class LineItemSerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for line items"""

    class Meta:
        model = OrderProduct
        url = serializers.HyperlinkedIdentityField(
            view_name="lineitem", lookup_field="id"
        )
        fields = ("id", "url", "order", "product")


class LineItems(ViewSet):
    """Line items for Bangazon orders"""

    # TIP: By setting this class attribute, then a `basename` parameter
    #      does not need to be set on the route in urls.py:11 and allow
    #      the serializer (see above) use the `view_name='lineitem'`
    #      argument for the HyperlinkedIdentityField. If this is NOT set
    #      then the following exception gets thrown.
    #
    # ImproperlyConfigured at /lineitems/4
    #   Could not resolve URL for hyperlinked relationship using view name
    #   "orderproduct-detail". You may have failed to include the related
    #   model in your API, or incorrectly configured the `lookup_field`
    #   attribute on this field.
    # queryset = OrderProduct.objects.all()

    def retrieve(self, request, pk=None):
        """
        @api {GET} /cart/:id DELETE line item from cart
        @apiName RemoveLineItem
        @apiGroup ShoppingCart

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611

        @apiParam {id} id Product Id to remove from cart
        @apiSuccessExample {json} Success
            HTTP/1.1 204 No Content
        """
        try:
            # line_item = OrderProduct.objects.get(pk=pk)
            customer = Customer.objects.get(user=request.auth.user)
            line_item = OrderProduct.objects.get(pk=pk, order__customer=customer)

            serializer = LineItemSerializer(line_item, context={"request": request})

            return Response(serializer.data)

        except OrderProduct.DoesNotExist as ex:
            return Response({"message": ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        """
        @api {DELETE} /lineitems/:id DELETE line item from cart
        @apiName RemoveLineItem
        @apiGroup ShoppingCart
        @apiParam {id} id Product Id to remove from cart
        @apiSuccessExample {json} Success
            HTTP/1.1 204 No Content
        @apiErrorExample {json} Product Not In Cart
            HTTP/1.1 404 Not Found
         {
                "detail": "Product not in cart."
            }
        """

    try:
        current_user = Customer.objects.get(user=request.auth.user)
        open_order = Order.objects.get(customer=current_user, payment_type=None)
        # Get the first (oldest) line item for this product
        line_item = OrderProduct.objects.filter(
            product__id=pk, order=open_order
        ).first()

        if line_item is None:
            return Response(
                {"detail": "Product not in cart."}, status=status.HTTP_404_NOT_FOUND
            )

        line_item.delete()
        return Response({}, status=status.HTTP_204_NO_CONTENT)

    except Order.DoesNotExist:
        return Response(
            {"detail": "No active cart found."}, status=status.HTTP_404_NOT_FOUND
        )
