"""View module for handling reports"""

from django.shortcuts import render
from django.db.models import Sum, F, DecimalField
from django.db.models.functions import Coalesce
from bangazonapi.models import Order, OrderProduct
from datetime import datetime


def completed_orders_report(request):
    """
    View to display a report of all completed orders (paid orders).
    Accessed at /reports/orders?status=complete

    Shows:
    - Order ID
    - Customer name
    - Total paid for the order
    - Payment type (merchant name)
    """

    # Get the status parameter from the query string
    status_param = request.GET.get("status", None)

    # Filter for completed orders (completed_on is not null and not the default date)
    completed_orders = (
        Order.objects.filter(completed_on__isnull=False)
        .exclude(completed_on="0000-00-00")
        .select_related(
            "customer__user",  # Get the related User to access first/last name
            "payment_type",  # Get the Payment details
        )
        .prefetch_related(
            "orderproduct_set__product"  # Get all line items and their products
        )
    )

    # Calculate totals for each order
    orders_with_totals = []
    for order in completed_orders:
        # Calculate order total from line items
        order_total = 0
        line_items = order.orderproduct_set.all()

        for line_item in line_items:
            if line_item.product:
                order_total += line_item.product.price * line_item.quantity

        # Get customer name from the related User
        customer_name = (
            f"{order.customer.user.first_name} {order.customer.user.last_name}".strip()
        )

        # Get payment type merchant name
        payment_type = (
            order.payment_type.merchant_name if order.payment_type else "Not Specified"
        )

        orders_with_totals.append(
            {
                "id": order.id,
                "customer_name": customer_name,
                "total": order_total,
                "payment_type": payment_type,
                "completed_on": order.completed_on,
            }
        )

    context = {
        "orders": orders_with_totals,
        "status": status_param,
    }

    return render(request, "reports/completed_orders.html", context)
