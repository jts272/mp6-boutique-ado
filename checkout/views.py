# import stripe from pip install
import stripe
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, render, reverse, get_object_or_404

# Custom context processor to allow calculating total for Stripe
from bag.contexts import bag_contents
from products.models import Product

from .forms import OrderForm

# Products and OLI required for success page/form handling
# Order required for checkout success view
from .models import Order, OrderLineItem


# Create your views here.
def checkout(request):
    # STRIPE VARS FROM SETTINGS
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    # STRIPE FORM SUBMISSION
    if request.method == "POST":
        # We need the shopping bag
        bag = request.session.get("bag", {})
        # Put form data into dictionary manually to skip save info box,
        # which doesn't have a field on the order model
        form_data = {
            "full_name": request.POST["full_name"],
            "email": request.POST["email"],
            "phone_number": request.POST["phone_number"],
            "country": request.POST["country"],
            "postcode": request.POST["postcode"],
            "town_or_city": request.POST["town_or_city"],
            "street_address1": request.POST["street_address1"],
            "street_address2": request.POST["street_address2"],
            "county": request.POST["county"],
        }
        order_form = OrderForm(form_data)
        if order_form.is_valid():
            order = order_form.save()
            # Iterate through bag items to create line items
            for item_id, item_data in bag.items():
                try:
                    product = Product.objects.get(id=item_id)
                    # For items without sizes
                    if isinstance(item_data, int):
                        order_line_item = OrderLineItem(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
                        order_line_item.save()
                    # Create line items for items with sizes
                    else:
                        for size, quantity in item_data[
                            "items_by_size"
                        ].items():
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=quantity,
                                product_size=size,
                            )
                            order_line_item.save()

                # Defensive approach if item not in database
                except Product.DoesNotExist:
                    messages.error(
                        request,
                        (
                            "One of the products in your bag wasn't found in our database. "
                            "Please call us for assistance!"
                        ),
                    )
                    order.delete()
                    return redirect(reverse("view_bag"))

            # Did user want to save their profile information to the session?
            request.session["save_info"] = "save-info" in request.POST
            # Send to success page with order number arg
            return redirect(
                reverse("checkout_success", args=[order.order_number])
            )

        # For invalid form
        else:
            messages.error(
                request,
                "There was an error with your form. \
                Please double check your information.",
            )

    if request.method == "GET":
        # Get bag from the session
        bag = request.session.get("bag", {})
        if not bag:
            messages.error(
                request, "There's nothing in your bag at the moment"
            )
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


def checkout_success(request, order_number):
    """
    Handle successful checkouts
    """
    # Required when we want to save user profiles
    save_info = request.session.get("save_info")
    # Get the order created from the order view
    order = get_object_or_404(Order, order_number=order_number)
    messages.success(
        request,
        f"Order successfully processed! \
        Your order number is {order_number}. A confirmation \
        email will be sent to {order.email}.",
    )

    # Bag no longer needed
    if "bag" in request.session:
        del request.session["bag"]

    template = "checkout/checkout_success.html"
    context = {
        "order": order,
    }

    return render(request, template, context)
