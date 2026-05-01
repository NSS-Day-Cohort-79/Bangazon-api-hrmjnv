from django.shortcuts import render
from django.db.models import Sum, F, DecimalField, Count
from django.db.models.functions import Coalesce
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from bangazonapi.models import Order, OrderProduct, Product, ProductCategory
from datetime import datetime


class Reports(ViewSet):

    @action(methods=["get"], detail=False)
    def orders(self, request):
        """
        View to display a report of all completed orders (paid orders).
        Accessed at /reports/orders?status=complete

        Shows:
        - Order ID
        - Customer name
        - Total paid for the order
        - Payment type (merchant name)
        """

        # Get status parameter from query string
        status_param = request.GET.get("complete", "true")

        # Filter orders based on completion status
        if status_param.lower() == "true":
            orders = Order.objects.filter(completed_on__isnull=False).select_related(
                "customer__user", "payment_type"
            )
        elif status_param.lower() == "false":
            orders = Order.objects.filter(completed_on__isnull=True).select_related(
                "customer__user", "payment_type"
            )
        else:
            orders = Order.objects.filter(completed_on__isnull=False).select_related(
                "customer__user", "payment_type"
            )

        # Build order data with totals
        orders_with_totals = []
        for order in orders:
            customer_name = f"{order.customer.user.first_name} {order.customer.user.last_name}".strip()
            payment_type = (
                order.payment_type.merchant_name
                if order.payment_type
                else "Not Specified"
            )

            # Calculate order total
            line_items = OrderProduct.objects.filter(order=order).select_related(
                "product"
            )
            order_total = sum(item.product.price for item in line_items if item.product)

            orders_with_totals.append(
                {
                    "id": order.id,
                    "customer_name": customer_name,
                    "total": order_total,
                    "payment_type": payment_type,
                    "completed_on": order.completed_on,
                }
            )

        # Calculate total revenue and render
        total_revenue = sum(order["total"] for order in orders_with_totals)
        context = {
            "orders": orders_with_totals,
            "status": status_param,
            "total_revenue": total_revenue,
        }

        return render(request, "bangazonapi/completed_orders.html", context)

    @action(methods=["get"], detail=False)
    def expensiveproducts(self, request):
        """
        View to display products priced at $1000 or more.
        Accessed at /reports/expensiveproducts
        """

        # Get min_price from query string, default 1000
        min_price = float(request.GET.get("min_price", 1000))

        # Filter products >= min_price with related data
        products = Product.objects.filter(price__gte=min_price).select_related(
            "customer__user", "category"
        )

        # Prepare data for template
        context = {
            "products": products,
            "min_price": min_price,
            "report_type": "Expensive",
        }

        return render(request, "bangazonapi/products_report.html", context)

    @action(methods=["get"], detail=False)
    def inexpensiveproducts(self, request):
        """
        View to display products priced under $1000.
        Accessed at /reports/inexpensiveproducts
        """

        # Get max_price from query string, default 1000
        max_price = float(request.GET.get("max_price", 1000))

        # Filter products < max_price with related data
        products = Product.objects.filter(price__lt=max_price).select_related(
            "customer__user", "category"
        )

        # Prepare data for template
        context = {
            "products": products,
            "max_price": max_price,
            "report_type": "Inexpensive",
        }

        return render(request, "bangazonapi/products_report.html", context)
