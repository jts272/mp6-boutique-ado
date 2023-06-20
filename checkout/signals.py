"""These signals are used to update the the order totals each time
a line item is attached to the order.

The module's `apps.py` must be updated to know about these signals.
"""

# Send these signals after ('post') the action
from django.db.models.signals import post_delete, post_save

# To receive signals
from django.dispatch import receiver

# The model we are listening to signals from
from .models import OrderLineItem


@receiver(post_save, sender=OrderLineItem)
def update_on_save(sender, instance, created, **kwargs):
    """Update order total on lineitem update/create.

    `post_save` signals are received from the OrderLineItem model in the
    function decorator. The function is called when the signal is sent.

    https://docs.djangoproject.com/en/3.2/ref/signals/#django.db.models.signals.post_save

    Arguments:
        sender -- the sender of the signal (OrderLineItem)
        instance -- the instance of the model that sent the signal
        created -- determine if this is a new instance or update (bool)
    """
    instance.order.update_total()


@receiver(post_delete, sender=OrderLineItem)
def update_on_delete(sender, instance, **kwargs):
    """Update order total on lineitem delete.

    Arguments:
        sender -- the sender of the signal (OrderLineItem)
        instance -- the instance of the model that sent the signal
    """
    instance.order.update_total()
