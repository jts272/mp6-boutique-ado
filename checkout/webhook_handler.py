import json
import time

import stripe
from django.http import HttpResponse

# Handle checkbox profile save
from profiles.models import UserProfile

from .models import Order, OrderLineItem, Product

# SEND CONFIRMATION EMAIL IMPORTS
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


class StripeWebHookHandler:
    """Handle Stripe webhooks."""

    def __init__(self, request):
        """Setup method each time an instance of this class is created.

        Arguments:
            request -- enable access to any request attrs coming from Stripe
        """
        self.request = request

    # PRIVATE METHOD (only used in this class)
    def _send_confirmation_email(self, order):
        """Send the user a confirmation email"""
        cust_email = order.email
        # Template and context provided for render_to_string method
        subject = render_to_string(
            "checkout/confirmation_emails/confirmation_email_subject.txt",
            {"order": order},
        )
        body = render_to_string(
            "checkout/confirmation_emails/confirmation_email_body.txt",
            {"order": order, "contact_email": settings.DEFAULT_FROM_EMAIL},
        )

        # Method to actually send the email
        # Subject, Body, From, To
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [cust_email])

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
        # Payment intent - all customer information held here
        intent = event.data.object
        # CREATE ORDER JUST LIKE FORM, FOR INSTANCES OF MALFUNCTIONAL SUBMISSION
        # Payment intent id
        pid = intent.id
        bag = intent.metadata.bag
        # For checkbox
        save_info = intent.metadata.save_info

        # UPDATE https://learn.codeinstitute.net/courses/course-v1:CodeInstitute+EA101+2021_T1/courseware/eb05f06e62c64ac89823cc956fcd8191/48ac02aa8ecc4079be016c336231bee7/?child=first
        # Get the Charge object
        stripe_charge = stripe.Charge.retrieve(intent.latest_charge)

        # billing_details = intent.charges.data[0].billing_details
        billing_details = stripe_charge.billing_details  # updated
        shipping_details = intent.shipping
        # grand_total = round(intent.data.charges[0].amount / 100, 2)
        grand_total = round(stripe_charge.amount / 100, 2)  # updated

        # Store empty string values as 'None' for our database (clean)
        for field, value in shipping_details.address.items():
            if value == "":
                shipping_details.address[field] = None

        # Update profile information if save_info was checked
        # ALLOW ANONYMOUS USERS TO CHECK OUT
        profile = None
        username = intent.metadata.username
        if username != "AnonymousUser":
            # They must be authenticated
            profile = UserProfile.objects.get(user__username=username)
            # If checkbox clicked
            if save_info:
                profile.default_phone_number = shipping_details.phone
                profile.default_country = shipping_details.address.country
                profile.default_postcode = shipping_details.address.postal_code
                profile.default_town_or_city = shipping_details.address.city
                profile.default_street_address1 = (
                    shipping_details.address.line1
                )
                profile.default_street_address2 = (
                    shipping_details.address.line2
                )
                profile.default_county = shipping_details.address.state
                profile.save()

        # For proper form submission when the user checks out, the form
        # should already be in the db
        # Presence check and return an ok response if it is there

        # First, assume the order doesn't exist
        order_exists = False

        # CREATE DELAY INSTEAD OF IMMEDIATE CREATION WHEN RECORD NOT FOUND
        attempt = 1
        while attempt < 5:
            try:
                order = Order.objects.get(
                    full_name__iexact=shipping_details.name,
                    email__iexact=shipping_details.email,
                    phone_number__iexact=shipping_details.phone,
                    country__iexact=shipping_details.country,
                    postcode__iexact=shipping_details.postal_code,
                    town_or_city__iexact=shipping_details.city,
                    street_address1__iexact=shipping_details.line1,
                    street_address2__iexact=shipping_details.line2,
                    county__iexact=shipping_details.state,
                    grand_total=grand_total,
                    # ADDITIONAL CHECKS AFTER DUPLICATE BAG LOGIC IMPLEMENTED
                    original_bag=bag,
                    stripe_pid=pid,
                )
                order_exists = True
                # BREAK WHILE LOOP IF ORDER FOUND
                break

            except Order.DoesNotExist:
                # DELAY LOGIC
                attempt += 1
                # SLEEP FOR ONE SECOND
                time.sleep(1)

        if order_exists:
            # SEND CONFIRMATION EMAIL HERE BEFORE RETURNING RESPONSE TO STRIPE
            self._send_confirmation_email(order)
            return HttpResponse(
                content=f"Webhook received: {event['type']} | SUCCESS: Verified order already in database",
                status=200,
            )

        else:
            order = None
            try:
                # Create if it does not exist, using code from checkout view
                order = Order.objects.create(
                    full_name=shipping_details.name,
                    # WE GOT THE PROFILE ALREADY ABOVE
                    # LET WH CREATE ORDERS FOR AUTH AND ANON USERS
                    # e.g. PROFILE DATA OR 'NONE'
                    user_profile=profile,
                    email=shipping_details.email,
                    phone_number=shipping_details.phone,
                    country=shipping_details.country,
                    postcode=shipping_details.postal_code,
                    town_or_city=shipping_details.city,
                    street_address1=shipping_details.line1,
                    street_address2=shipping_details.line2,
                    county=shipping_details.state,
                    # INCLUDE FIELDS TO CREATE SPECIFIC ORDER
                    original_bag=bag,
                    stripe_pid=pid,
                )
                # Iterate through bag items to create line items
                # LOAD BAG FROM JSON VERSION OF PAYMENTINTENT, NOT SESSION
                for item_id, item_data in json.loads(bag).items():
                    # WE DON'T HAVE A FORM TO SAVE IN THIS WEBHOOK TO CREATE THE ORDER
                    # CREATE IT HERE USING DATA FROM THE PAYMENTINTENT (WHICH CAME FROM THE FORM)
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

            except Exception as e:
                # IF ANYTHING GOES WRONG, DELETE THE ORDER IF IT WAS CREATED
                # 500 error causes Stripe to automatically try the webhook
                # again later
                if order:
                    order.delete()
                return HttpResponse(
                    content=f"Webhook received: {event['type']} | ERROR: {e}",
                    status=500,
                )

        print(intent)

        # SEND CONFIRMATION EMAIL IF ORDER CREATED BY WEBHOOK HANDLER
        self._send_confirmation_email(order)

        # ORDER MUST HAVE BEEN CREATED AT THIS POINT - SHOW SUCCESS
        return HttpResponse(
            content=f"Webhook received: {event['type']} | SUCCESS: Created order in webhook",
            status=200,
        )

    def handle_payment_intent_fail(self, event):
        return HttpResponse(
            content=f"PAYMENT FAILED Webhook received: {event['type']}",
            status=200,
        )
