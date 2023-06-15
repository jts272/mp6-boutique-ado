from django import template

register = template.Library()


@register.filter(name="calc_subtotal")
def calc_subtotal(price, quantity):
    """Custom filter for displaying subtotal in bag."""
    return price * quantity
