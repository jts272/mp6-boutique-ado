from django.shortcuts import render, redirect, reverse
from django.contrib import messages

from .forms import OrderForm


# Create your views here.
def checkout(request):
    # Get bag from the session
    bag = request.session.get("bag", {})
    if not bag:
        messages.error(request, "There's nothing in your bag at the moment")
        # Redirect "/checkout" url path
        return redirect(reverse("products"))

    order_form = OrderForm()
    template = "checkout/checkout.html"
    context = {
        "order_form": order_form,
        "stripe_public_key": "pk_test_51NMu8PEPb8OObKzZJEtyxn1AEAmJVbitHxGiYBMIOoVDEHgedK0qnuQexEHWPB3kbmS5C66CWj9uNtQCQRdTq9Px00oxNbOOdG",
        "client_secret": "test client secret",
    }

    return render(request, template, context)
