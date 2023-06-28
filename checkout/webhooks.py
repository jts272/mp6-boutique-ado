import json

import stripe
from django.conf import settings
from django.http import HttpResponse

from django.views.decorators.http import require_POST

# Stripe won't send a CSRF token so we will need this
from django.views.decorators.csrf import csrf_exempt

# OUR WEBHOOK HANDLER
from checkout.webhook_handler import StripeWebHookHandler


@require_POST
@csrf_exempt
def webhook(request):
    """Listen for webhooks from Stripe.

    https://stripe.com/docs/webhooks

    https://youtu.be/HsOrCqVovmk

    Arguments:
        request -- HTTP request object
    """
    # SETUP
    wh_secret = settings.STRIPE_WH_SECRET
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Get webhook data and verify its signature
    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    event = None

    try:
        # event = stripe.Event.construct_from(
        #     json.loads(payload), stripe.api_key
        # )
        event = stripe.Webhook.construct_event(payload, sig_header, wh_secret)
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)
    # Generic exception handler
    except Exception as e:
        return HttpResponse(content=e, status=400)

    # print("Success!")
    # return HttpResponse(status=200)

    # Set up webhook handler
    handler = StripeWebHookHandler(request)

    # Map webhook events to appropriate handler functions
    event_map = {
        "payment_intent.succeeded": handler.handle_payment_intent_success,
        "payment_intent.payment_failed": handler.handle_payment_intent_fail,
    }

    # Get webhook type from Stripe
    # example return payment_intent.succeeded
    event_type = event["type"]

    # Lookup the key in the dictionary to assign the var
    # Optional generic handler default provided
    event_handler = event_map.get(event_type, handler.handle_event)

    # Call the event handler with the event
    response = event_handler(event)
    print(response.content)
    return response
