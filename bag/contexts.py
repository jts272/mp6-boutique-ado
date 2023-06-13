from decimal import Decimal

from django.conf import settings
from django.shortcuts import get_object_or_404

from products.models import Product


def bag_contents(request):
    """A context processor for the contents of the shopping bag."""

    # Init vars
    bag_items = []
    total = 0
    product_count = 0
    # Get bag or init. Origin: `add_to_bag` in views.py
    bag = request.session.get("bag", {})

    # Iterate through k:v items in the shopping bag to display on site
    # This is the session bag
    for item_id, quantity in bag.items():
        # Get the product first for calculations and information
        product = get_object_or_404(Product, pk=item_id)
        # Total is the quantity of each product's price
        total += product.price * quantity
        # Increment the product count by the quantity
        product_count += quantity
        # Add dict to list of bag items for access in templates
        # This is like a context dict for the contents of the bag
        bag_items.append(
            {
                "item_id": item_id,
                "quantity": quantity,
                "product": product,
            }
        )

    # Incentivize customers to meet free shipping threshold
    if total < settings.FREE_DELIVERY_THRESHOLD:
        delivery = total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE / 100)
        free_delivery_delta = settings.FREE_DELIVERY_THRESHOLD - total
    else:
        delivery = 0
        free_delivery_delta = 0

    grand_total = delivery + total

    context = {
        "bag_items": bag_items,
        "total": total,
        "product_count": product_count,
        "delivery": delivery,
        "free_delivery_delta": free_delivery_delta,
        "free_delivery_threshold": settings.FREE_DELIVERY_THRESHOLD,
        "grand_total": grand_total,
    }
    return context
