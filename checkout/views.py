# import stripe from pip install
import stripe
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, render, reverse

# Custom context processor to allow calculating total for Stripe
from bag.contexts import bag_contents

from .forms import OrderForm


# Create your views here.
def checkout(request):
    # STRIPE VARS FROM SETTINGS
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    # Get bag from the session
    bag = request.session.get("bag", {})
    if not bag:
        messages.error(request, "There's nothing in your bag at the moment")
        # Redirect "/checkout" url path
        return redirect(reverse("products"))

    # bag_contents Stripe vars
    current_bag = bag_contents(request)
    total = current_bag["grand_total"]
    # Stripe requires total as integer
    stripe_total = round(total * 100)
    # Set secret key on Stripe
    stripe.api_key = stripe_secret_key
    # Create payment intent with amount and currency
    intent = stripe.PaymentIntent.create(
        amount=stripe_total, currency=settings.STRIPE_CURRENCY
    )

    # Stripe dict with lots of keys about payment information
    print(intent)

    # Warn of missing public key
    if not stripe_public_key:
        messages.warning(
            request,
            "Stripe public key is missing. \
            Did you forget to set it in your environment?",
        )

    order_form = OrderForm()
    template = "checkout/checkout.html"
    context = {
        "order_form": order_form,
        # "stripe_public_key": "pk_test_51NMu8PEPb8OObKzZJEtyxn1AEAmJVbitHxGiYBMIOoVDEHgedK0qnuQexEHWPB3kbmS5C66CWj9uNtQCQRdTq9Px00oxNbOOdG",
        "stripe_public_key": stripe_public_key,
        # "client_secret": "test client secret",
        "client_secret": intent.client_secret,
    }

    return render(request, template, context)
