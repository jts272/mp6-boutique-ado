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
            content=f"Unhandled webhook received: {event['type']}", status=200
        )

    # SPECIFIC EVENT HANDLING METHODS
    def handle_payment_intent_success(self, event):
        # Payment intent
        intent = event.data.object
        print(intent)
        return HttpResponse(
            content=f"Webhook received: {event['type']}", status=200
        )

    def handle_payment_intent_fail(self, event):
        return HttpResponse(
            content=f"PAYMENT FAILED Webhook received: {event['type']}",
            status=200,
        )
