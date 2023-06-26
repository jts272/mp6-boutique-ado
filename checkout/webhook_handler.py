from django.http import HttpResponse


class StripeWebHookHandler:
    """Handle Stripe webhooks."""

    def __init__(self, request):
        """Setup method each time an instance of this class is created.

        Arguments:
            request -- enable access to any request attrs coming from Stripe
        """
        self.request = request

    def handle_event(self, event):
        """Handle generic, unknown or unexpected webhook events.

        Arguments:
            event -- the event to handle

        Returns:
            HTTP response indicating Stripe event was received.
        """
        return HttpResponse(
            content=f"Webhook received: {event['type']}", status=200
        )
