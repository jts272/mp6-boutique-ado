# For unique order numbers
import uuid

from django.conf import settings
from django.db import models
from django.db.models import Sum

# For use as FK
from products.models import Product


# Create your models here.
class Order(models.Model):
    """Handles all orders across the store."""

    # Unique and permanent (not editable) value so users can find previous orders
    order_number = models.CharField(max_length=32, null=False, editable=False)
    full_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=False, blank=False)
    country = models.CharField(max_length=40, null=False, blank=False)
    # Not always required as not all countries have these
    postcode = models.CharField(max_length=20, null=True, blank=True)
    county = models.CharField(max_length=80, null=True, blank=True)
    town_or_city = models.CharField(max_length=40, null=False, blank=False)
    street_address1 = models.CharField(max_length=80, null=False, blank=False)
    street_address2 = models.CharField(max_length=80, null=True, blank=True)
    # Date automatically set
    date = models.DateTimeField(auto_now_add=True)
    # Last three calculated with model methods on save
    delivery_cost = models.DecimalField(
        max_digits=6, decimal_places=2, null=False, default=0
    )
    order_total = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, default=0
    )
    grand_total = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, default=0
    )


class OrderLineItem(models.Model):
    """An individual shopping bag item, relating to a specific order, which
    references the product, size, quantity and total cost for the line item.

    Usage: user checks out, info from the payment form is used to create
    an order instance. Iterate through the items in the shopping bag,
    creating an order line item for each one and attach it to the order.
    Delivery cost, order total and grand total are updated along the way.
    """

    # Access from Order model as `Order.lineitems.filter()` etc.
    order = models.ForeignKey(
        Order,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="lineitems",
    )
    # Give access to all associated fields of the product
    product = models.ForeignKey(
        Product, null=False, blank=False, on_delete=models.CASCADE
    )
    # Can be blank for products without size
    product_size = models.CharField(
        max_length=2, null=True, blank=True
    )  # XS, S, M, L, XL
    # Required and/or unique fields
    quantity = models.IntegerField(null=False, blank=False, default=0)
    # Automatically calculated on save
    lineitem_total = models.DecimalField(
        max_digits=6, decimal_places=2, null=False, blank=False, editable=False
    )
