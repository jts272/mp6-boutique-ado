import json

# import stripe from pip install
import stripe
from django.conf import settings
from django.contrib import messages
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
    reverse,
    HttpResponse,
)
from django.views.decorators.http import require_POST

# Custom context processor to allow calculating total for Stripe
from bag.contexts import bag_contents
from products.models import Product

from .forms import OrderForm

# Products and OLI required for success page/form handling
# Order required for checkout success view
from .models import Order, OrderLineItem

# Used in saving info
from profiles.forms import UserProfileForm
from profiles.models import UserProfile


# Create your views here.
@require_POST
def cache_checkout_data(request):
    """Handle checkbox to save payment data.

    Before calling confirm card payment method in Stripe JS, a post
    request is made to this view and is given the client secret from the
    payment intent.

    https://youtu.be/h0_abBkUPAw

    Arguments:
        request -- HTTP request object
    """
    # T/E block shows errors if applicable
    # This view is designed to be posted by JS
    try:
        payment_intent_id = request.POST.get("client_secret").split("_secret")[
            0
        ]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        # Modify the payment intent
        stripe.PaymentIntent.modify(
            payment_intent_id,
            metadata={
                # Contents of shopping bag
                "bag": json.dumps(request.session.get("bag", {})),
                # bool for whether to save info
                "save_info": request.POST.get("save_info"),
                # User placing the order
                "username": request.user,
            },
        )
        return HttpResponse(status=200)

    except Exception as e:
        messages.error(
            request,
            "Sorry, your payment cannot be processed right now. \
            Please try again later.",
        )
        return HttpResponse(content=e, status=400)


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
            # PREVENT FIRST SAVE AS SUBSEQUENT CHECKS ARE MADE BELOW
            order = order_form.save(commit=False)

            # PAYMENT INTENT ID FOR DUPLICATE BAG ORDER LOGIC
            pid = request.POST.get("client_secret").split("_secret")[0]
            order.stripe_pid = pid
            # UPDATE MODEL FIELD FOR ORIGINAL BAG FOR THE ORDER
            order.original_bag = json.dumps(bag)
            order.save()

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

        # Attempt to prefill the form with any info the user maintains in their profile
        if request.user.is_authenticated:
            try:
                profile = UserProfile.objects.get(user=request.user)
                order_form = OrderForm(
                    initial={
                        "full_name": profile.user.get_full_name(),
                        "email": profile.user.email,
                        "phone_number": profile.default_phone_number,
                        "country": profile.default_country,
                        "postcode": profile.default_postcode,
                        "town_or_city": profile.default_town_or_city,
                        "street_address1": profile.default_street_address1,
                        "street_address2": profile.default_street_address2,
                        "county": profile.default_county,
                    }
                )
            except UserProfile.DoesNotExist:
                order_form = OrderForm()
        else:
            order_form = OrderForm()

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

    # IF STATEMENT ALLOWS ANONYMOUS CHECKOUT WITHOUT BREAKING
    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user=request.user)
        # Attach the user's profile to the order
        order.user_profile = profile
        order.save()

        # Save the user's info
        if save_info:
            profile_data = {
                "default_phone_number": order.phone_number,
                "default_country": order.country,
                "default_postcode": order.postcode,
                "default_town_or_city": order.town_or_city,
                "default_street_address1": order.street_address1,
                "default_street_address2": order.street_address2,
                "default_county": order.county,
            }
            user_profile_form = UserProfileForm(profile_data, instance=profile)
            if user_profile_form.is_valid():
                user_profile_form.save()

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
