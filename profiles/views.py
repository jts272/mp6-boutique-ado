from django.contrib import messages
from django.shortcuts import get_object_or_404, render

# For order history
from checkout.models import Order

from .forms import UserProfileForm
from .models import UserProfile


def profile(request):
    """Display the user's profile."""
    profile = get_object_or_404(UserProfile, user=request.user)

    # Populate form with current user's profile information
    form = UserProfileForm(instance=profile)

    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully")

    # Use related name on the order model to get order history
    orders = profile.orders.all()

    template = "profiles/profile.html"
    context = {
        # "profile": profile,
        "form": form,
        "orders": orders,
        # For profile update success message toasts
        "on_profile_page": True,
    }

    return render(request, template, context)


def order_history(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)

    messages.info(
        request,
        (
            f"This is a past confirmation for order number {order_number}. "
            "A confirmation email was sent on the order date."
        ),
    )

    # Re-use order success template
    template = "checkout/checkout_success.html"
    context = {
        "order": order,
        # If user got to the checkout_success template from the order_history view
        "from_profile": True,
    }

    return render(request, template, context)
